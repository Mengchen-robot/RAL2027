import numpy as np
rng=np.random.default_rng(5)
def se_beta(n_fam=5,stg=8,n_trial=20,pi_d=0.30,sig_stage_pp=4.0,within_frac=0.9):
    n=n_fam*stg
    se_trial=100*np.sqrt(pi_d/n_trial)                 # sd of one paired Delta_k, pp
    sig=np.sqrt(sig_stage_pp**2+se_trial**2)
    dof=n-n_fam-1
    return sig/np.sqrt(n*within_frac), dof, se_trial
def mde(**kw):                                          # 80% power, two-sided 5%
    s,dof,st=se_beta(**kw); return 2.80*s, st
print("Per-stage covariate slope beta, units = pp of paired Delta per 1 SD of covariate.")
print("Within-family fixed-effects OLS; family effects absorbed, so n = number of STAGES.\n")
print(f"{'design':52s} {'trial-noise sd':>14s} {'SE(beta)':>9s} {'MDE@80%':>8s}")
cfgs=[("5 fam x 8 stages, 20 paired trials, pi_d=.30",dict()),
      ("5 fam x 8 stages, 40 paired trials",dict(n_trial=40)),
      ("5 fam x 8 stages, 20 trials, pi_d=.50",dict(pi_d=.5)),
      ("5 fam x 12 stages (n=60), 20 trials",dict(stg=12)),
      ("5 fam x 4 stages (n=20), 20 trials",dict(stg=4)),
      ("8 fam x 5 stages (n=40), 20 trials",dict(n_fam=8,stg=5)),
      ("as row 1 but covariate only 50% within-family",dict(within_frac=.5)),
      ("as row 1 but covariate only 10% within-family",dict(within_frac=.1)),
      ("continuous stage score, trial noise halved",dict(pi_d=.075)),
      ("continuous score + 40 trials + 12 stages/fam",dict(pi_d=.075,n_trial=40,stg=12))]
for lbl,kw in cfgs:
    m,st=mde(**kw); s,_,_=se_beta(**kw)
    print(f"{lbl:52s} {st:14.1f} {s:9.2f} {m:8.1f}")
# validate the analytic SE against a small simulation
def sim(beta,n_fam=5,stg=8,n_trial=20,pi_d=.3,tau=6.,sig=4.,wf=.9,reps=4000):
    n=n_fam*stg; fam=np.repeat(np.arange(n_fam),stg); st=100*np.sqrt(pi_d/n_trial); B=[]
    Xf=np.eye(n_fam)[fam]
    for _ in range(reps):
        z=np.sqrt(1-wf)*rng.normal(0,1,n_fam)[fam]+np.sqrt(wf)*rng.normal(0,1,n)
        d=beta*z+tau*rng.normal(0,1,n_fam)[fam]+sig*rng.normal(0,1,n)+st*rng.normal(0,1,n)
        X=np.column_stack([Xf,z]); b,_,_,_=np.linalg.lstsq(X,d,rcond=None); B.append(b[-1])
    return np.mean(B),np.std(B)
m,s=sim(4.0); a,_,_=se_beta()
print(f"\nvalidation: simulated  beta_hat = {m:.2f} (true 4.00), empirical SE = {s:.2f}  vs analytic SE = {a:.2f}")
print("\nkey economics: one paired EPISODE yields one observation for EVERY stage of that task,")
print("so n_stage grows at zero additional robot-hours; only the per-stage readout must exist.")

import numpy as np, itertools
np.set_printoptions(precision=3, suppress=True)

# ---------- 1. zeta prototypes (from absorb2.py, layer-4 residual 7.10cm/17.8deg) ----------
Z = dict(hinge=0.3, transport=1.5, pick=8.7, place=12.2, zip=13.7, insert=31.1)

# ---------- 2. stage tables (confirmatory = rigid families) ----------
# (stage_id, prototype, d_free, is_confirmatory)
fam = {}
fam['C'] = [('C1','pick',6),('C2','hinge',1),('C3','transport',6),('C4','pick',5),
            ('C5','transport',6),('C6','place',4),('C7','transport',6),('C8','hinge',1),('C9','insert',3)]
fam['B'] = [('B1','transport',5),('B2','pick',6),('B3','zip',1),('B4','place',4),
            ('B5','pick',6),('B6','zip',1)]
fam['D'] = [('D1','pick',6),('D2','hinge',1),('D3','transport',6),('D4','pick',5),
            ('D5','place',4),('D6','transport',6),('D7','hinge',1)]      # drawer: prismatic 1-DoF
fam['E'] = [('E1','pick',6),('E2','hinge',1),('E3','transport',6),('E4','pick',5),
            ('E5','place',4),('E6','transport',6),('E7','hinge',1)]      # cabinet door
fam['A'] = [('A1','transport',6),('A2','pick',4),('A3','transport',6),('A4','place',4),
            ('A5','place',4),('A6','pick',5),('A7','transport',6),('A8','place',4)]  # cloth: exploratory

conf = ['C','B','D','E']
print("=== stage counts ===")
for f in fam: print(f, len(fam[f]), 'confirmatory' if f in conf else 'EXPLORATORY')
n_conf = sum(len(fam[f]) for f in conf)
print("confirmatory stages n =", n_conf, "| + exploratory cloth", len(fam['A']), "=> total", n_conf+len(fam['A']))

# ---------- 3. within- vs between-family variance of log zeta ----------
def var_decomp(fams, key):
    rows=[]
    for f in fams:
        for sid,proto,df in fam[f]:
            v = np.log(Z[proto]) if key=='logzeta' else (6-df)
            rows.append((f, v))
    fs = np.array([r[0] for r in rows]); vs = np.array([r[1] for r in rows], float)
    gm = vs.mean(); tot = ((vs-gm)**2).sum()
    within = 0.0
    for f in set(fs):
        x = vs[fs==f]; within += ((x-x.mean())**2).sum()
    between = tot - within
    return within/tot, between/tot, vs.std(ddof=1)

for key in ['logzeta','absorb']:
    w,b,sd = var_decomp(conf, key)
    print(f"[{key}] confirmatory: within-family share={w:.3f} between={b:.3f} sd={sd:.3f}")
    w2,b2,sd2 = var_decomp(conf+['A'], key)
    print(f"[{key}] +cloth      : within-family share={w2:.3f} between={b2:.3f} sd={sd2:.3f}")

# ---------- 4. robot-hours ----------
# per-rollout minutes for COMPOSITIONAL tasks (exec + reset), derived from v5 6.6 atomic numbers
mins = dict(C=1.9, B=4.25, D=1.75, E=2.5, A=5.9)
FF = 1.4
def hrs(rollouts_per_fam, families, ff=FF):
    m = sum(rollouts_per_fam[f]*mins[f] for f in families)
    return m/60*ff

Npair = 20
main = {f: 2*Npair*2 for f in conf+['A']}          # 2 dir x Npair pairs x {base,ours}
h_main = hrs(main, conf+['A'])
print(f"\n[main endpoint] {sum(main.values())} rollouts -> {h_main:.1f} h  (Npair={Npair})")
h_main_conf_only = hrs(main, conf)
print(f"   of which rigid confirmatory only: {h_main_conf_only:.1f} h ; cloth exploratory: {h_main-h_main_conf_only:.1f} h")

# stage-targeted injection (causal identification): scripted stage-k start, truncated rollout
tgt_stages = 8; tgt_pairs = 20
h_tgt = tgt_stages*tgt_pairs*2*1.0/60*FF     # ~1.0 min truncated rollout incl reset
print(f"[stage-targeted injection] {tgt_stages} stages x {tgt_pairs} pairs x2 = {tgt_stages*tgt_pairs*2} rollouts -> {h_tgt:.1f} h")

# level sweep: levels 1 and 4 extra (3 already = main), 1 direction, 15 trials
sweep = {f: 2*15 for f in conf}
h_sweep = hrs(sweep, conf)
print(f"[level sweep 1+4, P->X only] {sum(sweep.values())} rollouts -> {h_sweep:.1f} h")

# A/A control + pi_d pilot, per-stage noise floor: 1 cloth + 1 rigid
aa = {'A':2*20, 'C':2*20}
h_aa = hrs(aa, ['A','C'])
print(f"[A/A + pi_d pilot] -> {h_aa:.1f} h")

# control arms A1-A7 (A8 software), 15 trials, on B+C+D subset
ctrl = {f: 7*15 for f in ['B','C','D']}
h_ctrl = hrs(ctrl, ['B','C','D'])
print(f"[7 control arms]  -> {h_ctrl:.1f} h")

rts  = {f: 2*15 for f in ['B','C','D']}; h_rts = hrs(rts, ['B','C','D'])
d6   = {f: 2*15 for f in ['B','C','D']}; h_d6  = hrs(d6, ['B','C','D'])
print(f"[R-t-S same-body x2] -> {h_rts:.1f} h   [D6 single-arm reader] -> {h_d6:.1f} h")

h_g05 = 2.3; h_e5 = 4.2; h_er = 4.8
h_eval = h_main+h_tgt+h_sweep+h_aa+h_ctrl+h_rts+h_d6+h_g05+h_e5+h_er
print(f"\n[G0.5]{h_g05} [E5]{h_e5} [ER]{h_er}")
print(f"EVAL SUBTOTAL = {h_eval:.1f} h")

# D12 collection: 5 families x 30 ep x 2 bodies x1.2 retake, teleop 1.5x exec
tele = {f: 30*2*1.2 for f in conf+['A']}
h_d12 = sum(tele[f]*mins[f]*1.5 for f in conf+['A'])/60
print(f"D12 collection = {h_d12:.1f} h  ({int(sum(tele.values()))} episodes)")
print(f"TOTAL = {h_eval+h_d12:.1f} robot-hours   (v5 baseline 150)")

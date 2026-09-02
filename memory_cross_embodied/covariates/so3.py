import numpy as np
rng=np.random.default_rng(0)

def hat(w): return np.array([[0,-w[2],w[1]],[w[2],0,-w[0]],[-w[1],w[0],0]])
def vee(W): return np.array([W[2,1],W[0,2],W[1,0]])
def expm_so3(w):
    th=np.linalg.norm(w)
    if th<1e-12: return np.eye(3)+hat(w)
    K=hat(w/th); return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K
def logm_so3(R):
    c=(np.trace(R)-1)/2; c=np.clip(c,-1,1); th=np.arccos(c)
    if th<1e-9: return vee(R-R.T)/2
    if abs(th-np.pi)<1e-6:
        A=(R+np.eye(3))/2
        i=int(np.argmax(np.diag(A))); v=A[:,i]/np.sqrt(max(A[i,i],1e-12))
        return th*v/np.linalg.norm(v)
    return th/(2*np.sin(th))*vee(R-R.T)

def karcher(Rs,iters=100,tol=1e-12):
    M=Rs[0].copy()
    for _ in range(iters):
        d=np.mean([logm_so3(M.T@R) for R in Rs],axis=0)
        M=M@expm_so3(d)
        if np.linalg.norm(d)<tol: break
    return M

def projected_mean(Rs):                      # Moakher 2002 projected (Euclidean) mean
    A=np.mean(Rs,axis=0); U,S,Vt=np.linalg.svd(A); D=np.diag([1,1,np.sign(np.linalg.det(U@Vt))])
    return U@D@Vt

def dispersion(Rs, sym=None):
    """sym: list of rotation matrices generating the gripper symmetry group (incl. I)."""
    if sym is None: sym=[np.eye(3)]
    M=karcher(Rs)
    for _ in range(30):                       # symmetry-quotient Karcher: re-align each sample
        Rs_al=[]
        for R in Rs:
            best=None;bd=1e9
            for S in sym:
                Rc=R@S; d=np.linalg.norm(logm_so3(M.T@Rc))
                if d<bd: bd=d;best=Rc
            Rs_al.append(best)
        Mn=karcher(Rs_al)
        if np.linalg.norm(logm_so3(M.T@Mn))<1e-10: M=Mn; break
        M=Mn
    xi=np.array([logm_so3(M.T@R) for R in Rs_al])
    var_geo=float(np.mean(np.sum(xi**2,axis=1)))        # rad^2 (Frechet variance)
    Sig=xi.T@xi/len(xi)                                  # rad^2 tangent covariance
    ev,evec=np.linalg.eigh(Sig)
    Abar=np.mean(Rs_al,axis=0); sv=np.linalg.svd(Abar,compute_uv=False)
    return dict(M=M,var_geo=var_geo,Sigma=Sig,eig=ev[::-1],evec=evec[:,::-1],
                sv_mean=sv, Rbar=float(np.linalg.norm(Abar,'fro')/np.sqrt(3)))

def naive_quat(Rs, align=True):
    def q(R):
        w=np.sqrt(max(0,1+np.trace(R)))/2
        if w<1e-6:
            # fallback
            e,v=np.linalg.eigh(R+R.T); pass
        x=(R[2,1]-R[1,2])/(4*w); y=(R[0,2]-R[2,0])/(4*w); z=(R[1,0]-R[0,1])/(4*w)
        return np.array([w,x,y,z])
    Q=np.array([q(R) for R in Rs])
    if align:
        for i in range(1,len(Q)):
            if Q[i]@Q[0]<0: Q[i]=-Q[i]
    return np.linalg.eigvalsh(np.cov(Q.T))[::-1]

def euler_var(Rs):
    E=[]
    for R in Rs:
        E.append([np.arctan2(R[2,1],R[2,2]),-np.arcsin(np.clip(R[2,0],-1,1)),np.arctan2(R[1,0],R[0,0])])
    return np.var(np.array(E),axis=0)

def sample(mean_R, sig_deg, n=200):
    s=np.deg2rad(np.array(sig_deg))
    return [mean_R@expm_so3(rng.normal(0,1,3)*s) for _ in range(n)]

D=np.rad2deg
print("case                         geo_sd(deg)  tangent_sd(deg)          quat_align_sd  quat_noalign_sd  euler_sd(deg)")
cases={
 "A iso 5deg":              (np.eye(3),[5,5,5]),
 "B pick: free roll 40deg": (np.eye(3),[3,3,40]),
 "C wide iso 60deg":        (np.eye(3),[60,60,60]),
}
for k,(M0,s) in cases.items():
    Rs=sample(M0,s)
    r=dispersion(Rs)
    qa=np.sqrt(naive_quat(Rs,True)); qn=np.sqrt(naive_quat(Rs,False))
    ev=np.sqrt(np.maximum(r['eig'],0))
    print(f"{k:28s} {D(np.sqrt(r['var_geo'])):8.2f}   {np.array2string(D(ev),precision=1):22s} {np.array2string(qa,precision=3):17s} {np.array2string(qn,precision=3):17s} {np.array2string(D(np.sqrt(euler_var(Rs))),precision=1)}")

# --- gripper 180deg symmetry ---
print()
Sym=[np.eye(3),expm_so3(np.array([0,0,np.pi]))]
Rs=[]
for i in range(200):
    R=expm_so3(rng.normal(0,1,3)*np.deg2rad([3,3,3]))
    if i%2: R=R@Sym[1]                    # physically identical grasp for a parallel jaw
    Rs.append(R)
r_no=dispersion(Rs); r_sym=dispersion(Rs,sym=Sym)
print("parallel-jaw 180deg flip, true spread 3 deg:")
print(f"  no symmetry quotient : geodesic sd = {D(np.sqrt(r_no['var_geo'])):.1f} deg, eig sd = {np.array2string(D(np.sqrt(np.maximum(r_no['eig'],0))),precision=1)}")
print(f"  with symmetry quotient: geodesic sd = {D(np.sqrt(r_sym['var_geo'])):.1f} deg, eig sd = {np.array2string(D(np.sqrt(np.maximum(r_sym['eig'],0))),precision=1)}")

# --- Karcher vs projected mean ---
for k,(M0,s) in cases.items():
    Rs=sample(M0,s); Mk=karcher(Rs); Mp=projected_mean(Rs)
    print(f"{k:28s} Karcher-vs-projected mean gap = {D(np.linalg.norm(logm_so3(Mk.T@Mp))):.3f} deg")

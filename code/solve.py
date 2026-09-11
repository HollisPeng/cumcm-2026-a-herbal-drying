"""Axisymmetric drying model. Run from any directory; outputs ../results.
Python 3.12, numpy, scipy, openpyxl (read only), matplotlib.
No random numbers are used. Temperatures in deg C except inside Arrhenius law.
"""
from pathlib import Path
import argparse, json, time
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags, bmat
from scipy.special import expi

ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT / 'data', ROOT / 'results'

class Drying:
    def __init__(self, mode, n=800, tail=(50., .05), hm=8e-7,
                 h=25., diffusion_scale=1., shrink=None):
        self.mode, self.n = mode, n
        self.tail, self.hm, self.h = tail, hm, h
        self.scale = diffusion_scale
        self.shrink = mode == 4 if shrink is None else shrink
        self.air = np.loadtxt(DATA / 'air.csv', delimiter=',', skiprows=1)
        self.rad = np.loadtxt(DATA / 'radius.csv', delimiter=',', skiprows=1)
        self.x = 1-(1-np.linspace(0., 1., n+1))**1.5
        self.dx = np.diff(self.x)
        self.faces = np.r_[0., (self.x[:-1]+self.x[1:])/2, 1.]
        self.vol = np.diff(self.faces**2)/2
        a = diags([np.ones(n), np.ones(n+1), np.ones(n)], [-1,0,1])
        self.pattern = bmat([[a,a],[a,a]], format='csc')

    def radius(self, t):
        return np.interp(t, self.rad[:,0], self.rad[:,1])/100 if self.shrink else .02

    def ambient(self, t):
        if t > self.air[-1,0]:
            return self.tail
        return tuple(np.interp(t,self.air[:,0],self.air[:,j]) for j in (1,2))

    def properties(self, T, C):
        c = np.maximum(C, 1e-10)
        if self.mode == 1:
            rho, cp, k = 820., 2600., np.full_like(c,.36)
            D = 7e-9*np.exp(-.89/c)
        elif self.mode == 2:
            rho, cp, k = 650+128*c, 1450+2736*c/(1+c), .21+.38*c/(1+c)
            D = 2.4e-3*np.exp(-.45/c-3850/(T+273.15))
        else:
            rho, cp, k = 760+90*c, 1850+2150*c/(1+c), .12+.20*c/(1+c)
            D = 4.2e-4*np.exp(-.30/c-3850/(T+273.15))
        return rho*cp, k, D*self.scale

    def diffusion(self, z, coeff, transfer, ambient, R):
        face_coeff = 2*coeff[:-1]*coeff[1:]/(coeff[:-1]+coeff[1:])
        flux = np.empty(self.n+2)
        flux[0] = 0.
        flux[1:-1] = self.faces[1:-1]*face_coeff*np.diff(z)/self.dx/R**2
        flux[-1] = -transfer*(z[-1]-ambient)/R
        return np.diff(flux)/self.vol

    def rhs(self, t, y):
        m = self.n+1
        T, C = y[:m], y[m:]
        Ta, Ca = self.ambient(t)
        R = self.radius(t)
        capacity,k,D = self.properties(T,C)
        # Kirchhoff integrated moisture flux avoids harmonic-mean bias in the
        # very dry surface layer. Integral exp(-a/C)dC = C exp(-a/C)+a Ei(-a/C).
        a = {1:.89,2:.45,4:.30}[self.mode]
        c = np.maximum(C,1e-10)
        potential = c*np.exp(-a/c)+a*expi(-a/c)
        delta = np.diff(C)
        q = np.diff(potential)
        close = abs(delta)<1e-6*np.maximum(c[:-1],c[1:])
        q[close] = np.exp(-a/((c[:-1]+c[1:])/2))[close]*delta[close]
        if self.mode==1: prefactor=7e-9
        else:
            prefactor=({2:2.4e-3,4:4.2e-4}[self.mode]
                       *np.exp(-3850/((T[:-1]+T[1:])/2+273.15)))
        flux = np.r_[0.,self.faces[1:-1]*prefactor*self.scale*q/self.dx/R**2,
                     -self.hm*(C[-1]-Ca)/R]
        return np.r_[self.diffusion(T,k,self.h,Ta,R)/capacity,
                     np.diff(flux)/self.vol]

    def run(self, until=None, rtol=2e-8, atol=2e-10):
        end = until if until is not None else 14*86400.
        y = np.r_[np.full(self.n+1,28.),np.full(self.n+1,2.55)]
        def event(t,z): return np.max(z[self.n+1:])-.15
        event.direction, event.terminal = -1, until is None
        self.parts = []
        for a,b,step in [(0.,min(end,14400.),20.),(14400.,end,180.)]:
            if b <= a: continue
            sol = solve_ivp(self.rhs,(a,b),y,method='BDF',rtol=rtol,
                            atol=atol,max_step=step,dense_output=True,
                            jac_sparsity=self.pattern,events=event)
            if not sol.success: raise RuntimeError(sol.message)
            self.parts.append(sol)
            if len(sol.t_events[0]) and until is None:
                self.crossing = float(sol.t_events[0][0])
                break
            y = sol.y[:,-1]
        if until is None:
            roots = [t for p in self.parts for t in p.t_events[0]]
            if not roots: raise RuntimeError('No drying threshold reached')
            self.crossing = float(roots[0])
            self.stop = int(np.floor(self.crossing))+1
            extra = solve_ivp(self.rhs,(self.crossing,self.stop),self.parts[-1].y[:,-1],
                              method='BDF',rtol=rtol,atol=atol,max_step=1.,
                              jac_sparsity=self.pattern,dense_output=True)
            if not extra.success: raise RuntimeError(extra.message)
            self.parts.append(extra)
        else:
            self.crossing, self.stop = None, float(until)
        return self

    def evaluate(self,t):
        t = np.atleast_1d(t).astype(float)
        y = np.empty((2*(self.n+1),len(t)))
        for j,p in enumerate(self.parts):
            mask = (t>=p.t[0]) & (t<=p.t[-1])
            if np.any(mask): y[:,mask] = p.sol(t[mask])
        return y

    def sample(self,t,distances_cm):
        t = np.atleast_1d(t).astype(float)
        y = self.evaluate(t)
        m=self.n+1
        T,C = [],[]
        for j,s in enumerate(t):
            q=np.asarray(distances_cm)/100/self.radius(s)
            T.append(np.interp(q,self.x,y[:m,j],right=np.nan))
            C.append(np.interp(q,self.x,y[m:,j],right=np.nan))
        return np.array(T),np.array(C)

def write_csv(path,t,a,header):
    np.savetxt(path,np.column_stack([t,a]),delimiter=',',
               header=header,comments='',fmt='%.10g')

def export_case(model,label,dt,end=None):
    end=model.stop if end is None else end
    ts=np.arange(dt,end+1e-9,dt,dtype=float)
    if ts.size==0 or ts[-1]<end: ts=np.r_[ts,end]
    distances=np.arange(21)/10
    T,C=model.sample(ts,distances)
    header='time_s,'+','.join(f'{r:g}' for r in distances)
    if label in (1,2): write_csv(OUT/f'result{label}_T.csv',ts,T,header)
    if label==4:
        surface=model.evaluate(ts)[-1]
        C=np.column_stack([C[:,:20],surface])
        header='time_s,'+','.join(f'{r:g}' for r in distances[:20])+',surface'
        write_csv(OUT/'radius_output.csv',ts,np.array([model.radius(t)*100 for t in ts]),'time_s,radius_cm')
    write_csv(OUT/f'result{label}_C.csv',ts,C,header)
    return ts,T,C

def audit(model):
    ts=np.linspace(0,model.stop,1001)
    y=model.evaluate(ts); m=model.n+1
    C=y[m:]
    residual=[]
    for t,z in zip(ts[::10],y.T[::10]):
        dc=model.rhs(t,z)[m:]
        residual.append(abs(2*np.dot(model.vol,dc)+2*model.hm/model.radius(t)*(z[-1]-model.ambient(t)[1])))
    return dict(min_C=float(C.min()),max_C=float(C.max()),
                radial_increase_max=float(np.maximum(np.diff(C,axis=0),0).max()),
                balance_residual_max=float(max(residual)),
                stop_s=model.stop,crossing_s=model.crossing,
                stop_max_C=float(model.evaluate([model.stop])[m:].max()),
                prev_second_max_C=float(model.evaluate([model.stop-1])[m:].max()),
                nfev=sum(p.nfev for p in model.parts))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,default=800)
    ap.add_argument('--validation',action='store_true');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    summary={'n':args.n,'tail':[50.,.05],'rtol':2e-8,'atol':2e-10}
    cases={}
    for mode,label,end in [(1,'q1',1800),(2,'q23',None),(4,'q4',None)]:
        start=time.time();m=Drying(mode,args.n).run(end);cases[label]=m
        summary[label]=audit(m)
        print(label,summary[label], 'elapsed',time.time()-start,flush=True)
    export_case(cases['q1'],1,1)
    export_case(cases['q23'],2,1,10800)
    export_case(cases['q23'],3,60)
    export_case(cases['q4'],4,60)
    # These coarse profiles are unrounded sources for figures and paper tables.
    for label,m in cases.items():
        times=np.linspace(0,m.stop,1001)
        vals=m.evaluate(times)
        np.savez_compressed(OUT/f'{label}_profiles.npz',times=times,x=m.x,
                            T=vals[:m.n+1].T,C=vals[m.n+1:].T,
                            R=np.array([m.radius(t) for t in times]))
    for key,times in [('q1',[100,300,600,900,1200,1500,1800]),
                      ('q23',np.arange(1800,10801,1800))]:
        T,C=cases[key].sample(times,[0,.5,1,1.5,2])
        summary[key]['paper_t']=list(map(float,times))
        summary[key]['paper_T']=T.tolist();summary[key]['paper_C']=C.tolist()
    for key in ['q23','q4']:
        m=cases[key];ts=np.r_[np.arange(21600,m.stop,21600),m.stop]
        _,C=m.sample(ts,[0,.5,1,1.5,2])
        summary[key]['long_t']=ts.tolist()
        summary[key]['long_C']=C.tolist()
        summary[key]['long_surface']=m.evaluate(ts)[-1].tolist()
        summary[key]['long_radius']=[m.radius(t)*100 for t in ts]
    if args.validation:
        summary['convergence']=[]
        for n in [args.n//2,args.n*2]:
            for mode,key,end in [(1,'q1',1800),(2,'q23',None),(4,'q4',None)]:
                m=Drying(mode,n).run(end)
                ref=cases[key]
                ts=np.unique(np.r_[1,2,3,10,30,np.linspace(60,min(m.stop,ref.stop),200)])
                Ta,Ca=m.sample(ts,[0,.5,1,1.5,2]);Tb,Cb=ref.sample(ts,[0,.5,1,1.5,2])
                row=dict(n=n,case=key,crossing_s=m.crossing,
                         max_T_diff=float(np.nanmax(abs(Ta-Tb))),
                         max_C_diff=float(np.nanmax(abs(Ca-Cb))))
                summary['convergence'].append(row);print('convergence',row,flush=True)
        summary['sensitivity']=[]
        tests=[('tail_last',dict(tail=tuple(cases['q23'].air[-1,1:]))),
               ('tail_lowT',dict(tail=(49.5,.05))),('tail_highT',dict(tail=(50.5,.05))),
               ('hm_-10%',dict(hm=7.2e-7)),('hm_+10%',dict(hm=8.8e-7)),
               ('D_-10%',dict(diffusion_scale=.9)),('D_+10%',dict(diffusion_scale=1.1))]
        for mode,key in [(2,'q23'),(4,'q4')]:
            for name,opts in tests:
                m=Drying(mode,args.n//2,**opts).run()
                row=dict(case=key,test=name,hours=m.crossing/3600)
                summary['sensitivity'].append(row);print('sensitivity',row,flush=True)
        for shrink in [False,True]:
            m=Drying(4,args.n//2,shrink=shrink).run()
            summary['sensitivity'].append(dict(case='q4',test='shrink_'+str(shrink),hours=m.crossing/3600))
    # JSON null / CSV nan mean physical points outside the shrunken cylinder.
    def clean(obj):
        if isinstance(obj,dict): return {k:clean(v) for k,v in obj.items()}
        if isinstance(obj,list): return [clean(v) for v in obj]
        if isinstance(obj,float) and not np.isfinite(obj): return None
        return obj
    (OUT/'summary.json').write_text(json.dumps(clean(summary),ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__': main()

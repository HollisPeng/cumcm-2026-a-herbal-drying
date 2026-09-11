"""Independent saved-file checks plus an analytic constant-property heat test."""
from pathlib import Path
import json
import argparse
import numpy as np
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
def run(files_only=False):
    result={}
    for label in [1,2,3,4]:
        wb=openpyxl.load_workbook(ROOT/f'results/workbooks/result{label}.xlsx',data_only=True,read_only=True)
        fields=[('温度','T'),('水分浓度','C')] if label<=2 else [('Sheet1','C')]
        for sheet,field in fields:
            expected=np.loadtxt(ROOT/f'results/result{label}_{field}.csv',delimiter=',',skiprows=1)
            rows=list(wb[sheet].values)
            saved=np.array([[np.nan if v is None else v for v in row] for row in rows[1:]],float)
            assert saved.shape==expected.shape,(label,sheet,saved.shape,expected.shape)
            assert np.array_equal(np.isnan(saved),np.isnan(expected))
            assert np.max(abs(saved[:,0]-expected[:,0]))==0
            err=float(np.nanmax(abs(saved[:,1:]-expected[:,1:])))
            assert err<=.00005001,err
            result[f'result{label}_{field}']={'rows':len(saved),'columns':saved.shape[1],
                                            'rounding_error_max':err,'last_time_s':saved[-1,0]}
        if label == 4:
            expected=np.loadtxt(ROOT/'results/radius_output.csv',delimiter=',',skiprows=1)
            saved=np.array(list(wb['表面位置'].values)[1:],float)
            assert saved.shape == expected.shape
            assert np.array_equal(saved[:,0],expected[:,0])
            err=float(np.max(abs(saved[:,1]-expected[:,1])))
            assert err<=.00005001,err
            result['surface_radius']={'rows':len(saved),'rounding_error_max':err}
        wb.close()
    if files_only:
        print(json.dumps(result,indent=2))
        return
    # For constant ambient 50 deg C, a cylinder has a Bessel-series solution.
    from scipy.special import j0,j1
    from scipy.optimize import brentq
    from solve import Drying
    m=Drying(1,800);m.air=np.array([[0.,50.,.05],[1800.,50.,.05]])
    m.run(1800.,rtol=2e-10,atol=2e-12)
    Bi=25*.02/.36
    def equation(z): return z*j1(z)-Bi*j0(z)
    grid=np.linspace(1e-8,160,20000);roots=[]
    for a,b in zip(grid[:-1],grid[1:]):
        if equation(a)*equation(b)<0: roots.append(brentq(equation,a,b))
    roots=np.array(roots)
    coeff=2*j1(roots)/(roots*(j0(roots)**2+j1(roots)**2))
    times=np.array([100.,600.,1800.]);dist=np.array([0,.5,1,1.5,2])
    numerical=m.sample(times,dist)[0]
    analytic=np.array([50+(28-50)*np.sum(coeff[:,None]*j0(roots[:,None]*dist[None,:]/2)
                          *np.exp(-.36/(820*2600)*roots[:,None]**2*t/.02**2),axis=0)
                       for t in times])
    result['analytic_heat_max_error_degC']=float(abs(numerical-analytic).max())
    assert result['analytic_heat_max_error_degC']<.0002
    (ROOT/'results/verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--files-only',action='store_true',
                        help='Check saved workbooks against CSVs without solving or writing files.')
    run(files_only=parser.parse_args().files_only)

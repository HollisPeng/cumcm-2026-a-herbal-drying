"""Regenerate all paper figures from solve.py outputs; no GUI required."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
S=json.loads((ROOT/'results/summary.json').read_text())
P={k:np.load(ROOT/f'results/{k}_profiles.npz') for k in ['q1','q23','q4']}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
                     'axes.spines.top':False,'axes.spines.right':False,
                     'figure.dpi':120,'savefig.dpi':220,'axes.grid':True,
                     'grid.alpha':.2,'lines.linewidth':1.6})
colors=['#185A9D','#C4562A','#37866B','#895D9A']
def finish(fig,name):
    fig.tight_layout(pad=1.2);fig.savefig(OUT/name,bbox_inches='tight');plt.close(fig)

a=np.loadtxt(ROOT/'data/air.csv',delimiter=',',skiprows=1)
r=np.loadtxt(ROOT/'data/radius.csv',delimiter=',',skiprows=1)
fig,axs=plt.subplots(1,3,figsize=(7,2.2))
for ax,j,label in [(axs[0],1,'Air temperature (deg C)'),(axs[1],2,'Air moisture (kg/kg)')]:
    ax.plot(a[:,0]/3600,a[:,j],color=colors[j-1]);ax.set(xlabel='Time (h)',ylabel=label)
axs[2].plot(r[:,0]/3600,r[:,1],color=colors[2]);axs[2].set(xlabel='Time (h)',ylabel='Radius (cm)')
finish(fig,'01_inputs.png')

p=P['q1'];fig,axs=plt.subplots(1,2,figsize=(7,2.4))
for j,t in enumerate([100,600,1800]):
    for ax,field in zip(axs,['T','C']):
        profile=np.array([np.interp(t,p['times'],col) for col in p[field].T])
        ax.plot(p['x']*2,profile,label=f'{t} s',color=colors[j])
for ax,y in zip(axs,['Temperature (deg C)','Moisture (kg/kg)']):
    ax.set(xlabel='Radius (cm)',ylabel=y);ax.legend(frameon=False,fontsize=8)
finish(fig,'02_preheat.png')

p=P['q23'];fig,axs=plt.subplots(1,2,figsize=(7,2.4))
for ax,field in zip(axs,['T','C']):
    a=np.loadtxt(ROOT/f'results/result2_{field}.csv',delimiter=',',skiprows=1)
    ax.plot(a[:,0]/3600,a[:,1],label='Center',color=colors[0])
    ax.plot(a[:,0]/3600,a[:,-1],label='Surface',color=colors[1]);ax.set_xlabel('Time (h)')
    ax.legend(frameon=False,fontsize=8)
axs[0].set_ylabel('Temperature (deg C)');axs[1].set_ylabel('Moisture (kg/kg)')
finish(fig,'03_first3h.png')

fig,axs=plt.subplots(1,2,figsize=(7,2.5))
for ax,key,title in zip(axs,['q23','q4'],['Fixed radius','Measured shrinkage']):
    p=P[key];t=p['times']/3600
    ax.plot(t,p['C'][:,0],label='Center',color=colors[0])
    ax.plot(t,p['C'][:,-1],label='Surface',color=colors[1])
    ax.axhline(.15,color='#666666',linestyle='--',label='Limit 0.15')
    ax.set(xlabel='Time (h)',ylabel='Moisture (kg/kg)',title=title,yscale='log',ylim=(.045,3))
    ax.legend(frameon=False,fontsize=7.5)
finish(fig,'04_drying.png')

p=P['q4'];fig,axs=plt.subplots(1,2,figsize=(7,2.5))
axs[0].plot(p['times']/3600,p['R']*100,color=colors[2])
axs[0].set(xlabel='Time (h)',ylabel='Radius (cm)')
for j,t in enumerate([6*3600,24*3600,S['q4']['stop_s']]):
    profile=np.array([np.interp(t,p['times'],col) for col in p['C'].T])
    radius=np.interp(t,p['times'],p['R'])
    axs[1].plot(p['x']*radius*100,profile,color=colors[j],label=f'{t/3600:.2f} h')
axs[1].set(xlabel='Physical radius (cm)',ylabel='Moisture (kg/kg)')
axs[1].legend(frameon=False,fontsize=8)
finish(fig,'05_shrinkage.png')
print('Saved five figures to',OUT)

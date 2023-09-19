#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 15:54:07 2022

Taking a look at a lot of the raw data from the Bowman plots

Would be way better with functions, instead of copy/paste stuff

Check and make sure all axes are the same

@author: spencerjordan
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

## Top level directory with data files --> Set up for mac/linux
DIR = '/Users/spencerjordan/Documents/bowman_data_analysis'

pw_data = pd.read_csv(DIR+'/ALL_PORE_WATER_COMPILED.CSV')

## Cleaning the depth input
outliers_N = ['30n','30N','30.1']
outliers_S = ['30s','30S','30.2']
for out in outliers_N:
    pw_data['Depth'][pw_data['Depth']==out] = '30 N'
for out in outliers_S:
    pw_data['Depth'][pw_data['Depth']==out] = '30 S'

pw_data['Depth'][pw_data['Depth']=='188'] = '180'

pw_depths = pw_data['Depth'].unique()
t = []
for k,val in enumerate(pw_depths):
    try:
        int(val)
        t.append(int(val))
    except:
        print(val)
pw_depths = t
pw_depths.append('30 N')
pw_depths.append('30 S')


## Going to organize by Al#
# Get unique values of Al
al_vals = pw_data['Al#'].unique()
t = []
for k,val in enumerate(al_vals):
    try:
        int(val)
        t.append(int(val))
    except:
        print(val)
al_vals = t

#%% Pore-water -  ppm NH4-N

for depth in pw_depths:
    fig, ax1 = plt.subplots(4,2,figsize=[12,10])
    fig.tight_layout()
    fig.suptitle(f'Pore Water: ppm NH4-N Depth = {depth}',fontsize=14,y=1.03)
    fig.supylabel('ppm-NH4-N',x=-0.02,fontsize=14)
    fig.supxlabel('Date',y=-0.02,fontsize=14)
    
    a = 0
    b = 0
    for key in al_vals:
        dat = pw_data[pw_data['Al#']==str(key)]
        dat = dat[dat['Depth']==str(depth)]
        dates = pd.to_datetime(dat['Date'],format='%m/%d/%y')
        dat['datetime'] = dates
        dat.set_index('datetime',inplace=True)
        dat.sort_index(inplace=True)
        ax1[a,b].plot(dat.index,dat['ppm NH4-N'],color='darkred')
        ## Add in a depth line?
        #ax2 = ax1[a,b].twinx()
        #ax2.set_ylabel('Y2-axis')
        #ax2.plot(dat['datetime'],dat['Depth'],color='red',alpha=0.4)
        
        ax1[a,b].set_xlim([pd.to_datetime(2017,format='%Y'),pd.to_datetime('2022-4',format='%Y-%m')])
        #ax[a,b].xaxis.set_major_locator(mdates.DayLocator(interval=365))
        ax1[a,b].set_title(f'Al#{key}',fontsize=11,y=0.98)
        ax1[a,b].grid()
        #ax1[a,b].xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax1[a,b].xaxis.get_major_locator()))
        
        ## Tickmark and Label Formatting
        ax1[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
        ax1[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
        ax1[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
        
        if b == 0:
            b = 1
        else:
            b = 0
        if b == 0:
            a += 1
    
    ax1[-1, -1].set_title('')        
    ax1[-1, -1].axis('off')
    #plt.savefig(DIR+f'/plots/pw/ppm_NH4-N-{depth}.png',dpi=200,bbox_inches='tight')


#%% Pore Water ppm NO3-N

pw_data['Depth'] = pw_data['Depth'].replace(['30 S'],'30') 
pw_data['Depth'] = pw_data['Depth'].replace(['30 N'],'30') 
pw_data['Depth'] = pw_data['Depth'].replace(['200'],'180') 
pw_data['Depth'] = pw_data['Depth'].replace(['290'],'280') 
pw_data['Depth'] = pw_data['Depth'].replace(['300'],'280') 

pw_depths = pw_data['Depth'].unique()

# Going year-by-year through the dataset
years = [2018,2019,2020,2021,2022]

for depth in pw_depths:
    fig2, ax2 = plt.subplots(3,2,figsize=[10,8])
    fig2.tight_layout()
    fig2.suptitle(f'Pore Water: ppm NO3-N Depth = {depth}',fontsize=14,y=1.03)
    fig2.supylabel('ppm-NO3-N',x=-0.02,fontsize=14)
    fig2.supxlabel('Date',y=-0.02,fontsize=14)
    a = 0
    b = 0
    for year in years:
        for key in al_vals:
            dat = pw_data[pw_data['Al#']==str(key)]
            dat = dat[dat['Depth']==str(depth)]
            dat = dat[dat['ppm NO3-N']!='redo']
            dates = pd.to_datetime(dat['Date'],format='%m/%d/%y')
            dat['datetime'] = dates
            dat = dat[dat['datetime']>=pd.to_datetime(year,format='%Y')]
            dat = dat[dat['datetime']<=pd.to_datetime(year+1,format='%Y')]
            
            try:
                dat['ppm NO3-N'] = pd.to_numeric(dat['ppm NO3-N'])
            except:
                print('dtype convertsion failed')
    
            dat.set_index('datetime',inplace=True)
            dat.sort_index(inplace=True)
            
            dat['ppm NO3-N'][dat['ppm NO3-N'] == 0] = 0.025
            
            dat = dat[pd.to_numeric(dat['ppm NO3-N'], errors='coerce').notnull()]
            ax2[a,b].plot(dat.index,dat['ppm NO3-N'],label=f'Al#{key}')

            
            #ax2[a,b].yaxis.set_major_locator(MaxNLocator(5)) 
            #ax2[a,b].xaxis.set_major_locator(MaxNLocator(5)) 
            
            ax2[a,b].set_xlim([pd.to_datetime(year,format='%Y'),pd.to_datetime(year+1,format='%Y')])
            #ax[a,b].xaxis.set_major_locator(mdates.DayLocator(interval=365))
            ax2[a,b].set_title(f'Al#{key}',fontsize=11,y=0.98)
            
            
            ## Tickmark and Label Formatting
            ax2[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax2[a,b].xaxis.set_minor_locator(mdates.MonthLocator(1))
            #ax2[a,b].xaxis.set_major_locator(mdates.MonthLocator())
            ax2[a,b].grid(b=True, which='major', color='grey', linestyle='-')
            ax2[a,b].set_title(f'{year}',y=0.985)
            
        
            
        # Set the indexes
        if b == 0:
            b = 1
        else:
            b = 0
        if b == 0:
            a += 1
    
    ax2[-1, -1].set_title('')
    ax2[-1, -1].axis('off')
    #plt.savefig(DIR+f'/plots/pw/ppm_NO3-N-{depth}.png',dpi=200,bbox_inches='tight')
    ax2[-1,-2].legend(loc=5,bbox_to_anchor=(1.2, 0.2, 0.5, 0.5),fontsize=12)
    #plt.savefig(f'/Users/spencerjordan/Documents/AGU_figures_2022/pw_NO3_{depth}.png',
    #            dpi=200,bbox_inches='tight')
    

#%% Neutron Probe - Water Content
# Plot stations together
# Potentially plot each year as a seperate line
np_data = pd.read_csv(DIR+'/np2018_2022_Spencer_Update.csv')

np_depths = np_data['Depth'].unique()

## Going to replace all of the '1', etc with 'Al-1' etc --> ASSUMING they're the same
# Fixing some syntaxing
np_data['Site'][np_data['Site']=='AL-1'] = 'Al-1'
np_data['Site'][np_data['Site']=='AL-2'] = 'Al-2'
# Formatting site names
for site in range(1,9):
    np_data['Site'][np_data['Site']==str(site)] = 'Al-'+str(site)
sites = np.unique(np_data['Site'])


for depth in np_depths:
    fig, ax = plt.subplots(4,2,figsize=[10,8])
    fig.tight_layout()
    
    fig.suptitle(f'Neutron Probe: Water Content Depth = {depth}',fontsize=14,y=1.03)
    fig.supylabel('Water Content',x=-0.02,fontsize=14)
    fig.supxlabel('Date',y=-0.02,fontsize=14)
    a = 0
    b = 0
    
    for site in sites:
        data = np_data[np_data['Site'] == site]
        data = data[data['Depth']==depth]
        
        ## Uppler y-limit
        data = data[data['water content']<=0.5]
        
        datetime = pd.to_datetime(data['date'],format='%m/%d/%y')
        data['datetime'] = datetime
        data.set_index('datetime',inplace=True)
        #data = data.resample('100d').mean()
        #ax[a,b].scatter(data.index,data['water content'],color='darkgreen',marker='o')
        ax[a,b].plot(data.index,data['water content'],color='darkgreen',marker='o',markersize=3.5,lw=1.2)
        #ax[a,b].set_ylim([0,0.5])
        ax[a,b].set_xlim([pd.to_datetime(2018,format='%Y'),pd.to_datetime('2022-08',format='%Y-%m')])
        #ax[a,b].set_xlim([pd.to_datetime('2022-08',format='%Y-%m'),pd.to_datetime('2022-08',format='%Y-%m')])
        ## Tick formatting and labels
        ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
        ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
        ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
        
        ax[a,b].set_title(f'{site}',y=0.965)
        ax[a,b].grid()
        # Set in the indexes
        if b == 0:
            b = 1
        else:
            b = 0
        if b == 0:
            a += 1
            
    ax[-1, -1].set_title('')
    ax[-1, -1].axis('off')
    #plt.savefig(DIR+f'/plots/np/water_content-{depth}.png',dpi=200,bbox_inches='tight')

#%% Neutron Probe - Water Content --> By year, with all monitors on same plot
np_data = pd.read_csv(DIR+'/np2018_2022_Spencer_Update.csv')
np_depths = np_data['Depth'].unique()

## Going to replace all of the '1', etc with 'Al-1' etc --> ASSUMING they're the same
# Fixing some syntaxing
np_data['Site'][np_data['Site']=='AL-1'] = 'Al-1'
np_data['Site'][np_data['Site']=='AL-2'] = 'Al-2'
# Formatting site names
for site in range(1,9):
    np_data['Site'][np_data['Site']==str(site)] = 'Al-'+str(site)
sites = np.unique(np_data['Site'])

# Going year-by-year through the dataset
years = [2018,2019,2020,2021,2022]

for depth in np_depths:
    fig, ax = plt.subplots(3,2,figsize=[10,8])
    fig.tight_layout()
    
    fig.suptitle(f'Neutron Probe Water Content at {depth} cm',fontsize=14,y=1.03)
    fig.supylabel('Water Content',x=-0.02,fontsize=14)
    fig.supxlabel('Month',y=-0.02,fontsize=14)
    a = 0
    b = 0
    for year in years:
        
        for site in sites:
            data = np_data[np_data['Site']==site]
            data = data[data['Depth']==depth]
            ## Uppler y-limit
            data = data[data['water content']<=0.5]
            
            datetime = pd.to_datetime(data['date'],format='%m/%d/%y')
            data['datetime'] = datetime
            ## Getting the yearly range of data
            data = data[data['datetime']>=pd.to_datetime(year,format='%Y')]
            data = data[data['datetime']<=pd.to_datetime(year+1,format='%Y')]
            data.set_index('datetime',inplace=True)
            data = data.sort_index()
            
            ax[a,b].plot(data.index,data['water content'],marker='o',
                         markersize=3.5,lw=1.2,label=f'{site}')
        ax[a,b].set_xlim([pd.to_datetime(year,format='%Y'),pd.to_datetime(year+1,format='%Y')])
        
        ## Tick formatting and labels
        ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator(1))
        ax[a,b].xaxis.set_major_locator(mdates.MonthLocator())
        ax[a,b].set_title(f'{year}',y=0.985)
        #ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
        if year == years[-1]:
            ax[a,b].legend(loc=5,bbox_to_anchor=(1.2, 0.25, 0.5, 0.5),fontsize=13,
                           title='Station')
        
        #ax[a,b].set_title(f'{site}',y=0.965)
        ax[a,b].grid()
        # Set in the indexes
        if b == 0:
            b = 1
        else:
            b = 0
        if b == 0:
            a += 1
            
    ax[-1, -1].set_title('')
    ax[-1, -1].axis('off')
    #plt.savefig(DIR+f'/plots/np/water_content-{depth}_combined.png',dpi=200,bbox_inches='tight')




#%% Multi-Level Sampling - NO3-N
ml_data = pd.read_csv(DIR+'/Bowman-MW-multilevel-sampling-ALL-DATA-2021-spencer.csv')
ml_data = ml_data.fillna(0)
## Getting unique monitoring wells
mw = np.unique(ml_data['MW#'])
mw = mw[:-7]

fig, ax = plt.subplots(7,2,figsize=[12,10])
fig.tight_layout()

fig.suptitle('Multi-Level Sampling - NO3-N',fontsize=15,y=1.03)
fig.supylabel('NO3-N [mg/l]',x=-0.02,fontsize=15)
fig.supxlabel('Sample Depth',y=-0.02,fontsize=15)

## Lower Limit
ll = 5

a = 0
b = 0
for well in mw:
    data = ml_data[ml_data['MW#'] == well]
    data = data[data['NO3-N mg/L'] >= ll]
    ax[a,b].plot(data['depth (m)'],data['NO3-N mg/L'],color='darkviolet',
                 lw=2,label=f'Depth Data: Lower Limit={ll}')
    ax[a,b].set_title(f'MW# {well}',y = 0.96)
    ax[a,b].grid()
    
    try:
        ax[a,b].set_xlim(right='7b')
    except:
        pass
    #ax[a,b].set_ylim(bottom=1.3)
    try:    
        gw_all_val = data['NO3-N mg/L'][data['depth (m)']=='GW all'].iloc[0]
        ax[a,b].axhline(gw_all_val,color='red',alpha=0.5,ls='--',label='GW All')
    except:
        pass
    
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

ax[-1,-2].legend(loc=5,bbox_to_anchor=(1.2, 0.5, 0.5, 0.5),fontsize=12)
ax[-1, -1].set_title('')
ax[-1, -1].axis('off')
plt.savefig(DIR+'/plots/ml/mls_NO3-N.png',dpi=200,bbox_inches='tight')

#%% Multi-Level Sampling - EC dS/m
ml_data = pd.read_csv(DIR+'/Bowman-MW-multilevel-sampling-ALL-DATA-2021-spencer.csv')

## Getting unique monitoring wells
mw = np.unique(ml_data['MW#'])
mw = mw[:-7]

fig, ax = plt.subplots(7,2,figsize=[12,10])
fig.tight_layout()

fig.suptitle('Multi-Level Sampling - EC dS/m',fontsize=15,y=1.03)
fig.supylabel('EC [dS/m]',x=-0.02,fontsize=15)
fig.supxlabel('Sample Depth',y=-0.02,fontsize=15)

## Lower Limit of figure
ll = 0.3

a = 0
b = 0
for well in mw:
    data = ml_data[ml_data['MW#'] == well]
    data = data[data['EC dS/m'] >= ll]
    ax[a,b].plot(data['depth (m)'],data['EC dS/m'],color='darkcyan',
                 lw=2,label=f'Depth Data: Lower Limit={ll}')
    ax[a,b].set_title(f'MW# {well}',y = 0.96)
    ax[a,b].grid()
    try:
        ax[a,b].set_xlim(right='7b')
    except:
        pass
    #ax[a,b].set_ylim(bottom=1.3)
    try:    
        gw_all_val = data['EC dS/m'][data['depth (m)']=='GW all'].iloc[0]
        ax[a,b].axhline(gw_all_val,color='red',alpha=0.5,ls='--',label='GW All')
    except:
        pass
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1
ax[-1,-2].legend(loc=5,bbox_to_anchor=(1.2, 0.5, 0.5, 0.5),fontsize=12)
ax[-1, -1].set_title('')
ax[-1, -1].axis('off')
plt.savefig(DIR+'/plots/ml/mls_EC.png',dpi=200,bbox_inches='tight')

#%% Multi-Level Sampling - NO3/EC
ml_data = pd.read_csv(DIR+'/Bowman-MW-multilevel-sampling-ALL-DATA-2021-spencer.csv')

## Getting unique monitoring wells
mw = np.unique(ml_data['MW#'])
mw = mw[:-7]

fig, ax = plt.subplots(7,2,figsize=[12,10])
fig.tight_layout()

fig.suptitle('Multi-Level Sampling - NO3/EC',fontsize=15,y=1.03)
fig.supylabel('NO3/EC',x=-0.02,fontsize=15)
fig.supxlabel('Sample Depth',y=-0.02,fontsize=15)

a = 0
b = 0
for well in mw:
    data = ml_data[ml_data['MW#'] == well]
    data = data[data['NO3/EC']!='#VALUE!']
    #data = data[data['NO3/EC'] >= 0.3]
    ax[a,b].plot(data['depth (m)'],data['NO3/EC'],color='darkolivegreen',
                 lw=2,label='Depth Data: No Lower Limit')
    
    ax[a,b].set_title(f'MW# {well}',y = 0.96)
    ax[a,b].yaxis.set_major_locator(MaxNLocator(5))
    ax[a,b].grid()
    
    if well == 5 or well == 6:
        ax[a,b].set_xlim(right='7a')
    else:
        ax[a,b].set_xlim(right='7b')
    #ax[a,b].set_ylim(bottom=1.3) 
    gw_all_val = data['NO3/EC'][data['depth (m)']=='GW all'].iloc[0]
    if well == 1:
        gw_all_val = float(gw_all_val)
    else:
        pass
    ax[a,b].axhline(gw_all_val,color='red',alpha=0.5,ls='--',label='GW All')
    
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

ax[-1,-2].legend(loc=5,bbox_to_anchor=(1.2, 0.5, 0.5, 0.5),fontsize=12)
ax[-1, -1].set_title('')
ax[-1, -1].axis('off')
plt.savefig(DIR+'/plots/ml/mls_NO3_EC.png',dpi=200,bbox_inches='tight')

#%% Looking at Queried data that Hanni downloaded - Well Water Levels
## Using some updated data
wl_data = pd.read_csv(DIR+'/BOW-MW-ALL-DATA-Compiled_update.csv')
wells = ml_data['MW#'].unique()
# Dropping nan well value
wells = wells[:20]

fig, ax = plt.subplots(10,2,figsize=[16,16])
fig.tight_layout()
fig.suptitle('Well Water Levels',y=1.015,fontsize=15)
fig.supxlabel('Date',fontsize=15,y=-0.01)
fig.supylabel('Water Level [Feet]',fontsize=15,x=-0.01)

a = 0
b = 0

for well in wells:
    data = wl_data[wl_data['MW#'] == well]
    dt = pd.to_datetime(data['Sampling Date'],format='%m/%d/%y')
    data['date'] = dt
    
    ax[a,b].plot(data['date'],data['DTW (feet)'],label=f'Well #{int(well)}',
                 color='midnightblue',lw=2)
    ax[a,b].xaxis.set_major_locator(MaxNLocator(4))
    ax[a,b].grid()
    ax[a,b].legend(fontsize=14,loc='upper center')
    
    ## Tickmark and Label Formatting
    ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
    ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
    
    #ax[a,b].set_title(f'Well #{well}',y=0.965)
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

plt.show()
#plt.savefig(DIR+'/plots/wl/well_water_levels.png',dpi=200,bbox_inches='tight')


#%% Looking at Queried data that Hanni downloaded - pH

wl_data = pd.read_csv(DIR+'/BOW-MW-ALL-DATA-Compiled.csv')
wells = ml_data['MW#'].unique()
# Dropping nan well value
wells = wells[:20]

fig, ax = plt.subplots(10,2,figsize=[16,16])
fig.tight_layout()
fig.suptitle('Well Water pH',y=1.015,fontsize=15)
fig.supxlabel('Date',fontsize=15,y=-0.01)
fig.supylabel('pH',fontsize=15,x=-0.01)

a = 0
b = 0

for well in wells:
    data = wl_data[wl_data['MW#'] == well]
    dt = pd.to_datetime(data['Sampling Date'],format='%m/%d/%Y')
    data['date'] = dt
    
    ax[a,b].plot(data['date'],data['pH'],label=f'Well #{int(well)}',
                 color='red',linewidth=2)
    ax[a,b].xaxis.set_major_locator(MaxNLocator(4))
    ax[a,b].grid()
    ax[a,b].legend(fontsize=14,loc='upper center')
    
    ## Tickmark and Label Formatting
    ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
    ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
    
    #ax[a,b].set_title(f'Well #{well}',y=0.965)
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

plt.savefig(DIR+'/plots/wl/well_water_pH.png',dpi=200,bbox_inches='tight')


#%% Looking at Queried data that Hanni downloaded - Temp

wl_data = pd.read_csv(DIR+'/BOW-MW-ALL-DATA-Compiled.csv')
wells = ml_data['MW#'].unique()
# Dropping nan well value
wells = wells[:20]

fig, ax = plt.subplots(10,2,figsize=[16,16])
fig.tight_layout()
fig.suptitle('Well Water Temperature',y=1.015,fontsize=15)
fig.supxlabel('Date',fontsize=15,y=-0.01)
fig.supylabel('Temp [C]',fontsize=15,x=-0.01)

a = 0
b = 0

for well in wells:
    data = wl_data[wl_data['MW#'] == well]
    dt = pd.to_datetime(data['Sampling Date'],format='%m/%d/%Y')
    data['date'] = dt
    
    ax[a,b].plot(data['date'],data['Temp C'],label=f'Well #{int(well)}',
                 color='purple',linewidth=2)
    ax[a,b].xaxis.set_major_locator(MaxNLocator(4))
    ax[a,b].grid()
    ax[a,b].legend(fontsize=14,loc='upper center')
    
    ## Tickmark and Label Formatting
    ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
    ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
    
    #ax[a,b].set_title(f'Well #{well}',y=0.965)
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

plt.savefig(DIR+'/plots/wl/well_water_temp.png',dpi=200,bbox_inches='tight')


#%% Looking at Queried data that Hanni downloaded - Ec(mV) [?]

wl_data = pd.read_csv(DIR+'/BOW-MW-ALL-DATA-Compiled.csv')
wells = ml_data['MW#'].unique()
# Dropping nan well value
wells = wells[:20]

fig, ax = plt.subplots(10,2,figsize=[16,16])
fig.tight_layout()
fig.suptitle('Well Water Eh',y=1.015,fontsize=15)
fig.supxlabel('Date',fontsize=15,y=-0.01)
fig.supylabel('Eh [mV]',fontsize=15,x=-0.01)

a = 0
b = 0

for well in wells:
    data = wl_data[wl_data['MW#'] == well]
    dt = pd.to_datetime(data['Sampling Date'],format='%m/%d/%Y')
    data['date'] = dt
    
    ax[a,b].plot(data['date'],data['Eh(mV)'],label=f'Well #{int(well)}',
                 color='purple',linewidth=2)
    ax[a,b].xaxis.set_major_locator(MaxNLocator(4))
    ax[a,b].grid()
    ax[a,b].legend(fontsize=14,loc='upper center')
    
    ## Tickmark and Label Formatting
    ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    ax[a,b].xaxis.set_minor_locator(mdates.MonthLocator())
    ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
    
    #ax[a,b].set_title(f'Well #{well}',y=0.965)
    # Set in the indexes
    if b == 0:
        b = 1
    else:
        b = 0
    if b == 0:
        a += 1

#plt.savefig(DIR+'/plots/wl/well_water_Eh(mV).png',dpi=200,bbox_inches='tight')



#%% Soil Data --> histograms with error bars

filename = f'{DIR}/soil-bwn-inorgan-N-2022_spencer.csv'

soil_data = pd.read_csv(filename)
soil_data['Date'] = pd.to_datetime(soil_data['Date'])
soil_data = soil_data.sort_values(by='Date')

soil_data = soil_data[soil_data['Date'] >= pd.to_datetime('01/01/2020',format='%m/%d/%Y')]
dates = soil_data['Date'].unique()
dates = dates[~np.isnan(dates)]
#remove = dates[1]
#dates = np.delete(dates,1)

blocks = ['1','2','3','4','5']
mean = []
std = []

dat = {}
width = 0.15
x = np.arange(len(blocks))
fig, ax = plt.subplots()
fig.tight_layout()

for date in dates:
    subset = soil_data[soil_data['Date'] == date]
    m = []
    s = []
    for block in blocks:
        sub = subset[subset['Block'] == block]
        mean = sub['lbs NH-N/acre-soil'].mean()
        #print(mean)
        #std = sub['lbs NO3-N/acre-soil'].std()
        #print(std)
        m.append(mean)
        s.append(std)
    
    dat[date] = [m,s]
        
''' 
rects1 = ax.bar(x-0.18,dat[dates[0]][0],width)
rects1 = ax.bar(x,dat[dates[1]][0],width)
rects1 = ax.bar(x+0.17,dat[dates[2]][0],width)
rects1 = ax.bar(x+0.34,dat[dates[3]][0],width)    
'''

ax.set_axisbelow(True)
ax.grid()
rects1 = ax.bar(x-0.18,dat[dates[0]][0],width,label='Dec 2020',
                color='purple')
rects1 = ax.bar(x,dat[dates[1]][0],width,label='Mar 2021',
                color='goldenrod')
rects1 = ax.bar(x+0.17,dat[dates[2]][0],width,label='Feb 2022',
                color='green')
rects1 = ax.bar(x+0.34,dat[dates[3]][0],width,label='Nov 2022',
                color='mediumblue')

ax.legend(fontsize=11,loc=2)
ax.set_xticks(x, blocks)
ax.tick_params(labelsize=11)
ax.set_title('NH4-N')
ax.set_xlabel('Block',fontsize=12)
ax.set_ylabel('lbs NH4-N per acre-soil',fontsize=12)
ax.set_ylim([0,11])
plt.savefig(f'{DIR}/soil_sampling_bar_NH4.png',dpi=200,
            bbox_inches='tight')










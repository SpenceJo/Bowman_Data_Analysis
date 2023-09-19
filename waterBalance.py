#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 12:40:15 2023

Calculate the monthly water balance and predicted groudwater recharge for each block
Based on the massBalanceMainData.xlsx file

@author: spencerjordan
"""

import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline as spline
import os

#%% Loading the main data sheet
###############################################################################
######################## Create Main Monthly Plot #############################
###############################################################################
##!!! Adjust the ET for the NE blocks during replanting
def load_data():
    ## Using Hanna's Precip values
    mainDat = pd.read_csv('~/Documents/bowmanMassBalance/massBalanceMainData_92.csv',skiprows=1)
    ## Using CIMIS's precip values
    return mainDat

## Load the data from the atmosph.in files to make a better comparison between 
## the HYDRUS results and the water mass balance
def load_data_atmopsh():
    os.chdir('/Users/spencerjordan/Documents/Hydrus/python_scripts')
    from hydrus_model_bowman import atmosph
    os.chdir('/Users/spencerjordan/Documents/bowmanMassBalance')
    a = atmosph()
    a.main()
    atmosph_data = a.atmosph_data
    atmosph_data = atmosph_data[atmosph_data.index>pd.to_datetime('08/31/2012')]
    atmosph_data = atmosph_data[atmosph_data.index<pd.to_datetime('09/01/2022')]
    
    

def apply_ET_mult(mainDat):
    ##!!! Adding the 0.78ß adjustment factor to the ET --> gained from Ranch System comparison
    block_keys = ['NE1','NE2','NW','SW1','SW2','SE']
    for block in block_keys:
        mainDat[f'{block}_ET'] = mainDat[f'{block}_ET'] * 0.92
    return mainDat

def calculate_balance(mainDat):
    mainDat['NE1_balance'] = mainDat[['NE1_I','Precip']].sum(axis=1) - mainDat['NE1_ET']
    mainDat['NE2_balance'] = mainDat[['NE2_I','Precip']].sum(axis=1) - mainDat['NE2_ET']
    mainDat['NW_balance'] = mainDat[['NW_I','Precip']].sum(axis=1) - mainDat['NW_ET']
    mainDat['SW1_balance'] = mainDat[['SW1_I','Precip']].sum(axis=1) - mainDat['SW1_ET']
    mainDat['SW2_balance'] = mainDat[['SW2_I','Precip']].sum(axis=1) - mainDat['SW2_ET']
    mainDat['SE_balance'] = mainDat[['SE_I','Precip']].sum(axis=1) - mainDat['SE_ET']
    ##!!! Should think about doing an area weighted average...
    mainDat['avgBalance'] = mainDat[['NE1_balance','NE2_balance','NW_balance',
                                     'SW1_balance','SW2_balance','SE_balance']].mean(axis=1)
    mainDat['Date'] = pd.to_datetime(mainDat['Date'])
    mainDat = mainDat.set_index(pd.to_datetime(mainDat['Date']))
    #mainDat = pd.read_csv('~/Documents/bowmanMassBalance/massBalanceMainData.csv',skiprows=1)
    ## Cut to 2013 to 2022 season for Hanni's Paper
    mainDat = mainDat[mainDat.index>=pd.to_datetime('09/01/2012',format='%m/%d/%Y')]
    mainDat = mainDat[mainDat.index<pd.to_datetime('09/01/2022',format='%m/%d/%Y')]
    mainDat = mainDat.resample('1M').sum()
    mainDat['stdBalance'] = mainDat[['NE1_balance','NE2_balance','NW_balance',
                                     'SW1_balance','SW2_balance','SE_balance']].std(axis=1)
    ## Get 2022 subset where NE plots are not considered
    sub2022 = mainDat.loc[mainDat['G.season']==2022.0,:]
    mean2022 = sub2022[['NW_balance','SW1_balance','SW2_balance',
                            'SE_balance']].mean(axis=1)
    std2022 = sub2022[['NW_balance','SW1_balance','SW2_balance',
                            'SE_balance']].std(axis=1)
    mainDat.loc[mainDat['G.season']==2022.0,'avgBalance'] = mean2022
    mainDat.loc[mainDat['G.season']==2022.0,'stdBalance'] = std2022
    return mainDat


def create_figure(mainDat,mainDat_noMult):
    fig, ax = plt.subplots(figsize=[15,10])
    ax.bar(mainDat.index,mainDat['avgBalance'],width=30,
           label='Water Balance',
           edgecolor='black',
           linewidth=0.7,)
    ## Error bars if wanted
    ax.errorbar(mainDat.index,mainDat['avgBalance'],yerr=mainDat['stdBalance'],
                fmt='none',capsize=2,color='darkorange')
    ## Datetime axis formatting
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1,7)))
    ax.set_xticklabels(ax.get_xticks(), rotation = 45,fontsize=14)
    ax.set_yticklabels(ax.get_yticks(), fontsize=14)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%b"))
    #ax.grid()
    ax.set_title('Monthly Water Mass Balance\nMean +/- standard deviation across blocks',
                 fontsize=20,loc='left')
    ax.set_ylabel('Water Flux [cm]',fontsize=18)
    ax.set_xlabel('Date',fontsize=18)
    #plt.savefig('monthlyBalance.png',dpi=200)
    fig,ax2 = plt.subplots()
    mainDat['avgBalance'].cumsum().plot(title='Cumulative Water Balance',
                                        ylabel='cm of water',grid=True,ax=ax2,
                                        label='84% CIMIS ETo')
    mainDat_noMult['avgBalance'].cumsum().plot(label='Original CIMIS ETo',
                                        ylabel='cm of Water',grid=True,ax=ax2)
    ax2.legend()
    #plt.savefig('monthlyBalance_cumsum.png',dpi=200)


## Load the data
mainDat = load_data()
## Apply the ET multiplier
mainDat_noMult = mainDat.copy()
mainDat = apply_ET_mult(mainDat)
## Calculate the mass balances
mainDat_noMult = calculate_balance(mainDat_noMult)
mainDat = calculate_balance(mainDat)
## Create the orchard average monthly mass balance figure
create_figure(mainDat,mainDat_noMult)

#%%
###############################################################################
################# Recreate yearly figure for Hanni's paper ####################
###############################################################################
## Cut data to only includ erelevant years
mainDat = mainDat[mainDat.index<pd.to_datetime('09/01/2022')]
fig, ax = plt.subplots()
irrigation = mainDat[['NE1_I','NE2_I','SW1_I','SW2_I','NW_I','SE_I']].mean(axis=1).resample('12MS').sum()
irrigation.name = 'Irrigation'
ET = mainDat[['NE1_ET','NE2_ET','SW1_ET','SW2_ET','NW_ET','SE_ET']].mean(axis=1).resample('12MS').sum() * -1
ET.name = 'ET'
Precip = mainDat['Precip'].resample('12MS').sum()
Precip.name = 'Precipitation'
balanceDat = pd.concat([irrigation,ET,Precip],axis=1)

balanceDat[['ET','Irrigation','Precipitation']].plot(ax=ax,kind='bar',
                                    stacked=True,
                                    width=0.8,
                                    )
ax.set_ylabel('Mean water flux [cm]',fontsize=12)
ax.set_xlabel('Growing Season',fontsize=12)
ax.legend(loc='center right',
          bbox_to_anchor=[1.33, 0.5],
          fontsize=10)
ax.grid(visible=True,alpha=0.5,color='darkgray')
ax.set_title('Annual Water Mass Balance')
labelNew = [2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
labels = [item.get_text() for item in ax.get_xticklabels()]
for idx,k in enumerate(labels):
    labels[idx] = labelNew[idx]
ax.set_xticklabels(labels,rotation=60)

#%%
## Do the same thing but split by block and sum the water balance
fig, ax = plt.subplots()
NE1 = mainDat['Precip'] + mainDat['NE1_I'] - mainDat['NE1_ET']
NE1.name = 'NE1'
NE2 = mainDat['Precip'] + mainDat['NE2_I'] - mainDat['NE2_ET']
NE2.name = 'NE2'
SW1 = mainDat['Precip'] + mainDat['SW1_I'] - mainDat['SW1_ET']
SW1.name = 'SW1'
SW2 = mainDat['Precip'] + mainDat['SW2_I'] - mainDat['SW2_ET']
SW2.name = 'SW2'
NW = mainDat['Precip'] + mainDat['NW_I'] - mainDat['NW_ET']
NW.name = 'NW'
SE = mainDat['Precip'] + mainDat['SE_I'] - mainDat['SE_ET']
SE.name = 'SE'

dat = pd.concat([NE1,NE2,SW1,SW2,NW,SE],axis=1).resample('12MS').sum()
dat.plot(kind='bar',
         width=0.8,
         ax=ax,
         edgecolor='black',
         linewidth=0.7,)
labelNew = [2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
labels = [item.get_text() for item in ax.get_xticklabels()]
for idx,k in enumerate(labels):
    labels[idx] = labelNew[idx]
ax.set_xticklabels(labels,rotation=60)
ax.set_xlabel('Growing Season')
ax.set_ylabel('Mean water flux [cm]')
ax.set_title('Annual Water Mass Balance')
ax.legend(loc='center right',
          bbox_to_anchor=[1.22, 0.5],
          fontsize=10)

fig, ax2 = plt.subplots()

std = dat.std(axis=1)
dat.mean(axis=1).plot(kind='bar',
         width=0.8,
         ax=ax2,
         edgecolor='black',
         linewidth=0.7,
         yerr=std,
         ecolor='orange',
         capsize=4,)
labelNew = [2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
labels = [item.get_text() for item in ax2.get_xticklabels()]
for idx,k in enumerate(labels):
    labels[idx] = labelNew[idx]
ax2.set_xticklabels(labels,rotation=60)
ax2.set_xlabel('Growing Season')
ax2.set_ylabel('Orchard mean water flux [cm]')
ax2.set_title('Annual Water Mass Balance\n')
ax2.text(1.2,28,'Mean +/- standard deviation across blocks')


#%% Using neutron probe to calculate change in storage
## Try Open-ET PT-JPL
###############################################################################
##################### Water Balance via Neutron Probes ########################
###############################################################################
## Perform cumsum on water balance
## No longer doing cumulative sum but keeping variable name
mainDat_CS = mainDat.copy()#.cumsum()

## Plot the water balance data
fig, ax = plt.subplots(figsize=[15,10])
ax.plot(mainDat_CS.index,mainDat_CS['avgBalance'],
       label='Water Balance',color='red')
ax.grid()
#ax.set_title('Monthly Water Mass Balance\nMean +/- standard deviation across blocks',fontsize=18,loc='left')
ax.set_ylabel('Water Flux [cm]',fontsize=18)
ax.set_xlabel('DateTime',fontsize=18)
## Set the xlim if desired....
ax.set_xlim([pd.to_datetime('2018/03/06',format='%Y/%m/%d'),
             pd.to_datetime('2022/12/08',format='%Y/%m/%d')])

###############################################################################
########### Load the neutron probe data to calculate ΔS
###############################################################################
## Directory with the Bowman Data
DIR = '/Users/spencerjordan/Documents/bowman_data_analysis'
np_data = pd.read_csv(DIR+'/np2018_2022_Spencer_Update.csv')
## Some data cleaning
# Fixing some syntaxing
np_data.loc[np_data['Site']=='AL-1','Site'] = 'Al-1'
np_data.loc[np_data['Site']=='AL-2','Site'] = 'Al-2'
# Formatting site names
for site in range(1,9):
    np_data.loc[np_data['Site']==str(site),'Site'] = 'Al-'+str(site)
sites = np.unique(np_data['Site'])
depths = np.unique(np_data['Depth'])
np_data['date'] = pd.to_datetime(np_data['date'])
## Concerting water content to a depth of water
# Relate the station depth to a depth of soil being represented
## Could check sensitivity with water content
## --> Equation that takes the raw signal to a water content
## How sensitive is the recharge to how this is calculated
## Then we know where we need to pay more attention
## --> also could do this with the ET conversion
depthDict = {30:45,
             60:30,
             90:60,
             180:95,
             280:50}
## Multiplying the water content value by the depth each value represents
for depth in depths:
    np_data.loc[np_data['Depth']==depth,'water content'] = np_data.loc[np_data['Depth']==depth,'water content'] * (depthDict[depth])

## Creating a new DataFrame that holds the information organized by site
np_data_temp = np_data.copy()
npSites = pd.DataFrame()
for idx,site in enumerate(sites):
    dat = np_data_temp.loc[np_data_temp['Site']==site,:].groupby('date').mean()['water content'].diff()
    dat[0] = 0
    npSites[f'{site}'] = dat

## Group by date to get orchard average
wc = np_data.groupby('date').mean()
## Difference the data to calculate change in storage
wcDiff = wc.diff()
## Changes the first entry to be relative to zero instead of NaN
wcDiff['water content'][0] = 0
## Plot the change in storage
ax.plot(wcDiff.index,wcDiff['water content'],alpha=1,color='blue',
       label='Neutron Probe Differencing')


###############################################################################
############ Format the plot
###############################################################################
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1,7)))
ax.set_xticklabels(ax.get_xticks(), rotation = 45,fontsize=14)
ax.set_yticklabels(ax.get_yticks(), fontsize=14)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%b"))
ax.legend(fontsize=20)
## Set title
ax.set_title('Monthly Mass Balance and Neutron Probe ΔS',fontsize=22,loc='left')
#plt.savefig(f'{DIR}/np_data_water_balance_compare.png',dpi=200)

###############################################################################
######### Making spline curves and to difference the two curves 
###############################################################################
## mass balance spline
startDate = wcDiff.index[0]
mainDat_CS['sequential'] = mainDat_CS.index - startDate
mainDatSpline = mainDat_CS[mainDat_CS.index>pd.to_datetime('2018/03/06',format='%Y/%m/%d')]
mainDatSpline = mainDatSpline[mainDatSpline.index<pd.to_datetime('2022/12/08',format='%Y/%m/%d')]
mainDatSpline['sequential'] = [float(x.days) for x in mainDatSpline['sequential']]
mbSpline = spline(mainDatSpline['sequential'],mainDatSpline['avgBalance'])
xs = np.linspace(0,1800,1800)
## Doing the same for the NP data
wcDiff['sequential'] = wcDiff.index - startDate
wcDiff['sequential'] = [float(x.days) for x in wcDiff['sequential']]
wcSpline = spline(wcDiff['sequential'],wcDiff['water content'])

###############################################################################
######### Calculate recharge by subtracting the two spline curves
######### recharge == mass_balance - delta_storage
###############################################################################
predictedRecharge = mbSpline(xs) - wcSpline(xs)
rechargeIdx = [pd.to_timedelta(x,unit='days')+startDate for x in xs]
rch = pd.DataFrame({'recharge':predictedRecharge,
                    'DateTime':rechargeIdx})
rch = rch.set_index('DateTime').resample('1M').mean()

## Save for the HYDRUS result comparison
#rch.to_pickle('/Users/spencerjordan/Documents/Hydrus/python_scripts/massBalance_recharge.p')

###############################################################################
########## Plot predicted recharge
###############################################################################
fig,ax1 = plt.subplots()
"""
## IF PLOTTING WITH HYDRUS --> remove the width parameter
## Recharge predicted by Hydrus simulations
hydrusRecharge = pd.read_pickle('~/Documents/bowmanMassBalance/hydrus_recharge.p')
hydrusRecharge = hydrusRecharge.resample('1M').sum()
hydrusRecharge['0.5'].plot(ax=ax1,ylim=[-30,50],color='purple',
                           label='HYDRUS Predicted Recharge')
"""
ax1.bar(rch.index,rch['recharge'],label='Mass Balance Predicted Recharge',
        width=25)
ax1.set_xlim([pd.to_datetime('2018-04',format='%Y-%m'),pd.to_datetime(2022,format='%Y')])
ax1.axhline(0,c='black',ls='--')
ax1.set_title('Orchard Average Predicted Recharge')
ax1.set_xlim([pd.to_datetime('2018-05-01',format='%Y-%m-%d'),
             pd.to_datetime('2022-11-01',format='%Y-%m-%d')])
ax1.set_ylim([-10,10])
ax1.grid()
ax1.set_xlabel('Date')
ax1.set_ylabel('Recharge [cm]')
#ax1.legend()
plt.xticks(rotation=60, fontsize=8)

#%%
###############################################################################
######### Doing the analysis per site
###############################################################################

siteDict = {'NE1':[1],
            'NE2':[2],
            'SE':[7,8],
            'SW1':[],
            'SW2':[6],
            'NW':[3,4]}
## Getting a mean value in npSites for each block
blockMean = pd.DataFrame()
blockMean['NE1'] = npSites['Al-1']
blockMean['NE2'] = npSites['Al-2']
## Taking the average of sites 7 and 8    
blockMean['SE'] = [np.mean([x, npSites['Al-8'][idx]]) for idx,x in enumerate(npSites['Al-7'])]
## Using Al-6 for SW1 since there is no monitoring site there   
blockMean['SW1'] = npSites['Al-6']    
blockMean['SW2'] = npSites['Al-6']
## Taking the average of sites 3 and 4
blockMean['NW'] = [np.mean([x, npSites['Al-4'][idx]]) for idx,x in enumerate(npSites['Al-3'])]    
 
## Initialize the panel figure for each block
fig, ax = plt.subplots(2,3,figsize=[15,10])
fig.suptitle('Monthly Groundwater Recharge by Block, 0.78 Multiplier Applied to CIMIS ET',
             fontsize=19,y=0.98)
fig.supylabel('cm of Recharge',fontsize=17)
fig.supxlabel('Date',fontsize=17,y=0.04)
fig.tight_layout(pad=2.5)
a,b = 0,0

for site in siteDict:
    ## mass balance spline
    startDate = wcDiff.index[0]
    mainDat_CS['sequential'] = mainDat_CS.index - startDate
    mainDatSpline = mainDat_CS[mainDat_CS.index>pd.to_datetime('2018/03/06',format='%Y/%m/%d')]
    mainDatSpline = mainDatSpline[mainDatSpline.index<pd.to_datetime('2022/12/08',format='%Y/%m/%d')]
    mainDatSpline['sequential'] = [float(x.days) for x in mainDatSpline['sequential']]
    mbSpline = spline(mainDatSpline['sequential'],mainDatSpline[f'{site}_balance'])
    xs = np.linspace(0,1800,1800)
    ## Doing the same for the NP data
    diffSite = pd.DataFrame({'water content':blockMean[f'{site}']})
    diffSite['sequential'] = diffSite.index - startDate
    diffSite['sequential'] = [float(x.days) for x in diffSite['sequential']]
    diffSite = diffSite.fillna(0)
    wcSpline = spline(diffSite['sequential'],diffSite['water content'])
    ###########################################################################
    ######## Calculate recharge
    ###########################################################################
    predictedRecharge = mbSpline(xs) - wcSpline(xs)
    rechargeIdx = [pd.to_timedelta(x,unit='days')+startDate for x in xs]
    rch = pd.DataFrame({'recharge':predictedRecharge,
                        'DateTime':rechargeIdx})
    rch = rch.set_index('DateTime').resample('1M').mean()
    
    ## Label is weird to convey information about SW1, don't set legend for the other blocks
    ax[a,b].bar(rch.index,rch['recharge'],label='No Vadose Zone Data\nUsing SW2 Neutron Probe\nTrees Replanted in GS 2018',
            width=25)
    ax[a,b].set_xlim([pd.to_datetime('2018-04',format='%Y-%m'),pd.to_datetime(2022,format='%Y')])
    ax[a,b].set_ylim([-10,15])
    ax[a,b].grid()
    ax[a,b].set_title(f'{site}',fontsize=15)
    
    ## Format the date ticks
    ax[a,b].xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1)))
    ax[a,b].set_xticklabels(ax[a,b].get_xticks(),fontsize=12)
    ax[a,b].set_yticklabels(ax[a,b].get_yticks(), fontsize=12)
    ax[a,b].xaxis.set_major_formatter(mdates.DateFormatter("%b-%y"))
    if site == 'SW1':
        ax[a,b].legend()
    
    if b == 0:
        b = 1
    elif b == 1:
        b = 2
    else:
        b = 0
    if b == 0:
        a = a + 1





#%% Resampling monthly balance to match dates available for NP data
## I feel like we should match these dates so that data are more comparable with each other

mainDatNew = mainDat.reindex(wc.index)

dateRange = pd.date_range(pd.to_datetime('2018-03-06',format='%Y-%m-%d'),pd.to_datetime('2022-12-08',format='%Y-%m-%d'))

df = pd.DataFrame({'date':dateRange})
df = df.set_index('date')

df1 = pd.merge(df, mainDat, how='outer', left_index=True, right_index=True)
df1 = df1[df1.index>=pd.to_datetime('2018-03-06',format='%Y-%m-%d')]
df1 = df1[df1.index<=pd.to_datetime('2022-12-08',format='%Y-%m-%d')]


df2 = pd.merge(df, wc, how='outer', left_index=True, right_index=True)

df3 = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

df3 = df3[['water content','avgBalance']]

df3['avgBalance'].plot(kind='bar')

#%% Annual Balance using only water balance data
annualBalance = mainDat.resample('AS-OCT').sum()
annualBalance = annualBalance.loc[annualBalance.index<pd.Timestamp('2022/10/01'),:]
fig, ax = plt.subplots(figsize=[15,10])

annualBalance.plot(y=['NE1_balance','NE2_balance','NW_balance',
                                 'SW1_balance','SW2_balance','SE_balance'],
                        kind='bar',rot=45,
                        figsize=[13,10],ax=ax,width=0.8)

ax.grid()
ax.legend(fontsize=14)

labelNew = [2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
labels = [item.get_text() for item in ax.get_xticklabels()]
for idx,k in enumerate(labels):
    labels[idx] = labelNew[idx]
ax.set_xticklabels(labels,fontsize=14)
ax.set_title('Annual Water Mass Balance by Block',fontsize=18,loc='left')
ax.set_ylabel('Water Flux [cm]',fontsize=18)
ax.set_xlabel('DateTime',fontsize=18)

#plt.savefig('annualBalance.png',dpi=200)


#%% Annual balance using the recharge calcuted with water balance and neutron probe data

fig,ax3 = plt.subplots()
ax3.grid()

rch = rch[rch.index<pd.to_datetime('09/01/2022')]
annualMean = rch.resample('AS-OCT').sum()
ax3.bar(annualMean.index,annualMean.recharge,width=200)
plt.xticks(rotation=60,fontsize=8)
ax3.set_xlabel('Date')
ax3.set_ylabel('cm of Water')
ax3.set_title('Orchard Average Annual Recharge by Water Year')
ax3.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(10)))
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))

#%%
###############################################################################
############ Annual Balance for each field according to NP Data ###############
###############################################################################
## Create a comparable figure to the water balance annual balance
## Will need to average a few of the stations since more than 1 exist in some plots
## Same approach of finding total leaching per year, starting in October (water year)

npYearly = pd.DataFrame()
npYearly['date'] = np_data['date'].unique()

for site in sites:
    sub = np_data.loc[np_data['Site']==site].groupby('date').sum()
    sub[site] = sub['water content weighted'] * 280
    #sub['date'] = sub.index
    npYearly = pd.merge(npYearly,sub[site],how='outer',on='date')

npYearly.set_index('date',inplace=True)
npYearly = npYearly.resample('AS-OCT').mean()
npYearly = npYearly.diff()
npYearly = npYearly.dropna()

npYearly['NW'] = npYearly[['Al-4','Al-3']].mean(axis=1)
npYearly['NE2'] = npYearly['Al-2']
npYearly['NE1'] = npYearly['Al-1']
npYearly['SW2'] = npYearly['Al-6']
npYearly['SE'] = npYearly[['Al-7','Al-8']].mean(axis=1)
#npYearly['SW1'] = npYearly['Al-7']

fig, ax = plt.subplots(figsize=[15,10])

npYearly.plot(y=['NW','NE2','NE1','SW2','SE'],
              ax=ax, kind='bar', grid=True)

labelNew = [2019,2020,2021,2022]
labels = [item.get_text() for item in ax.get_xticklabels()]
for idx,k in enumerate(labels):
    labels[idx] = labelNew[idx]
ax.set_xticklabels(labels,fontsize=14,rotation=0)

ax.set_ylabel('Annual Water Flux [cm]',fontsize=14)
ax.set_xlabel('Date',fontsize=14)
ax.set_title('Neutron Probe Annual Water Balance by Block',fontsize=16)
ax.legend(fontsize=14,loc=3)

#%% Different Approach for annual balance using NP data

npYearly = np_data.groupby(['date','Site']).sum()
npYearly['water content'] = npYearly['water content weighted'] * 280
yearlyDiff = npYearly.groupby('date').mean()
yearlyDiff = yearlyDiff.resample('AS-OCT').sum()
## Take the difference of the dataframe
yearlyDiff = yearlyDiff.diff()
yearlyDiff = yearlyDiff.dropna()
fig, ax = plt.subplots(figsize=[15,10])
yearlyDiff['water content'].plot(ax=ax, kind='bar', grid=True)













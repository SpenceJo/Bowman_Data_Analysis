#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 14:18:21 2023

Compare CIMIS, Ranch System, and Kosana's flux tower ETo data

@author: spencerjordan
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

###################
## Load OpenET data
###################
openET = pd.read_csv('~/Documents/bowman_data_analysis/OPENET_SE_all_years.csv')
openET.set_index(pd.to_datetime(openET['DateTime']),inplace=True)

##########################
## Load Ranch Systems Data
##########################
rsET = pd.read_csv('~/Downloads/widget-graph-export-2.csv')
rsET['DateTime'] = rsET['Date'] + ' ' + rsET['Time']
rsET.set_index(pd.to_datetime(rsET['DateTime'],format='%Y-%m-%d %H:%M'),
               inplace=True)
rsET = rsET[rsET.index>=pd.to_datetime('2022-04-26')]

#######################
## Load Flux Tower Data
####################### 
fluxTower = pd.read_csv('~/Downloads/BowmanET_daily_2022_11_10.csv')
fluxTower.set_index(pd.to_datetime(fluxTower['date'],format='%m/%d/%Y'),inplace=True)
fluxTower['ETo'] = fluxTower['ETo']/10/2.54
#fluxTower['Kc'] = fluxTower['Kc'].fillna(np.nanmean(fluxTower['Kc']))
#fluxTower.loc[fluxTower['Kc']<0,'Kc'] = (np.nanmean(fluxTower['Kc']))

fluxTower['ETa'] = fluxTower['ETo'] * fluxTower['Kc']

##################
## Load CIMIS Data
##################
path = '~/Documents/Hydrus/python_scripts/cimis_daily.csv'
cimis = pd.read_csv(path)
cimis.set_index(pd.to_datetime(cimis['Date']),inplace=True)
cimis = cimis[cimis.index>min(rsET.index)]
cimis['ETo'] = cimis['ETo (mm)']/10/2.54
## Applying a multiplier to match up CIMIS data to Ranch System
cimis['ETo_adj'] = cimis['ETo'] * 0.78

#####################
## Plot ETo
#####################
fig,ax = plt.subplots()
rsET['Daily ETo (inch) (294)'].plot(ax=ax,label='Ranch System ETo',
          color='darkgreen')

fluxTower['ETo'].plot(ax=ax,label='Flux Tower ETo',
                      color='red',alpha=0.8)

cimis['ETo'].plot(ax=ax,label='CIMIS ETo',
                  color='blue',alpha=0.7)
openET['Ensemble ET'].plot(ax=ax,color='orange',alpha=0.7,label='openET ETa')

ax.set_ylabel('Inches of Water')
ax.set_title('ETo from Ranch System, CIMIS, and Flux Tower\nETa from OpenET')
ax.legend()
plt.savefig('ET_compare.png',dpi=200)

ax.set_xlim([pd.to_datetime('2022/04/01',format='%Y/%m/%d'),
             pd.to_datetime('2022/11/01',format='%Y/%m/%d')])

###############################################################################
## Resample the Ranch System data to match the daily data from CIMIS so that a 
## cumulative sum comparison can be made
rsET = rsET.resample('1d').mean()
ax.grid()



#%% Adjusting the ET with the Kc values we use in the model

def apply_Kc(ET_data,key,Kc='Shackle'):
    """
    Apply the Kc values to the ETo data to calculate ETa
    """
    print('Applying Kc Values....')
    ET_data['ETa_Kc'] = ET_data[key]
    ## Kc values based on time of year and tree age
    ## Values are from Doll and Shackel, 2015
    ## '_15' refers to first 15 days of month and '_16' refers to 16th day and onwards
    if Kc == 'Shackle':
        Kc_vals = {'1':0.40,
                   '2':0.41,
                   '3_15':0.55,
                   '3_16':0.67,
                   '4_15':0.75,
                   '4_16':0.84,
                   '5_15':0.89,
                   '5_16':0.98,
                   '6_15':1.02,
                   '6_16':1.07,
                   '7':1.11,
                   '8':1.11,
                   '9_15':1.08,
                   '9_16':1.04,
                   '10_15':0.97,
                   '10_16':0.88,
                   '11':0.69,
                   '12':0.43
                   } 
    elif Kc == 'itrc_norm':
        Kc_vals = {'1':0.77/0.73,
                       '2':0.9/2.12,
                       '3':1.68/4.01,
                       '4':2.75/5.56,
                       '5':5.96/7.32,
                       '6':6.39/7.58,
                       '7':6.7/7.98,
                       '8':5.7/6.76,
                       '9':4.32/5.39,
                       '10':2.82/3.47,
                       '11':0.45/1.05,
                       '12':0.87/0.99}
    elif Kc == 'itrc_wet':
        ############################
        ## ITRC Kc Values - wet year
        ############################
        Kc_vals = {'1':0.38/0.39,
                       '2':0.83/0.81,
                       '3':2.35/2.76,
                       '4':3.69/4.12,
                       '5':4.15/4.08,
                       '6':5.66/6.31,
                       '7':6.14/7.49,
                       '8':5.76/7.00,
                       '9':3.83/4.78,
                       '10':2.68/3.48,
                       '11':1.00/1.05,
                       '12':0.92/1.02}
    elif Kc == 'itrc_dry':
        ############################
        ## ITRC Kc Values - dry year
        ############################
        Kc_vals = {'1':0.64/0.77,
                        '2':1.31/1.24,
                        '3':2.11/2.78,
                        '4':3.78/5.34,
                        '5':5.8/7.14,
                        '6':6.08/7.23,
                        '7':6.31/7.73,
                        '8':5.27/6.38,
                        '9':4.32/5.23,
                        '10':2.47/3.62,
                        '11':0.89/1.26,
                        '12':0.76/1.36}
    else:
        print('****Invalid Choice for Kc*****')
        return
    for month in Kc_vals.keys():
        """
        Go through the climate data and turn ETo to ETa
        """
        ## Check for 15-day split
        if '_' not in month:
            sub = ET_data.loc[ET_data.index.month == int(month),key] * Kc_vals[month]
            ET_data.loc[ET_data.index.month == int(month),'ETa_Kc'] = sub
        else:
            m = month.split('_')[0]
            d = month.split('_')[-1]
            if d == '15':
                sub = ET_data.loc[(ET_data.index.month == int(m))
                                      & (ET_data.index.day <= int(d)),key] * Kc_vals[month]
                ET_data.loc[(ET_data.index.month == int(m))
                                      & (ET_data.index.day <= int(d)),'ETa_Kc'] = sub
            else:
                sub = ET_data.loc[(ET_data.index.month == int(m))
                                      & (ET_data.index.day > int(d)),key] * Kc_vals[month]
                ET_data.loc[(ET_data.index.month == int(m))
                                      & (ET_data.index.day > int(d)),'ETa_Kc'] = sub
    return ET_data


fluxTower_ETa = apply_Kc(fluxTower,'ETo')
cimis = apply_Kc(cimis,'ETo',Kc='itrc_dry')
rsET = apply_Kc(rsET,'Daily ETo (inch) (294)',Kc='itrc_wet')
model_ET = apply_Kc(cimis.copy(),'ETo',Kc='Shackle')
## Apply the flux tower's predicted Kc value to CIMIS data
cimis_flux_ETa = cimis.loc[cimis.index<=pd.to_datetime(fluxTower.index.max()),'ETo'] * fluxTower['Kc']

#%% Seperate plots for ETo and ETa
fig,ax2 = plt.subplots()
fig.suptitle('Cumulative ET Comparisons')

######################
## Initialize the plot
######################
ax2.set_ylabel('Cumulative ET [cm]')
(rsET['ETa_Kc']*2.54).cumsum().plot(ax=ax2,label='Ranch Systems ETc w/ ITRC dry Kc',legend=True)
#################################
## Plot original CIMIS + adjusted
#################################
(cimis['ETa_Kc']*2.54).cumsum().plot(ax=ax2,label='CIMIS ETc w/ ITRC dry Kc',legend=True,
                  alpha=0.7)
## Adjust the ETa
eta_adjust = 0.92
cimis['ETa_Kc_adj'] = cimis['ETa_Kc'] * eta_adjust
#(cimis['ETa_Kc_adj']*2.54).cumsum().plot(ax=ax2,label=f'{int(eta_adjust*100)}% CIMIS ETc',legend=True,
#                  alpha=0.7,
#                  ls='--')
## Adjusted used flux tower predicted Kc
(cimis_flux_ETa*2.54).cumsum().plot(ax=ax2,label='CIMIS ETc w/ FT Kc')
(model_ET['ETa_Kc']*2.54).cumsum().plot(ax=ax2,label='Model ETc (CIMIS with our Kc)')

##################################
## Plot the cumulative OpenET data
##################################
(openET.loc[openET.index>pd.to_datetime('2022-04-26'),'Ensemble ET']*2.54).cumsum().plot(ax=ax2,
                                                                                  label='OpenET ensemble ETa',
                                                                                  legend=True,
                                                                                  )
##############################
## Plot cumsum flux tower data
##############################
(fluxTower['ETa']*2.54).cumsum().plot(ax=ax2,
                               label='In-field flux tower ETa',
                               marker='*',
                               ms=2,
                               legend=True)
ax2.legend()
#ax2.legend(loc=5,bbox_to_anchor=(1.3, 0.25, 0.5, 0.5),fontsize=13)
ax2.grid()
ax2.grid()
































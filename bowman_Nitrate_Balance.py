#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:53:28 2022

Bowman N Mass Balances

@author: spencerjordan
"""

import pandas as pd
import matplotlib.pyplot as plt

## Load Manual Mass Balance Data
data = pd.read_csv('~/Documents/bowman_data_analysis/N_mass_balance/manual_mass_balance_2022.csv')

## Add a data column for NUE
data['NUE2'] = round((data['Uptake kg/ha']+data['Growth'])/data['Fert kg/ha'],2)

## Define Nitrogen Inputs, Outputs, and leaching subsets
inputs = data[['block','GS','Fert kg/ha','Min','Dep']].copy()
outputs = data[['block','GS','Uptake kg/ha','Growth','Denit']].copy()
leaching = data[['block','GS','leaching']].copy()

## Create the plot object, 3 rows with 9 columns
fig, ax = plt.subplots(3,10,figsize=(18,10))
## Add a title and xlabel applied to the whole figure, adjusting title position with 'y'
fig.suptitle('N Mass Balance',fontsize=22,y=1.005)
fig.supxlabel('Orchard Plot',fontsize=16)
## Helps with layout formatting, adding verticle and horitoztal padding
fig.tight_layout(w_pad=-2,h_pad=2)

################################ Inputs plot ##################################
# Create a plot for each year in the input data
for i,year in enumerate(inputs['GS'].unique()):
    ## Add a grid to the plot
    ax[0,i].grid(zorder=0)
    
    ## Create a dataset as a slice of the Inputs data based on the year of interest
    inputs2 = inputs[inputs['GS']==year].copy()
    
    ## Reordering x-values to match Hanni's Plots
    plots = ['NE','NW','SE','SW']
    df_sort = pd.DataFrame({'block' : plots})
    inputs2 = pd.merge(df_sort, inputs2,left_on='block',right_on='block',how='outer')
    inputs2['fert_bot'] = inputs2['Dep'] + inputs2['Min']
    ## Add a bar plot for the Dep, Min, and Fert variables, specifying the bottom
    ## of each as the starting point for the next --> stacking them
    ax[0,i].bar(inputs2['block'],inputs2['Dep'],label='Dep',zorder=3)
    ax[0,i].bar(inputs2['block'],inputs2['Min'],label='Min',
                bottom=inputs2['Dep'],zorder=3)
    ax[0,i].bar(inputs2['block'],inputs2['Fert kg/ha'],label='Fert',
                bottom=(inputs2['fert_bot']),zorder=3)
    
    ## Settting a limit for the y-axis
    ax[0,i].set_ylim([0,375])
    
    ## Create a unique title for each plot
    ax[0,i].set_title(f'{year}',fontsize=16)
    
    ## Change the fontsize of the x-tick labels
    ax[0,i].tick_params(axis='x', which='major', labelsize=13)
    
    # Turn off y-tick labels for all plots except the first
    if i:
        ax[0,i].set_yticklabels([])
   
## Set a ylabel for the first plot
ax[0,0].set_ylabel('N Inputs [kg/ha]',fontsize=16)
## Add a legend based on data from the last panel
ax[0,9].legend(loc=5,bbox_to_anchor=(1.2, 0.3, 0.5, 0.5),fontsize=13)
    
############################### Outputs Plot ##################################
for i,year in enumerate(outputs['GS'].unique()):
    ax[1,i].grid(zorder=0)
    outputs2 = outputs[outputs['GS']==year].copy()
    outputs2[['Denit','Growth','Uptake kg/ha']] = -1 * outputs2[['Denit','Growth','Uptake kg/ha']]
    plots = ['NE','NW','SE','SW']
    df_sort = pd.DataFrame({'block' : plots})
    outputs2 = pd.merge(df_sort, outputs2,left_on='block',right_on='block',how='outer')
    outputs2['crop_bot'] = outputs2['Denit'] + outputs2['Growth']
    
    ax[1,i].bar(outputs2['block'],outputs2['Denit'],label='Denit',zorder=3)
    ax[1,i].bar(outputs2['block'],outputs2['Growth'],label='Tree',
                bottom=outputs2['Denit'],zorder=3)
    ax[1,i].bar(outputs2['block'],outputs2['Uptake kg/ha'],label='Crop',
                bottom=outputs2['crop_bot'],zorder=3)
    ax[1,i].set_ylim([0,-375])
    ax[1,i].set_title(f'{year}',fontsize=16,y=0.99)
    ax[1,i].invert_yaxis()
    ax[1,i].tick_params(axis='both', which='major', labelsize=13)
    # Turn off y-ticks
    if i == 0:
        pass
    else:
        ax[1,i].set_yticklabels([])
    
ax[1,0].set_ylabel('N Outputs [kg/ha]',fontsize=16)
ax[1,9].legend(loc=5,bbox_to_anchor=(1.3, 0.3, 0.5, 0.5),fontsize=13)

############################## Leaching Plot ##################################
for i,year in enumerate(outputs['GS'].unique()):
    ax[2,i].grid(zorder=0)
    leaching2 = leaching[leaching['GS']==year].copy()
    ## Reordering to Match Hanni's Plots
    plots = ['NE','NW','SE','SW']
    df_sort = pd.DataFrame({'block' : plots})
    leaching2 = pd.merge(df_sort, leaching2,left_on='block',right_on='block',how='outer')
    leaching2['leaching'] = -1 * leaching2['leaching']
    ax[2,i].bar(leaching2['block'],leaching2['leaching'],zorder=3)
    ax[2,i].set_ylim([0,-375])
    ax[2,i].set_title(f'{year}',fontsize=16,y=0.99)
    ax[2,i].invert_yaxis()
    ax[2,i].tick_params(axis='both', which='major', labelsize=13)
    # Turn off y-ticks
    if i == 0:
        pass
    else:
        ax[2,i].set_yticklabels([])
        
ax[2,0].set_ylabel('Leaching [kg/ha]',fontsize=16)

## Save the final figure
plt.savefig('/Users/spencerjordan/Documents/bowman_data_analysis/N_mass_balance/combined_N_balance.png',
            dpi=250, bbox_inches='tight')















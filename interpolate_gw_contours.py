#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 22:33:33 2023

Look into 

@author: spencerjordan
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from scipy.interpolate import griddata
from shapely.geometry import box
import matplotlib.pyplot as plt


mw_coordinates = pd.read_csv('/Users/spencerjordan/Documents/Hydrus/mw_coordinates.csv')
mw_coordinates['MW#'] = np.arange(1,21)
mw_coordinates[['x','y','z']] = mw_coordinates[['x','y','z']]*0.3048
## Create spatial data out of mw location using california state plane datum
crs = "+proj=lcc +lat_1=37.06666666666667 +lat_2=38.43333333333333 +lat_0=36.5 +lon_0=-120.5 +x_0=2000000 +y_0=500000.0000000002 +ellps=GRS80 +datum=NAD83 +to_meter=0.3048006096012192 +no_defs"
MW = gpd.GeoDataFrame(mw_coordinates,
                     geometry=gpd.points_from_xy(x=mw_coordinates['x'],y=mw_coordinates['y'],crs=crs))

#Get WL depth measurements (ft)
hds = pd.read_csv('/Users/spencerjordan/Documents/bowman_data_analysis//BOW-MW-ALL-DATA-Compiled_working.csv')
#Get rid of nans
hds = hds[hds['NO3-N (mg/L)'].notna()]
hds = hds.merge(mw_coordinates, on='MW#', how='left')

## Set datetime index
hds['Sampling Date'] = pd.to_datetime(hds['Sampling Date'])
hds = hds.set_index('Sampling Date')
##############################################
## Create the spatial grid to interpolate over
##############################################
def create_grid(minx_grid,miny_grid,maxx_grid,maxy_grid,N_rows,N_cols):
    """
    Create the spatial grid to represent the top layer of the MODFLOW mesh
    """
    # Grid size
    grid_width = maxx_grid-minx_grid
    grid_height = maxy_grid-miny_grid
    # Cell size
    cell_width = grid_width/N_cols
    cell_height = grid_height/N_rows
    # Define grid origin as upper left grid corner
    origin_y = maxy_grid
    origin_x = minx_grid
    # Create grid cells
    grid_cells = []
    for i in range(N_rows): # For each row
        cell_origin_y = origin_y - i * cell_height # Calculate the current y coordinate
        for j in range(N_cols): # Create all cells in row
            cell_origin_x = origin_x + j * cell_width # Calculate the current x coordinate
            minx_cell = cell_origin_x
            miny_cell = cell_origin_y - cell_height
            maxx_cell = cell_origin_x + cell_width
            maxy_cell = cell_origin_y
            grid_cells.append(box(minx_cell, miny_cell, maxx_cell, maxy_cell)) # Store the new cell
    # Create a GeoDataFrame containing the grid
    grid = gpd.GeoDataFrame(geometry=grid_cells)
    return grid

def generate_grid(N_ROWS=117,N_COLS=91):
    """
    Generate the grid based on orchard boundary file and model discretization
    """
    ## Bounding box as geopandas dataframe --> Orchard boundary shapefile
    orch = gpd.read_file('/Users/spencerjordan/Documents/GW_modflow_Model-selected/Input data/Model boundary shapefile/Bowman_N_1404x1092.shp')
    orch_bounds = orch.total_bounds
    # Create the grid using the orchard bounding box
    grid = create_grid(orch_bounds[0],orch_bounds[1],orch_bounds[2],orch_bounds[3],N_ROWS,N_COLS)
    return grid

## DataFrame that will hold all the interpolated Z values
Z_df = pd.DataFrame()

grid = generate_grid()
method = 'cubic'
## For each date want to create a contour
for date in hds.index.unique():
    sub = hds[hds.index==date]
    ## Don't plot if not all wells were sampled on that date
    if len(sub) < 20:
        pass
    else:
        N = sub[['MW#','NO3-N (mg/L)','x','y']]
        points = np.vstack((N['x'],N['y'])).T
        X,Y = np.meshgrid(N['x'],N['y'])
        xi = np.vstack((grid.centroid.x,grid.centroid.y)).T
        Z = griddata(points,N['NO3-N (mg/L)'],xi,
                     method=method,
                     rescale=True)
        plt.imshow(Z.reshape(117,91))
        plt.show()
        Z_df[date] = Z
        
        ## Try Kriging from skgstat
        from skgstat import OrdinaryKriging,Variogram
        fig,ax = plt.subplots()
        V = Variogram(coordinates=points,
                      values=N['NO3-N (mg/L)'],
                      model='gaussian',
                      normalize=False)
        ok = OrdinaryKriging(V,
                             min_points=5,
                             max_points=40)
        kriging = ok.transform(xi)
        im = ax.imshow(kriging.reshape(117,91))
        #plt.colorbar(im,ax)
        
        ## Try kriging from pyKrige
        from pykrige import OrdinaryKriging as OK
        xi = np.vstack((grid.centroid.x,grid.centroid.y))
        krig = OK(xi[0],xi[1],N['NO3-N (mg/L)'],
                  variogram_model='linear')
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
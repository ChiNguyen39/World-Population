#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 11:47:37 2022

@author: kienguyen
"""
%matplotlib inline
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import cartopy.crs as ccrs
import cartopy

import folium
from folium import plugins
from folium.plugins import HeatMap

from numerize import numerize
import decimal
import io
from PIL import Image

# Set working path for this project
project_dir = os.getcwd()
dpi = 300
#%%
cities_population = pd.read_csv('/Users/kienguyen/Documents/Regis/MSDS/04. MSDS670_X40_Data Visualization/07. Week 7/Data/World Cities Database Population (OCT-2022).csv', sep=';',low_memory=False)
cities_population

#Drop columns that not necessary:
cities_population = cities_population.iloc[:,[1,2,3,6,7,-7,-6,-5,-4,-2,-1]]

# Fix 'Coordinate column name'
cities_population = cities_population.rename(columns={cities_population.columns[-1]:'Coordinate'})
cities_population = cities_population.rename(columns={cities_population.columns[-4]:'Digital Elevation Model'})

# Drop NA
cities_population = cities_population.loc[~cities_population.Coordinate.isna()]

# Convert to number
cities_population['Population'] = pd.to_numeric(cities_population['Population'])
cities_population['Elevation'] = pd.to_numeric(cities_population['Elevation'], errors='coerce')
cities_population['Digital Elevation Model'] = pd.to_numeric(cities_population['Digital Elevation Model'], errors='coerce')
cities_population.info()

# Fix number of Coordinate
cities_population['Coordinate'] = cities_population['Coordinate'].apply(lambda x: [coordinate for coordinate in x.split(',') if len(coordinate)>0])

#%%
# PLOT 1: Top 20 crowded cities
# Create data to plot
sort_20 = (cities_population
     .sort_values('Population', ascending=False)
     .reset_index(drop=True)
     .head(20)
     .sort_values('Population')
)
# Format population number for better reading
sort_20['Population'] = sort_20['Population'].astype(float)
for index,row in sort_20.iterrows():
    sort_20.loc[index, "Population"] = numerize.numerize(sort_20.loc[index, "Population"])

# plot the horizontal bar
fig, ax = plt.subplots(figsize = (18,12))

plot1 = ax.barh(sort_20.Name, sort_20.Population)
ax.set_title('Top Crowded cities', fontsize = 20)
ax.set_xlabel('Population', fontsize = 12)
plot1_name = 'Top20 crowded cities.png'
fig.savefig(project_dir + "/Chart/"+ plot1_name, dpi = dpi)

#%%
# PLOT 2: Mapping the cities onto map
# Split the longtitude and latitude
long_lat = cities_population['Coordinate'].apply(pd.Series)
long_lat.columns = ['Latitude','Longitude']

cities_population = cities_population.merge(long_lat, left_index=True, right_index=True)

cities_population = cities_population.drop(columns='Coordinate')

# Transform to geopandas
cities_population = gpd.GeoDataFrame(
        cities_population, 
        geometry=gpd.points_from_xy(cities_population.Longitude, cities_population.Latitude),
        crs='EPSG:4326'
)
# plot into map
ccrs.PlateCarree()
plot_df = cities_population.sort_values('Population', ascending=False).head(100)
# Scale for appropriate size of markers
plot_df['Population'] = plot_df['Population'] / 1e5 * 3
fig, ax = plt.subplots(figsize=(20,10))
ax = plt.axes(projection=ccrs.PlateCarree())
plot_df.plot(ax=ax, marker = 'o', markersize='Population', alpha=0.6, color='#1875cc')
ax.axis('off')
ax.coastlines()
ax.set_global()
ax.set_title('Top 100 Crowded cities', fontsize = 20)
plt.show()
plot2_name = 'Top 100 crowded cities.png'
fig.savefig(project_dir + "/Chart/"+ plot2_name, dpi = dpi)

#%%
# PLOT 3: Heatmap the cities with more than 1M population

map_mega_cities = folium.Map(location=[0, 0],
                    tiles = "cartodbpositron",
                    zoom_start = 2) 

# Create a List with the coordinates of all cities > 1M population
heat_data = [[row['Latitude'],row['Longitude']] for index, row in cities_population.loc[cities_population.Population > 1e6].iterrows()]

HeatMap(heat_data).add_to(map_mega_cities)

map_mega_cities.save(project_dir + "/Chart/"+ 'mega_cities_heatmap.html')
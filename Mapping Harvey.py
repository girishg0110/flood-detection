# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 20:43:08 2020

@author: giris
"""

import ee, folium, geehydro


#ee.Authenticate()
ee.Initialize()

# Load Sentinel-1
sentinel1 = ee.ImageCollection('COPERNICUS/S1_GRD')

# Houston's coordinates stored in a Point construct
houston_point = ee.Geometry.Point([-95.37, 29.76])
# # Filter by metadata properties -- we want IW and VV band
#8/1 to 8/16 is our before; 8/17 to 9/2 is our after
harvey_collect = sentinel1\
.filter(ee.Filter.date('2017-08-01', '2017-09-02'))\
.filterBounds(houston_point)\
.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))\
.select('VV')

# Filter by date {before, after}
before = harvey_collect.filterDate('2017-08-01', '2017-08-16').mosaic()
after = harvey_collect.filterDate('2017-08-17', '2017-09-02').mosaic()

# Threshold smoothed radar intensities to identify "flooded" areas.
SMOOTHING_RADIUS = 100
DIFF_UPPER_THRESHOLD = -3
diff_smoothed = after.focal_median(SMOOTHING_RADIUS, 'circle', 'meters') \
    .subtract(before.focal_median(SMOOTHING_RADIUS, 'circle', 'meters'))
diff_thresholded = diff_smoothed.lt(DIFF_UPPER_THRESHOLD)

# Display map
Map = folium.Map()
Map.centerObject(houston_point, 13)
Map.addLayer(before, {'min':-30,'max':0}, 'Before flood')
Map.addLayer(after, {'min':-30,'max':0}, 'After flood')
Map.addLayer(after.subtract(before), {'min':-10,'max':10}, 'After - before', 0)
Map.addLayer(diff_smoothed, {'min':-10,'max':10}, 'diff smoothed', 0)
Map.addLayer(diff_thresholded.updateMask(diff_thresholded), {'palette': '0000FF'}, 'flooded areas - blue')
#Map.save('Houston_Before-After_Harvey.html')
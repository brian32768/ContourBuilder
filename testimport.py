#!/usr/bin/env python
#!/c/Python27/ARcGISx6410.5/python
import sys, os
import subprocess

# This should happen in the environment not the script
# or I could make gdal.pth files
#sys.path.append(r'C:\Users/bwilson/GDAL/bin/gdal/python')
#sys.path.append(r'C:\Users/bwilson/GDAL/bin/gdal/python/osgeo')

from osgeo import gdal, gdal_array
from osgeo.gdalconst import *
from osgeo import ogr

os.chdir("/Users/bwilson/TrailPeople/Marketing/Vallejo_bluff_trail")
tif   = "raster_Project.tif"
layername = "contour"
shpfile = layername + ".shp"
interval = 100

raster_ds = gdal.Open(tif, GA_ReadOnly)

ogr_ds    = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(shpfile)
layer     = ogr_ds.CreateLayer(layername)

flddef = ogr.FieldDefn("ID",ogr.OFTInteger)
layer.CreateField(flddef)
flddef = ogr.FieldDefn("Contour", ogr.OFTReal)
layer.CreateField(flddef)
                
gdal.ContourGenerate(raster_ds.GetRasterBand(1), interval, 0, 
                     [], 0,0, # FixedLevelCount, NODATA settings
                     layer,
                     0, 1 # index of fid, index of felev
                     ) 
ogr_ds = None # Dereference to close shapefile
del ogr_ds

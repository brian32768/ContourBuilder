# ContourBuilder

I am trying to automate the contour build process. This script has
hardcodes to a DEM file and it was written for ArcGIS Desktop 10.5.

I wrote this code originally for TrailPeople.net, I get a lot of
requests there for high resolution contour layers. (Typically 6"
intervals.)

It's using ArcGIS with both Spatial Analyst and 3D Analyst extensions.
I tried doing a GDAL only version but failed apparently,
the code is still there but all commented out right now.

## What's here

### Main scripts

  build_contour.py   This runs from command line and generates a contour feature class from DEM.
  test_import.py     I believe this is just some GDAL test code I wrote.

### Some helpers live here

  raster.py
  utility.py






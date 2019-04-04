# ContourBuilder

I am trying to automate the contour build process. This script has
hardcodes to a DEM file and it was written for ArcGIS Desktop 10.5.

I wrote this code originally for TrailPeople.net; I get a lot of
requests there for high resolution contour layers. (Typically 6"
intervals.)

It's using ArcGIS with both Spatial Analyst and 3D Analyst extensions.
I tried doing a GDAL only version but failed apparently,
the code is still there but all commented out right now.

Step one is to come up with a TIFF file to feed it.
I usually go search in the NOAA data viewer in California
or DOGAMI in Oregon.

## What's here

### Main scripts

**build_contour.py** runs from command line and generates a contour feature class from DEM. Scroll to the bottom and look for these settings in the source file and edit them for your project,  
**source_folder** - the folder containing the DEM file  
**src_dem** - a TIF file containing elevation data  
**z_factor** - if the DEM is in meters, 3.28 converts output to feet.   Otherwise set it to 1.  
**geodatabase** - the gdb file in 'folder' (will be created if does not exist)  

You need to know the number for the projection, it's set to 103239 which is northern California

You can adjust the interval and index interval and reference scale and then call build_annotation as many times as you want with different settings; in the sample I build 3 layers with different settings.

test_import.py     I believe this is just some GDAL test code I wrote.

### Some helpers live here

**raster.py**  
**utility.py**

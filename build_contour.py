#!/c/Python27/ARcGISx6410.5/python -u
# -u forced unbuffered print so we can see progess messages
#
#  Build a contour layer and annotate it.
#
from __future__ import print_function
import arcpy
import arcpy.sa
import os
from glob import glob

from utility import copy_fc, create_geodatabase, create_feature_dataset, reproject
import raster

using_gdal = True
#sys.path.append(r'C:\Users/bwilson/GDAL/bin/gdal/python')
from osgeo import gdal, gdal_array
from osgeo.gdalconst import *
from osgeo import ogr
#import subprocess
#os.environ['GDAL_DATA'] = r'C:\Users/bwilson/GDAL/bin/gdal-data' # So it can find the PROJ4 CSV tables

arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")

def gdal_contour(tif,shp,interval):
    contour_bin = "gdal_contour"
    args = [contour_bin, "-i", str(interval), "-a", "Contour", tif, shp]
    rval = subprocess.check_output(args)
    """
    Oh how I wish I could use this code
    raster_ds = gdal.Open(self.dem_path, GA_ReadOnly)
    rasband1 = raster_ds.GetRasterBand(1)
    ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(rough_path)
    rough_shp = ogr_ds.CreateLayer(rough_fc)

    fid = ogr.FieldDefn("ID",ogr.OFTInteger)
    rough_shp.CreateField(fid)
                
    felev = ogr.FieldDefn("Contour", ogr.OFTReal)
    rough_shp.CreateField(felev)
                
    ftype = ogr.FieldDefn("Type", ogr.OFTInteger) # 1=intermediate 2=indexed
    rough_shp.CreateField(ftype)

    # See http://www.gdal.org/gdal__alg_8h.html#aceaf98ad40f159cbfb626988c054c085
    # ContourGenerate(Band srcBand, double contourInterval, double contourBase, 
    #    int fixedLevelCount, int useNoData, double noDataValue, 
    #    OGRLayerShadow dstLayer, int idField, int elevField,
    #    GDALProgressFunc callback = None, void callback_data = None) -> int
    gdal.ContourGenerate(rasband1, self.interval, 0, 
                         0, False, None, # # FixedLevelCount, NODATA settings
                         rough_shp, # dest layer
                         0, # index of fid
                         1 # index of felev
                         ) 
    raster_ds = None
    del raster_ds
    ogr_ds = None # Dereference to close shapefile
    del ogr_ds
    """
    return rval

class contour(object):

    sref_id = None
    sref_obj = None
    indem = None
    index_interval = interval = 40

    shortest = 20 # Shortest possible feature, little bumps and rocks should be dropped out
    bendiness = 20 # How curvy contours can be
    reference_scale = 5000 # Reference scale for annotation

    dem_path= ""
    z_factor = 1

    def __init__(self, sref_id, output_location, dem_path, z_factor):

        # Some tools will not take a string so get an object here.
        self.sref_id = sref_id
        self.sref_obj = arcpy.SpatialReference(sref_id)

        folder, gdb = os.path.split(output_location)
        self.output_location = output_location

        self.folder = folder
        self.workspace = os.path.join(folder, "workspace.gdb")
        create_geodatabase(self.workspace)

        self.z_factor = z_factor
        self.dem_path = self.smooth_dem(dem_path)

        return

    def smooth_dem(self, dem):
        """ Set up a raster to use as the source for our contours. 
        Generate TIF files so we can use GDAL tools if we want."""

        final_dem = os.path.join(self.folder, "raster_Smooth.tif")
        if not arcpy.Exists(final_dem):
            print("Reprojecting %s" % dem)
            dem_projected = os.path.join(self.folder, "raster_Project.tif")
            raster.reproject(dem, dem_projected, self.sref_obj)

            radius = 2
            print("Smoothing raster from '%s'" % dem_projected)
            result = arcpy.sa.FocalStatistics(dem_projected, arcpy.sa.NbrCircle(radius), "MEAN", "DATA")
            result.save(final_dem)

        return final_dem

    def build_lines(self):
        """ Build the contour lines """

        print("build lines at %d" % self.interval)

        # First build a rough contour (with many tiny features)
        # then copy it less those features to the final resting place.

        rough_fc = "contour_%d_Rough" % self.interval
        rough_path = os.path.join(self.folder, rough_fc + '.shp')

        shape_length = "SHAPE_Leng" # name in a shapefile

        if arcpy.Exists(rough_path):
            print("\tSkipping '%s'\n" % rough_path)
        else:
            # This creates a feature class that will have a field called "Type" to indicate
            # if a contour should be indexed or not

            if using_gdal:
                gdal_contour(self.dem_path,rough_path,self.interval)
                # Note that this file will not have the magic Shape_Leng field that ArcGIS creates.
                # but if you copy the fc with arcpy to the fgdb then it gets added!
            else:
                arcpy.ContourWithBarriers_3d(self.dem_path, rough_path, 
                                         "", # barrier fc
                                         "POLYLINES",
                                         "", # values file
                                         "", 
                                         "", #base
                                         self.interval, self.index_interval,
                                         "", # explicit contour list
                                         z_factor
                                         )

        interval_layer = "contour_%d" % self.interval
        interval_path = os.path.join(self.output_location, interval_layer)
        if not arcpy.Exists(interval_path):
            # Selection with length fails with GDAL generated shapefile so I am copying first then select and delete

            print("Copy contours frome shapefile to fgdb")
            copy_fc(rough_path, interval_path)

            print("\tDeleting features that are tiny from '%s'." % interval_layer)

            selection_layer = interval_layer + "_Layer"
            shape_length = arcpy.ValidateFieldName("Shape_Length", interval_path)
            arcpy.MakeFeatureLayer_management(interval_path, selection_layer, "\"%s\"<%d" % (shape_length,self.shortest), self.folder)
            arcpy.DeleteFeatures_management(selection_layer)

            try:
                arcpy.AddField_management(interval_path, "Type", "SHORT")
            except:
                print("Already have Type in '%s'" % interval_layer)
                pass

            contour = "Contour"
            selection_layer = interval_layer + "_INTERVAL_Layer"

            arcpy.MakeFeatureLayer_management(interval_path, selection_layer, "Mod(%s,%d)<>0" % (contour, self.index_interval))
            arcpy.CalculateField_management(selection_layer, "Type", 1, "PYTHON_9.3")

            selection_layer = interval_layer + "_INDEXED_Layer"
            arcpy.MakeFeatureLayer_management(interval_path, selection_layer, "Mod(%s,%d)=0"  % (contour, self.index_interval))
            arcpy.CalculateField_management(selection_layer, "Type", 2, "PYTHON_9.3")

        return

    def build_annotation(self):

        print("build annotation at %d" % self.interval)

        arcpy.env.workspace = self.workspace

        contour_fc = "contour_%d" % self.interval
        contour_path = os.path.join(self.output_location, contour_fc)
        contour_anno = contour_fc + "_Annotation"

        folder, geodatabase = os.path.split(self.output_location)

        # We break the rule here and rebuild the layer every time
        # If we don't then it will create a new class every time
        # with a number at the end 1,2,3... very annoying.
        dataset = os.path.join(self.output_location, "annotation_%d" % self.interval)
        if arcpy.Exists(dataset):
            arcpy.Delete_management(dataset)
        create_feature_dataset(dataset, self.sref_obj)

        output_layer = "Contours_%d" % self.interval
        print("Creating annotation.", contour_fc, dataset, self.reference_scale, output_layer)
        arcpy.ContourAnnotation_cartography(contour_path, dataset, "Contour", str(self.reference_scale), output_layer,
                                            "BROWN", "Type", "PAGE", "ENABLE_LADDERING")

        print("Creating contour layer file.")
        layerfile = os.path.join(folder, "contour_%d.lyr" % self.interval)
        if arcpy.Exists(layerfile):
            try:
                arcpy.Delete_management(layerfile)
            except Exception as e:
                print("Delete of '%s' failed, " % layerfile, e)

        arcpy.SaveToLayerFile_management(output_layer, layerfile, "RELATIVE", "CURRENT")

        return True

# ========================================================================

if __name__ == "__main__":
    # Because this script checks for existence of each object before rebuilding it, you should be able to
    # place an exit(0) ANYWHERE to test it up to that point and then re-run.
    # To get it to rebuild something you have to nuke the feature, this script WILL NOT overwrite existing things.

    # Elevation data
    source_folder = "D:\\TrailPeople\\Data_Repository\\CA\\NOAA\\Vallejo"
    src_dem = "Job343109_CA2010_coastal_DEM.tif"
    dem_path = os.path.join(source_folder, src_dem)
    z_factor = 3.28 # Convert NOAA meters to good old feet.

    # TODO Might want to do reproject and clip steps outside the class
    folder = "D:\\TrailPeople\\Marketing\\Vallejo_bluff_trail" 

    geodatabase = os.path.join(folder, "contour.gdb")
    create_geodatabase(geodatabase)

    c = contour(103239, # Nor Cal
                 geodatabase, dem_path, z_factor)

    c.index_interval = 5
    c.interval = 1
    c.reference_scale = 625
#    c.build_lines()
    c.build_annotation()

    c.index_interval = 10
    c.interval = 2
    c.reference_scale = 1250
#    c.build_lines()
    c.build_annotation()

    c.index_interval = 20
    c.interval = 4
    c.reference_scale = 2500
#    c.build_lines()
    c.build_annotation()

    exit(0)

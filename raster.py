#!/usr/bin/env python
#
#
from __future__ import print_function
import arcpy
import os

def reproject(inraster, outraster, sref):
    """ Reproject a raster. """

    if arcpy.Exists(outraster): return True

    print("Reprojecting\n\t'%s'\n\t'%s'" % (inraster, outraster))

    # NB ProjectRaster tool will not accept an object!
    arcpy.ProjectRaster_management(inraster, outraster, sref.exportToString(), "BILINEAR") 
    # what about cell size??? should be the same as the input. no need to specify.
    # might want to specify a transform???

    return True

def clip(raster, clip_fc):
    """ Clip the input raster with clip_fc and push the pixels out to output_raster. """
    #arcpy.Clip_management(
    return

# Unit tests would be good
if __name__ == "__main__":
    print("No tests here.")

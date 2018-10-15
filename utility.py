#!/usr/bin/env python
#
from __future__ import print_function
import arcpy
import os
from arcgisscripting import ExecuteError

def copy_fc(inf, outf):
    arcpy.CopyFeatures_management(inf, outf)
    return True

def create_geodatabase(location):
    """ Create the geodatabase if it does not exist. """
    if arcpy.Exists(location): return True
    try:
        path, fgdb = os.path.split(location)
        arcpy.CreateFileGDB_management(path, fgdb, "CURRENT")
    except ExecuteError:
        # This just means it exists
        pass
    except Exception as e:
        print(type(e))
        print(e)
    return True


def create_feature_dataset(dataset, sref):
    """ Create destination feature dataset if it does not exist. """

    location, fd = os.path.split(dataset)
    if arcpy.Exists(dataset):
        return True
    try:
        arcpy.CreateFeatureDataset_management(location,fd, sref)
        print("Dataset '%s' created in '%s'" % (fd, location))
    except Exception as e:
        print(e)
        return False
    return True


def reproject(src, dest, sref):
    """ Reproject a feature class """
    try:
        arcpy.Project_management(src, dest, sref)
    except Exception as e:
        print(e)
        return False
    return True

# That is all for now.

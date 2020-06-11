#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
#  licensing by GeoVille GmbH.
#
#
# Date created: 06.05.2017
# Date last modified: 09.06.2017
#
#
__author__ = "Christina Ludwig"
__version__ = "1.0"

# GUI for QGIS ---------------------------------------------------------------

##Optical-SAR Water Fusion =name
##Water Cycle Regime=group
##ParameterFile|path_watermasks_opt|Directory containing optical based water masks|True|False
#ParameterFile|path_watermask_opt_max|Potential water body mask|False|False
##ParameterFile|path_watermask_sar|SAR based water mask|False|False
##OutputDirectory|path_output|Output directory
##*ParameterString|start_date|Start date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterString|end_date|End date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True

# DEBUGGING PARAMETERS ------------------------------------------------------
# For debugging outside of QGIS set this flag to True
DEBUG = False

# IMPORTS ------------------------------------------------------------------------------
import os, sys
from osgeo import gdal, osr
import numpy as np
import fnmatch
import datetime as dt
import subprocess

if not DEBUG:
    from qgis.core import QgsProcessingException
    from processing.tools import dataobjects
    import qgis

import RSutils.RSutils as rsu

# FUNCTIONS -----------------------------------------------------------------------------------

def reclass_sar(watermask_sar):
    """
    Reclassifies a SAR based water mask so that water is marked by the value 1 and non-water is 0.

    :param watermask_sar: (nparray) SAR based watermask
    :return: (nparray) reclassified watermask
    """

    watermask_sar_reclass = np.where(watermask_sar == 1, 0, 1)
    watermask_sar_reclass = np.where(watermask_sar == 0, 1, watermask_sar_reclass)
    watermask_sar_reclass = np.where(np.isnan(watermask_sar), np.nan, watermask_sar_reclass)

    return(watermask_sar_reclass)

def fuse_watermasks(watermask_opt, watermask_opt_max, watermask_sar):
    """
    Fuses an optical and a sar based watermask.

    :param watermask_opt: (nparray) Optical based watermask
    :param watermask_opt_max: (nparray) Optical based maximum watermask derived from whole time series
    :param watermask_sar: (nparray) SAR based watermask
    :return: watermask_fused: (nparray) Fused watermask
    """

    # Create empty array for fused watermask
    fused_watermask = np.empty(watermask_opt.shape, dtype=np.byte)
    fused_watermask[:] = 255

    # Fusion rules
    fused_watermask = np.where(((watermask_sar == 1) & (watermask_opt_max == 1)) |
                               ((watermask_sar == 1) & (watermask_opt >= 0.8)), 1, watermask_opt)
    fused_watermask = np.where(np.isnan(watermask_opt) & ((watermask_opt_max == 0) & (watermask_sar == 0)), 0, fused_watermask)

    return fused_watermask

# MAIN ----------------------------------------------------------------------------------------

# Directory containing watermasks
if not os.path.exists(path_watermasks_opt):
    print "Invalid input parameter: 'Directory containing watermasks' not found: %s" % path_watermasks_opt
    raise QgsProcessingException("Invalid input parameter: 'Directory containing watermasks' "
                                         "not found: %s" % path_watermasks_opt)

# Directory containing watermasks
if not os.path.exists(path_output):
    print "Invalid input parameter: 'Output directory' not found: %s" % path_output
    raise QgsProcessingException("Invalid input parameter: 'Output directory' "
                                         "not found: %s" % path_output)

# Search for potential water mask
path_watermask_opt_max = fnmatch.filter(os.listdir(path_watermasks_opt), "*_potential_watermask.tif")
if len(path_watermasks_opt) == 0:
    if not DEBUG:
        raise QgsProcessingException("Invalid input parameter: Potential watermask not found within %s."
                                             % path_watermasks_opt)
else:
    path_watermask_opt_max = os.path.join(path_watermasks_opt, path_watermask_opt_max[0])

# File title
title = os.path.basename(path_watermasks_opt)
if title[:6] == "step5_":
    title = title[6:]

# Create output directories
path_output_watermasks = os.path.join(path_output, "step7_" + title + "_sar")
if not os.path.exists(path_output_watermasks):
    os.mkdir(path_output_watermasks)

# CHECK START AND END DATES --------------------------------------------------------------------------------------
if start_date != "":
    try:
        start_date = dt.datetime.strptime(start_date, "%Y%m%d")
    except:
        raise QgsProcessingException("Invalid input parameter: Format of 'Start date' is not valid.")
else:
    start_date = dt.datetime.strptime("19000101", "%Y%m%d")

if end_date != "":
    try:
        end_date = dt.datetime.strptime(end_date, "%Y%m%d")
    except:
        raise QgsProcessingException("Invalid input parameter: Format of 'End date' is not valid.")
else:
    end_date = dt.datetime.strptime("30000101", "%Y%m%d")

if end_date < start_date:
    raise QgsProcessingException("Invalid input parameters: 'Start date'  must be earlier than 'End date'.")

# START PROCESSING -----------------------------------------------------------------------------------------------

# Find optical water mask files
watermask_files = fnmatch.filter(os.listdir(path_watermasks_opt), "*water_mask.tif")
if len(watermask_files) == 0:
    if not DEBUG:
        raise QgsProcessingException("Invalid input parameters: 'Start date'  must be earlier than 'End date'.")
    else:
        print("Invalid input data: No optical water masks found.")
        sys.exit(1)

# Read optical maximum watermask as nparray
geotrans_opt, proj_str_opt = rsu.raster2array(path_watermask_opt_max)[1:3]

# SAR ---------------------------------------------------------------------------------------

# Check projection
source_sar = gdal.Open(path_watermask_sar)
proj_sar = osr.SpatialReference()
proj_sar.ImportFromWkt(source_sar.GetProjection())
pix_size_sar = source_sar.GetGeoTransform()[1]
proj_opt = osr.SpatialReference()
proj_opt.ImportFromWkt(proj_str_opt)

# Reproject SAR water mask if necessary
if not proj_sar.IsSame(proj_opt) or (geotrans_opt[1] != pix_size_sar):
    path_watermask_sar_reprojected = path_watermask_sar[:-4] + "_reprojected.tif"
    if not os.path.exists(path_watermask_sar_reprojected):
        if not DEBUG:
            feedback.setProgressText('Reprojecting SAR water mask ...')
        else:
            print("Reprojecting SAR water mask ...")
        cmd = ["gdalwarp", "-ot", "Byte", "-of", "GTiff", "-tr", str(geotrans_opt[1]), str(geotrans_opt[1]),
               "-overwrite", "-co", "COMPRESS=LZW", "-s_srs", proj_sar.ExportToProj4(), "-t_srs", proj_opt.ExportToProj4(),
               path_watermask_sar, path_watermask_sar_reprojected]
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            if not DEBUG:
                raise QgsProcessingException("Error: SAR water mask could not be reprojected. \n %s " % e)

    path_watermask_sar = path_watermask_sar_reprojected

    del proj_sar, proj_opt

# Extent of AOI
opt_watermask_files = [os.path.join(path_watermasks_opt, f) for f in watermask_files]
extent_AOI = rsu.getJointExtent(opt_watermask_files + [path_watermask_sar])
if extent_AOI is None:
    if not DEBUG:
        raise QgsProcessingException("Error: SAR water mask and optical water masks are not intersecting.")
    else:
        print("Error: SAR water mask and optical water masks are not intersecting." )
        sys.exit(1)

# Read SAR water mask
watermask_sar = rsu.raster2array(path_watermask_sar, AOI_extent=extent_AOI)[0]

# Reclassify SAR water mask
watermask_sar = reclass_sar(watermask_sar)

# Read optical maximum watermask as nparray
watermask_opt_max, geotrans_opt, proj_str_opt = rsu.raster2array(path_watermask_opt_max, AOI_extent=extent_AOI)

# Perform fusion for each optical water mask
for wm_file in watermask_files:

    if not DEBUG:
        feedback.setProgressText("Fusing water mask %s" % os.path.basename(wm_file))

    # Extract date
    idx_date = wm_file.find("_d") + 2
    watermask_date = dt.datetime.strptime(wm_file[idx_date:idx_date+8], "%Y%m%d")

    # If date is not within start and end date
    if watermask_date > end_date or watermask_date < start_date:
        continue

    # Read watermask as nparray
    watermask_opt, geotrans, proj = rsu.raster2array(os.path.join(path_watermasks_opt, wm_file), AOI_extent=extent_AOI)

    # Perform fusion
    fused_watermask = fuse_watermasks(watermask_opt, watermask_opt_max, watermask_sar)

    # Write to file
    path_output_file = os.path.join(path_output_watermasks, wm_file[:-4] + "_sar.tif")
    res = rsu.array2raster(fused_watermask, geotrans, proj, path_output_file, gdal.GDT_Float32, 255)
    if res != True:
        if not DEBUG:
            raise QgsProcessingException(res)
        else:
            print(res)
            sys.exit(1)
    else:
        if not DEBUG:
            try:
                dataobjects.load(path_output_file, os.path.basename(path_output_file), isRaster=True)
            except:
                dataobjects.load(path_output_file, os.path.basename(path_output_file))


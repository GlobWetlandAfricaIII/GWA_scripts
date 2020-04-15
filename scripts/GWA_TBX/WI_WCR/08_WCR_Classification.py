#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
#
# Date created: 09.06.2017
# Date last modified: 18.01.2018
#
#
__author__ = "Christina Ludwig"
__version__ = "1.0"

##Classification WCR= name
##Water Cycle Regime=group
##ParameterFile|path_watermasks|Directory containing water masks|True|False
##OutputDirectory|path_output|Output directory
##*ParameterString|start_date|Start date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterString|end_date|End date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterNumber|max_extent_thresh|Water frequency threshold for maximum water extent|0|100|10
##*ParameterNumber|min_extent_thresh|Water frequency threshold for minimum water extent|0|100|80

DEBUG = False


import os, sys
import numpy as np
import fnmatch
import gdal
from shutil import copyfile
import datetime as dt
import time

starttime = time.time()

if not DEBUG:
    from processing.core.GeoAlgorithmExecutionException import (
        GeoAlgorithmExecutionException,
    )
    from processing.tools import dataobjects

    here = os.path.dirname(scriptDescriptionFile)

qmlDir = os.path.join(here, "data", "qml")

import RSutils.RSutils as rsu

# Functions ------------------------------------------------------------------------------------------


def calculate_frequency(watermasks):
    """
    Calculates water occurrence and number of valid observations of a stack of water masks

    :param watermasks: (nparray) 3d np array with water masks
    :return:    occurrence (nparray) 2d array indicating the number of water occurrences
                valid_obs (nparray) 2d array indicating the number of observations
    """

    # Number of valid observations
    valid_obs = np.nansum(~np.isnan(watermasks), axis=0).astype("int8")

    # Number of water/wetness occurrences
    occurrence = np.nansum(watermasks, axis=0)

    # Set occurrence to np.nan where there are no observations
    occurrence = np.where(valid_obs == 0, np.nan, occurrence)

    return (occurrence, valid_obs)


# Check input parameters ------------------------------------------------------------------------------

if not os.path.exists(path_watermasks):
    if not DEBUG:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameters: 'Directory containing water masks' does not exist."
        )
    print(
        "Invalid input parameters: 'Directory containing water masks' does not exist."
    )

if not os.path.exists(path_output):
    if not DEBUG:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameters: 'Output directory' does not exist."
        )
    print("Invalid input parameters: 'Output directory' does not exist.")

title = os.path.basename(path_watermasks)
if title[:4] == "step":
    title = title[6:]

# Create output directory
path_output_classification = os.path.join(
    path_output, "step8_" + title + "_WCRclassification"
)
if not os.path.exists(path_output_classification):
    os.mkdir(path_output_classification)

if not DEBUG:
    feedback.setProgressText(path_output_classification)

# Check start and end dates ------------------------------------------------------------------------
if start_date != "":
    try:
        start_date = dt.datetime.strptime(start_date, "%Y%m%d")
    except:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(
                "Invalid input parameter: Format of 'Start date' is not valid."
            )
else:
    start_date = dt.datetime.strptime("19000101", "%Y%m%d")

if end_date != "":
    try:
        end_date = dt.datetime.strptime(end_date, "%Y%m%d")
    except:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(
                "Invalid input parameter: Format of 'End date' is not valid."
            )
else:
    end_date = dt.datetime.strptime("30000101", "%Y%m%d")

if end_date < start_date:
    raise GeoAlgorithmExecutionException(
        "Invalid input parameters: 'Start date'  must be earlier than 'End date'."
    )


# WATER occurrence and frequency =========================================================

# Search water masks
watermask_files = [
    os.path.join(path_watermasks, f)
    for f in fnmatch.filter(os.listdir(path_watermasks), "*_water_mask_sar.tif")
]
if not watermask_files:
    watermask_files = [
        os.path.join(path_watermasks, f)
        for f in fnmatch.filter(os.listdir(path_watermasks), "*_water_mask.tif")
    ]

# Check whether masks exist
if len(watermask_files) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("No water masks found")
    else:
        print("No water masks found.")
else:
    print("Found " + str(len(watermask_files)) + " water mask files.\n")
    if not DEBUG:
        feedback.setProgressText(
            "Found " + str(len(watermask_files)) + " water mask files.\n"
        )

# Get joint extent of all watermasks
joint_extent = rsu.getJointExtent(watermask_files)
geotrans, proj = rsu.raster2array(watermask_files[0], joint_extent)[1:3]


# CALCULATE WATER FREQUENCY ----------------------------------------------------------------------------------------

if not DEBUG:
    feedback.setProgressText("Calculating water frequency ...")

# Read in watermasks
watermasks = []
for wm_file in watermask_files:
    # Extract date of water mask from file name
    dateidx = wm_file.find("_d") + 2
    watermask_date = dt.datetime.strptime(wm_file[dateidx : dateidx + 8], "%Y%m%d")
    # Filter water mask files by dates
    if (start_date is None or (start_date <= watermask_date)) and (
        end_date is None or (end_date >= watermask_date)
    ):
        jointExt = rsu.getJointExtent(wm_file, AOIextent=joint_extent)
        watermask, geotrans = rsu.raster2array(wm_file, jointExt)[:2]
        if (
            watermask.shape[1] < joint_extent.ncol
            or watermask.shape[0] < joint_extent.nrow
        ):
            watermask = rsu.padArray(watermask, geotrans, joint_extent)
        watermasks.append(watermask)

# Make watermask stack
watermasks = np.array(watermasks)

# Calculate water frequency
water_occurrence, valid_obs = calculate_frequency(watermasks)
water_frequency = (water_occurrence / valid_obs) * 100.0

# CLASSIFICATION -----------------------------------------------------------------------------------

if not DEBUG:
    feedback.setProgressText("Writing classification to file ...")

# Minimum water extent
min_water_extent = np.where(water_frequency > min_extent_thresh, 1, 0)

# Maximum water extent
max_water_extent = np.where(water_frequency > max_extent_thresh, 1, 0)

# Export maps to file ===============================================================================

# Water frequency
file_name = title + "_number_of_observations"
dest = os.path.join(path_output_classification, file_name + ".tif")
res = rsu.array2raster(valid_obs, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

file_name = title + "_water_frequency"
dest = os.path.join(path_output_classification, file_name + ".tif")
res = rsu.array2raster(water_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + ".qml")
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# Load water frequency to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))

# Maximum water extent
file_name = title + "_maximum_water_extent"
dest = os.path.join(path_output_classification, file_name + ".tif")
res = rsu.array2raster(max_water_extent, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + ".qml")
copyfile(os.path.join(qmlDir, "maximum_extent.qml"), outfile_name)

# Load to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))

# Minimum water extent
file_name = title + "_minimum_water_extent"
dest = os.path.join(path_output_classification, file_name + ".tif")
res = rsu.array2raster(min_water_extent, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + ".qml")
copyfile(os.path.join(qmlDir, "minimum_extent.qml"), outfile_name)

# Load to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))

if not DEBUG:
    feedback.setProgressText("Water Cycle Regime classification done.\n")
else:
    print("Water Cycle Regime classification done.")

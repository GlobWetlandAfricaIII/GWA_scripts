
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

##Classification = name
##Wetland Inventory=group
##ParameterFile|path_masks|Directory containing water and wetness masks|True|False
##OutputDirectory|path_output|Output directory
##*ParameterString|start_date|Start date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterString|end_date|End date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterNumber|high_wetland_prob_thresh|WWPI threshold between high and medium wetland probability|0|100|50
##*ParameterNumber|low_wetland_prob_thresh|WWPI threshold between medium and low wetland probability|0|100|25

DEBUG = False

# test paths
if DEBUG:

    #path_watermasks = r"I:\temp\GWA_TBX_SE\SE_wat45_mmu3\fused_watermasks"
    path_masks = r"I:\WI\02_InterimProducts\WI_test\step5_SEwa45bs55sv55dv65mu3"
    #path_output = r"I:\temp\GWA_TBX_SE\SE_wat45_mmu3\fused_watermasks"
    path_output = r"I:\WI\02_InterimProducts\WI_test"
    start_date = ""
    end_date = ""
    high_wetland_prob_thresh = 40
    low_wetland_prob_thresh = 25
    here = ""

import os, sys
import numpy as np
import fnmatch
import gdal
from shutil import copyfile
import datetime as dt
import time

starttime = time.time()

if not DEBUG:
    from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
    from processing.tools import dataobjects
    here = os.path.dirname(scriptDescriptionFile)

qmlDir = os.path.join(here, 'data', 'qml')

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

if not os.path.exists(path_masks):
    if not DEBUG:
        raise GeoAlgorithmExecutionException("Invalid input parameters: 'Directory containing water masks' does not exist.")
    print("Invalid input parameters: 'Directory containing water masks' does not exist.")

if not os.path.exists(path_output):
    if not DEBUG:
        raise GeoAlgorithmExecutionException("Invalid input parameters: 'Output directory' does not exist.")
    print("Invalid input parameters: 'Output directory' does not exist.")

title = os.path.basename(path_masks)
if title[:4] == "step":
    title = title[6:]

# Create output directory
path_output_classification = os.path.join(path_output, "step8_" + title + "_WIclassification")
if not os.path.exists(path_output_classification):
    os.mkdir(path_output_classification)

if not DEBUG:
    progress.setText(path_output_classification)

# Check start and end dates ------------------------------------------------------------------------
if start_date != "":
    try:
        start_date = dt.datetime.strptime(start_date, "%Y%m%d")
    except:
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'Start date' is not valid.")
else:
    start_date = dt.datetime.strptime("19000101", "%Y%m%d")

if end_date != "":
    try:
        end_date = dt.datetime.strptime(end_date, "%Y%m%d")
    except:
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'End date' is not valid.")
else:
    end_date = dt.datetime.strptime("30000101", "%Y%m%d")

if end_date < start_date:
    raise GeoAlgorithmExecutionException("Invalid input parameters: 'Start date'  must be earlier than 'End date'.")


# WATER OCCURRENCE AND FREQUENCY
# =========================================================

# Search water masks
watermask_files = []
for f in fnmatch.filter(os.listdir(path_masks), "*_water_mask.tif"):
    f_path = os.path.join(path_masks, f)
    # check if sar fused water mask exists. if yes use that one instead.
    f_path_sar = os.path.join(path_masks, f[:-4] + "_sar.tif")
    if os.path.exists(f_path_sar):
        watermask_files.append(f_path_sar)
    else:
        watermask_files.append(f_path)

# Check whether masks exist
if len(watermask_files) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("No water masks found")
    else:
        print("No water masks found.")
else:
    print ("Found " + str(len(watermask_files)) + " water mask files.\n")
    if not DEBUG:
        progress.setText("Found " + str(len(watermask_files)) + " water mask files.\n")
        progress.setText("\n".join(watermask_files))

# Get joint extent of all watermasks
joint_extent = rsu.getJointExtent(watermask_files)
geotrans, proj = rsu.raster2array(watermask_files[0], joint_extent)[1:3]

# CALCULATE WATER FREQUENCY ----------------------------------------------------------------------------------------

if not DEBUG:
    progress.setText("Calculating water frequency ...")

# Read in watermasks
watermasks = []
for wm_file in watermask_files:

    # Extract date of water mask from file name
    dateidx = wm_file.find("_d") + 2
    watermask_date = dt.datetime.strptime(wm_file[dateidx:dateidx + 8], "%Y%m%d")
    # Filter water mask files by dates
    if (start_date is None or (start_date <= watermask_date)) and (end_date is None or (end_date >= watermask_date)):
        jointExt = rsu.getJointExtent(wm_file, AOIextent=joint_extent)

        # Water
        watermask, geotrans = rsu.raster2array(wm_file, jointExt)[:2]
        if watermask.shape[1] < joint_extent.ncol or watermask.shape[0] < joint_extent.nrow:
            watermask = rsu.padArray(watermask, geotrans, joint_extent)
        watermasks.append(watermask)

# Make watermask stack
watermasks = np.array(watermasks)

# Calculate water frequency
water_occurrence, valid_obs = calculate_frequency(watermasks)
water_frequency = (water_occurrence / valid_obs) * 100.


# WETNESS OCCURRENCE AND FREQUENCY
# =========================================================

# CALCULATE WETNESS FREQUENCY ----------------------------------------------------------------------------------------

if not DEBUG:
    progress.setText("Calculating wetness frequency ...")

# Wetness masks
wetmasks = []
dveg_masks = []
sveg_masks = []
soil_masks = []

for wm_file in watermask_files:

    # Extract date of water mask from file name
    dateidx = wm_file.find("_d") + 2
    watermask_date = dt.datetime.strptime(wm_file[dateidx:dateidx + 8], "%Y%m%d")
    # Filter water mask files by dates
    if (start_date is None or (start_date <= watermask_date)) and (end_date is None or (end_date >= watermask_date)):

        wetmask_fused = []

        # Dense vegetation wetness
        dveg_files = [os.path.join(path_masks, f) for f in
                      fnmatch.filter(os.listdir(path_masks), "*_d" + wm_file[dateidx:dateidx + 8] + "*_dveg_mask_sar.tif")]
        if not dveg_files:
            dveg_files = [os.path.join(path_masks, f) for f in
                          fnmatch.filter(os.listdir(path_masks),
                                         "*_d" + wm_file[dateidx:dateidx + 8] + "*_dveg_mask.tif")]
        if dveg_files:
            jointExt = rsu.getJointExtent(dveg_files[0], AOIextent=joint_extent)
            dveg_mask, geotrans_dveg = rsu.raster2array(dveg_files[0], jointExt)[:2]
            if dveg_mask.shape[1] < joint_extent.ncol or dveg_mask.shape[0] < joint_extent.nrow:
                dveg_mask = rsu.padArray(dveg_mask, geotrans_dveg, joint_extent)
            wetmask_fused.append(dveg_mask)
            dveg_masks.append(dveg_mask)
        else:
            print("No wetness mask for dense vegetation found for scene %s" % dt.datetime.strftime(watermask_date, "%Y-%m-%d"))

        # Sparse vegetation wetness
        sveg_files = [os.path.join(path_masks, f) for f in
                      fnmatch.filter(os.listdir(path_masks), "*_d" + wm_file[dateidx:dateidx + 8] + "*_sveg_mask_sar.tif")]
        if not sveg_files:
            sveg_files = [os.path.join(path_masks, f) for f in
                          fnmatch.filter(os.listdir(path_masks),
                                         "*_d" + wm_file[dateidx:dateidx + 8] + "*_sveg_mask.tif")]
        if sveg_files:
            jointExt = rsu.getJointExtent(sveg_files[0], AOIextent=joint_extent)
            sveg_mask, geotrans_sveg = rsu.raster2array(sveg_files[0], jointExt)[:2]
            if sveg_mask.shape[1] < joint_extent.ncol or sveg_mask.shape[0] < joint_extent.nrow:
                sveg_mask = rsu.padArray(sveg_mask, geotrans_sveg, joint_extent)
            wetmask_fused.append(sveg_mask)
            sveg_masks.append(sveg_mask)
        else:
            print("No wetness mask for sparse vegetation found for scene %s" % dt.datetime.strftime(watermask_date, "%Y-%m-%d"))

        # Bare soil wetness
        soil_files = [os.path.join(path_masks, f) for f in
                      fnmatch.filter(os.listdir(path_masks), "*_d" + wm_file[dateidx:dateidx + 8] + "*_soil_mask_sar.tif")]
        if not soil_files:
            soil_files = [os.path.join(path_masks, f) for f in
                          fnmatch.filter(os.listdir(path_masks),
                                         "*_d" + wm_file[dateidx:dateidx + 8] + "*_soil_mask.tif")]
        if soil_files:
            jointExt = rsu.getJointExtent(soil_files[0], AOIextent=joint_extent)
            soil_mask, geotrans_soil = rsu.raster2array(soil_files[0], jointExt)[:2]
            if soil_mask.shape[1] < joint_extent.ncol or soil_mask.shape[0] < joint_extent.nrow:
                soil_mask = rsu.padArray(soil_mask, geotrans_soil, joint_extent)
            wetmask_fused.append(soil_mask)
            soil_masks.append(soil_mask)
        else:
            print("No wetness mask for bare soil found for scene %s" % dt.datetime.strftime(watermask_date, "%Y-%m-%d"))

        # Fuse wetness masks
        if not wetmask_fused:
            print("No wetness masks found for %s" % dt.datetime.strftime(watermask_date, "%Y-%m-%d"))
            continue

        wetmask_fused = np.nanmax(np.array(wetmask_fused), axis=0)

        wetmasks.append(wetmask_fused)

if not DEBUG:
    progress.setText("Writing classification to file ...")

# Make watermask stack
wetmasks = np.array(wetmasks)
dveg_masks = np.array(dveg_masks)
sveg_masks = np.array(sveg_masks)
soil_masks = np.array(soil_masks)

# Calculate wet frequencies
wet_occurrence = calculate_frequency(wetmasks)[0]
wet_frequency = (wet_occurrence / valid_obs) * 100.

# Calculate wet dveg frequencies
dveg_occurrence = calculate_frequency(dveg_masks)[0]
dveg_frequency = (dveg_occurrence / valid_obs) * 100.
# Calculate wet sveg frequencies
sveg_occurrence = calculate_frequency(sveg_masks)[0]
sveg_frequency = (sveg_occurrence / valid_obs) * 100.
# Calculate wet soil frequencies
soil_occurrence = calculate_frequency(soil_masks)[0]
soil_frequency = (soil_occurrence / valid_obs) * 100.

# Dry frequency
dry_frequency = 100. - water_frequency - wet_frequency


# CLASSIFICATION -----------------------------------------------------------------------------------

# Water Wetness Presence Index
WWPI = water_frequency + (0.75 * wet_frequency)

# Permanent Water
permWater = np.where(water_frequency >= 80, 1, 0)

# Temporary Water
tempWater = np.where((dry_frequency <= 80) & (wet_frequency < 65) & (water_frequency < 80) & (water_frequency >= wet_frequency), 2, 0)  # & ((waterFreq > 0.25) & (waterFreq <= 0.8))

# Permanent Wet
permWet = np.where(wet_frequency >= 65, 3, 0)

# temporary Wet
tempWet = np.where((dry_frequency <= 80) & (wet_frequency < 65) & (water_frequency < 80) & (water_frequency < wet_frequency), 4, 0)  # & ((wetFreq > 0.25) & (wetFreq <= 0.75))

# Dry
noWater = np.where(dry_frequency > 80, 10, 0)

# wetland probability
WetHighProb = np.where((permWet > 0) | ( ((tempWater > 0 ) | (tempWet > 0)) & (WWPI >= high_wetland_prob_thresh)), 2, 0)
WetMedProb = np.where(((tempWater > 0) | (tempWet > 0)) & ((WWPI >= low_wetland_prob_thresh) & (WWPI < high_wetland_prob_thresh)), 3, 0)
WetLowProb = np.where((tempWet > 0) & (WWPI < low_wetland_prob_thresh), 4, 0)

# New Classification: 1 - Permanent Water, 2 - Wetland (high prob), 3 - Wetland (med prob), 4 - Wetland (low prob.)
WetProbClass = permWater + WetHighProb + WetMedProb + WetLowProb
WetProbClass = np.where(np.isnan(WWPI), np.nan, WetProbClass)


# Export maps to file ===============================================================================

# Number of observations
file_name = title + "_number_of_observations"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(valid_obs, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Water frequency
file_name = title + "_water_frequency"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(water_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# Load water frequency to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))

# Wetness frequency
file_name = title + "_wetness_frequency"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(wet_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# Load water frequency to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))


# DENSE VEGETATOIN --------------------------------------------------------------------
file_name = title + "_dveg_frequency"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(dveg_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# SPARSE VEGETATION ---------------------------------------
file_name = title + "_sveg_frequency"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(sveg_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# BARE SOIL
file_name = title + "_soil_frequency"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(soil_frequency, geotrans, proj, dest, gdal.GDT_Float32, -9999)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "water_wet_frequency.qml"), outfile_name)

# Classification
file_name = title + "_wetland_probability"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(WetProbClass, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# Legend file
outfile_name = os.path.join(path_output_classification, file_name + '.qml')
copyfile(os.path.join(qmlDir, "wetland_probability.qml"), outfile_name)

# Load water frequency to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))

# WWPI
file_name = title + "_WWPI"
dest = os.path.join(path_output_classification, file_name + '.tif')
res = rsu.array2raster(WWPI, geotrans, proj, dest, gdal.GDT_Byte, 255)
if res != True:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(res)
    else:
        print(res)
        sys.exit(1)

# qml file
outfile_name = os.path.join(path_output_classification, file_name+'.qml')
copyfile(os.path.join(qmlDir, "WWPI.qml"), outfile_name)

# Load water frequency to canvas
if not DEBUG:
    try:
        dataobjects.load(dest, os.path.basename(dest), isRaster=True)
    except:
        dataobjects.load(dest, os.path.basename(dest))


if not DEBUG:
    progress.setText('Wetland Inventory classification done.\n')
else:
    print('Wetland Inventory classification done.')


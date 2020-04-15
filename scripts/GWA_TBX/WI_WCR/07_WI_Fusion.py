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

##Optical-SAR Water and Wetness Fusion =name
##Wetland Inventory=group
##ParameterFile|path_masks_opt|Directory containing optical based water and wetness masks|True|False
##ParameterFile|path_water_freq_sar|SAR based water frequency|False|False
##ParameterFile|path_wet_freq_sar|SAR based wetness frequency
##OutputDirectory|path_output|Output directory
##ParameterString|start_date|Start date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##ParameterString|end_date|End date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##ParameterBoolean|wetness_fusion|Perform wetness fusion|True

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
    from processing.core.GeoAlgorithmExecutionException import (
        GeoAlgorithmExecutionException,
    )
    from processing.tools import dataobjects
    import qgis

import RSutils.RSutils as rsu

# FUNCTIONS -----------------------------------------------------------------------------------


def fuse_watermasks(watermask_opt, watermask_opt_max, watermask_sar):
    """
    Fuses an optical and a sar based watermask.

    :param watermask_opt: (nparray) Optical based watermask
    :param watermask_opt_max: (nparray) Optical based maximum watermask derived from whole time series
    :param watermask_sar: (nparray) SAR based watermask
    :return: watermask_fused: (nparray) Fused watermask
    """

    # Fusion rules
    fused_watermask = np.where(
        ((watermask_sar == 1) & (watermask_opt_max == 1))
        | ((watermask_sar == 1) & (watermask_opt >= 0.75)),
        1,
        watermask_opt,
    )
    # fused_watermask = np.where(np.isnan(watermask_opt) & (watermask_sar == 0), 0, fused_watermask)

    return fused_watermask


# MAIN ----------------------------------------------------------------------------------------

# Directory containing watermasks
if not os.path.exists(path_water_freq_sar):
    print "Invalid input parameter: 'SAR based water frequency' file not found: %s" % path_water_freq_sar
    raise GeoAlgorithmExecutionException(
        "Invalid input parameter: 'SAR based water frequency' "
        "file not found %s" % path_water_freq_sar
    )

# check if water frequency file exists
if not os.path.exists(path_wet_freq_sar) and wetness_fusion:
    print "Invalid input parameter: 'SAR based wetness frequency' file not found: %s" % path_wet_freq_sar
    raise GeoAlgorithmExecutionException(
        "Invalid input parameter: 'SAR based wetness frequency' "
        "file not found %s" % path_wet_freq_sar
    )

# check if wetness frequency file exists
if not os.path.exists(path_masks_opt):
    print "Invalid input parameter: 'Directory containing watermasks' not found: %s" % path_masks_opt
    raise GeoAlgorithmExecutionException(
        "Invalid input parameter: 'Directory containing watermasks' "
        "not found: %s" % path_masks_opt
    )

# Search for potential water mask
path_watermask_opt_max = fnmatch.filter(
    os.listdir(path_masks_opt), "*_potential_watermask.tif"
)
if len(path_masks_opt) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameter: Potential watermask not found within %s."
            % path_masks_opt
        )
else:
    path_watermask_opt_max = os.path.join(path_masks_opt, path_watermask_opt_max[0])

# File title
title = os.path.basename(path_masks_opt)
if title[:6] == "step5_":
    title = title[6:]

# Create output directories
path_output_masks = os.path.join(path_output, "step7_" + title + "_sar")
if not os.path.exists(path_output_masks):
    os.mkdir(path_output_masks)

# CHECK START AND END DATES --------------------------------------------------------------------------------------
if start_date != "":
    try:
        start_date = dt.datetime.strptime(start_date, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameter: Format of 'Start date' is not valid."
        )
else:
    start_date = dt.datetime.strptime("19000101", "%Y%m%d")

if end_date != "":
    try:
        end_date = dt.datetime.strptime(end_date, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameter: Format of 'End date' is not valid."
        )
else:
    end_date = dt.datetime.strptime("30000101", "%Y%m%d")

if end_date < start_date:
    raise GeoAlgorithmExecutionException(
        "Invalid input parameters: 'Start date'  must be earlier than 'End date'."
    )

# START PROCESSING -----------------------------------------------------------------------------------------------

# Find optical water mask files
watermask_files = fnmatch.filter(os.listdir(path_masks_opt), "*water_mask.tif")
if len(watermask_files) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(
            "Invalid input parameters: 'Start date'  must be earlier than 'End date'."
        )
    else:
        print ("Invalid input data: No optical water masks found.")
        sys.exit(1)

# Read optical maximum watermask as nparray
geotrans_opt, proj_str_opt = rsu.raster2array(path_watermask_opt_max)[1:3]

# SAR ---------------------------------------------------------------------------------------

# Check projection
source_sar = gdal.Open(path_water_freq_sar)
proj_sar = osr.SpatialReference()
proj_sar.ImportFromWkt(source_sar.GetProjection())
pix_size_sar = source_sar.GetGeoTransform()[1]
proj_opt = osr.SpatialReference()
proj_opt.ImportFromWkt(proj_str_opt)

# Reproject SAR water mask if necessary
if not proj_sar.IsSame(proj_opt) or (geotrans_opt[1] != pix_size_sar):

    # Reproject water frequency
    path_water_freq_sar_reprojected = path_water_freq_sar[:-4] + "_reprojected.tif"
    if not os.path.exists(path_water_freq_sar_reprojected):
        if not DEBUG:
            feedback.setProgressText("Reprojecting SAR water frequency ...")
        else:
            print ("Reprojecting SAR water frequency ...")
        cmd = [
            "gdalwarp",
            "-ot",
            "Byte",
            "-of",
            "GTiff",
            "-tr",
            str(geotrans_opt[1]),
            str(geotrans_opt[1]),
            "-overwrite",
            "-co",
            "COMPRESS=LZW",
            "-s_srs",
            proj_sar.ExportToProj4(),
            "-t_srs",
            proj_opt.ExportToProj4(),
            path_water_freq_sar,
            path_water_freq_sar_reprojected,
        ]
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError as e:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(
                    "Error: SAR water frequency could not be reprojected. \n %s " % e
                )

    path_water_freq_sar = path_water_freq_sar_reprojected

    # Reproject wetness frequency
    if wetness_fusion:
        path_wet_freq_sar_reprojected = path_wet_freq_sar[:-4] + "_reprojected.tif"
        if not os.path.exists(path_wet_freq_sar_reprojected):
            if not DEBUG:
                feedback.setProgressText("Reprojecting SAR wetness frequency ...")
            else:
                print ("Reprojecting SAR wet frequency ...")
            cmd = [
                "gdalwarp",
                "-ot",
                "Byte",
                "-of",
                "GTiff",
                "-tr",
                str(geotrans_opt[1]),
                str(geotrans_opt[1]),
                "-overwrite",
                "-co",
                "COMPRESS=LZW",
                "-s_srs",
                proj_sar.ExportToProj4(),
                "-t_srs",
                proj_opt.ExportToProj4(),
                path_wet_freq_sar,
                path_wet_freq_sar_reprojected,
            ]
            try:
                subprocess.check_call(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                if not DEBUG:
                    raise GeoAlgorithmExecutionException(
                        "Error: SAR wetness frequency could not be reprojected. \n %s "
                        % e
                    )

        path_wet_freq_sar = path_wet_freq_sar_reprojected

        del proj_sar, proj_opt

# Extent of AOI
opt_watermask_files = [os.path.join(path_masks_opt, f) for f in watermask_files]
extent_AOI = rsu.getJointExtent(opt_watermask_files + [path_water_freq_sar])
if extent_AOI is None:
    if not DEBUG:
        raise GeoAlgorithmExecutionException(
            "Error: SAR water mask and optical water masks are not intersecting."
        )
    else:
        print ("Error: SAR water mask and optical water masks are not intersecting.")
        sys.exit(1)

# Read SAR wetness frequency as nparray
if wetness_fusion:
    wet_freq_sar = rsu.raster2array(path_wet_freq_sar, AOI_extent=extent_AOI)[0]

# Read SAR water frequency as nparray
water_freq_sar = rsu.raster2array(path_water_freq_sar, AOI_extent=extent_AOI)[0]

# Read optical maximum watermask as nparray
watermask_opt_max, geotrans_opt, proj_str_opt = rsu.raster2array(
    path_watermask_opt_max, AOI_extent=extent_AOI
)

# mask sar water frequency by optical potential water mask
water_freq_sar_masked = np.where(watermask_opt_max == 1, water_freq_sar, np.nan)

# calculate mean of sar water frequency within potential water mask
mean_water_frequency = np.nanmean(water_freq_sar_masked)

# Create sar water mask
water_mask_sar = np.where(
    (water_freq_sar >= mean_water_frequency) & (watermask_opt_max == 1), 1, 0
)
water_mask_sar = np.where(np.isnan(watermask_opt_max), np.nan, water_mask_sar)

# Perform fusion for each optical water mask
for wm_file in watermask_files:

    # Extract date
    idx_date = wm_file.find("_d") + 2
    watermask_date = dt.datetime.strptime(wm_file[idx_date : idx_date + 8], "%Y%m%d")

    # If date is not within start and end date
    if watermask_date > end_date or watermask_date < start_date:
        continue

    if not DEBUG:
        feedback.setProgressText("Fusing water mask %s" % os.path.basename(wm_file))

    # Read watermask as nparray
    watermask_opt, geotrans, proj = rsu.raster2array(
        os.path.join(path_masks_opt, wm_file), AOI_extent=extent_AOI
    )

    # Perform fusion
    fused_watermask = fuse_watermasks(watermask_opt, watermask_opt_max, water_mask_sar)

    # Write to file
    path_output_file = os.path.join(path_output_masks, wm_file[:-4] + "_sar.tif")
    res = rsu.array2raster(
        fused_watermask, geotrans, proj, path_output_file, gdal.GDT_Float32, 255
    )
    if res != True:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(res)
        else:
            print (res)
            sys.exit(1)
    else:
        if not DEBUG:
            dataobjects.load(path_output_file, os.path.basename(path_output_file))

    if wetness_fusion:

        # Dense vegetation wetness mask
        wet_files_soil = [
            os.path.join(path_masks_opt, f)
            for f in fnmatch.filter(
                os.listdir(path_masks_opt),
                "*_d" + wm_file[idx_date : idx_date + 8] + "*_soil_mask.tif",
            )
        ]

        # Dense vegetation wetness mask
        wet_files_sveg = [
            os.path.join(path_masks_opt, f)
            for f in fnmatch.filter(
                os.listdir(path_masks_opt),
                "*_d" + wm_file[idx_date : idx_date + 8] + "*_sveg_mask.tif",
            )
        ]

        if wet_files_soil:

            if not DEBUG:
                feedback.setProgressText("Fusing wetness mask %s" % wet_files_soil[0])

            # Wetness mask
            if len(wet_files_soil) != 0:
                wet_mask_soil, geotrans_wet = rsu.raster2array(
                    wet_files_soil[0], extent_AOI
                )[:2]
            else:
                wet_mask_soil = np.zeros(shape=fused_watermask.shape)

            if len(wet_files_sveg) != 0:
                wet_mask_sveg, geotrans_wet = rsu.raster2array(
                    wet_files_sveg[0], extent_AOI
                )[:2]
            else:
                wet_mask_sveg = np.zeros(shape=fused_watermask.shape)

            # Fuse wetness masks by taking the maximum value
            wet_mask_opt = np.nanmax(np.array([wet_mask_soil, wet_mask_sveg]), axis=0)

            # Binary mask of weighted wetmask
            wet_mask_binary = np.where(
                (wet_mask_soil >= 0.75) | (wet_mask_sveg >= 0.75), 1, 0
            )
            wet_mask_binary = np.where(
                (watermask_opt >= 0.75) | np.isnan(wet_mask_opt),
                np.nan,
                wet_mask_binary,
            )

            # Mask sar water frequency by optical potential water mask
            # wet_freq_sar_masked = np.where(wet_mask_binary == 1, wet_freq_sar, np.nan)

            # plt.hist(wet_freq_sar_masked.ravel(), bins=np.asarray(range(0,100,5)), range=(0, 100))
            # Get threshold for SAR wet mask
            wet_sar_threshold = np.nanpercentile(wet_freq_sar, 90)

            # Create sar water mask
            wet_mask_sar = np.where(wet_freq_sar >= wet_sar_threshold, 1, 0)
            wet_freq_sar_water = np.where(wet_mask_sar == 1, wet_freq_sar, np.nan)

            # Rescale areas that are wet according to SAR wetness frequency from 0.75 to 1
            wet_freq_sar_water_scaled = rsu.rescale(wet_freq_sar_water)

            # Fuse optical and sar water masks
            wet_mask_fused = np.nanmax(
                np.array([wet_freq_sar_water_scaled, wet_mask_opt]), axis=0
            )

            # mask sar water frequency by optical potential water mask
            # wet_freq_sar_masked = np.where(wet_mask_binary == 1, wet_freq_sar, np.nan)

            # Set pixels that are classified as water to 0
            wet_mask_fused = np.where(fused_watermask >= 0.75, 0, wet_mask_fused)

            # Write to file
            path_output_file = os.path.join(
                path_output_masks, os.path.basename(wet_files_soil[0])[:-4] + "_sar.tif"
            )
            res = rsu.array2raster(
                wet_mask_fused, geotrans, proj, path_output_file, gdal.GDT_Float32, 255
            )

            if res != True:
                if not DEBUG:
                    raise GeoAlgorithmExecutionException(res)
                else:
                    print (res)
                    sys.exit(1)
            else:
                if not DEBUG:
                    dataobjects.load(
                        path_output_file, os.path.basename(path_output_file)
                    )

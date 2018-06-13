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

##Water and Wetness Indices=name
##Wetland Inventory=group
##ParameterFile|path_imagery|Directory containing imagery|True|False
##ParameterSelection|sensor|Sensor|Sentinel-2;Landsat 5/7/8|Sentinel-2
##ParameterSelection|AOI_type|Type of AOI|Shapefile;User defined extent;Joint extent of all scenes
##ParameterFile|path_AOI|Shapefile containing AOI (Area of Interest)
##ParameterExtent|extent_coordinates|User defined extent||True
##OutputDirectory|path_output|Output directory
##*ParameterString|tile_ID|Tile ID (Sentinel-2) or Path/Row (Landsat)||False|True|False
##*ParameterString|start_date|Start date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterString|end_date|End date (YYYYMMDD) - if left empty all available scenes will be used||False|True|True
##*ParameterSelection|calculate_wetness_indices|Spectral indices for ... |Wetland Inventory;Water Cycle Regime|Wetland Inventory

# DEBUGGING PARAMETERS ------------------------------------------------------
# For debugging outside of QGIS set this flag to True
DEBUG = False

# IMPORTS ------------------------------------------------------------------------------
import os, sys
from osgeo import gdal, osr
import numpy as np
import fnmatch
import datetime as dt
import zipfile

if not DEBUG:
    from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
    from processing.tools import dataobjects
    import qgis

# Load additional library (rsutils)
if DEBUG:
    sys.path.append(r"")
import RSutils.RSutils as rsu

# FUNCTIONS ------------------------------------------------------------------------------------

def calculate_indices_for_scene(scene, output_dir, bandNo, extent_AOI=None, WCRonly=False):
    """ Calculates spectral indices for a Sentinel or Landsat scene

    :param scene: Object of class 'Scene'
    :param output_dir: (string) Path to output directory
    :param bandNo: (list) List of spectral band numbers that are used for index calculations
    :param extent_AOI: (list) Parameters of extent of AOI
    :param calculate_wetness_indices: (boolean) If True water and wetness indices are calculated, if False only water indices
    :return:
    """

    NODATA = -9999

    # Check output directory
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_name = scene.sensorCode + "_" + scene.tileID + "_" + dt.datetime.strftime(scene.date, "%Y%m%d")

    # Read in bands with clouds masked out
    bands = []
    for b in bandNo:
        bands.append(scene.getBand(b, masked=True))
    bands = np.array(bands)

    # Check bands for invalid values and set them to NAN
    #invalid_pixels = np.nansum(np.isnan(bands), axis=0)
    #bands = np.where(invalid_pixels > 0, np.nan, bands).astype("float32")

    print("NDVI")
    dest = os.path.join(output_dir, "NDVI", output_name + "_NDVI.tif")
    if not os.path.exists(os.path.dirname(dest)):
        os.mkdir(os.path.dirname(dest))
    NDVI = ((bands[3] - bands[2]) / (bands[3] + bands[2])) * 5000. + 5000.
    if (NDVI.shape[1] < extent_AOI.ncol) or (NDVI.shape[0] < extent_AOI.nrow):
        NDVI = rsu.padArray(NDVI, scene.geotrans, scene.proj, extent_AOI)
    # Save to file
    res = rsu.array2raster(NDVI, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
    if res != True:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(res)
        else:
            print(res)
            sys.exit(1)
    del NDVI

    dest = os.path.join(output_dir, "NDWI", output_name + "_NDWI.tif")
    # if not os.path.exists(dest):
    print("NDWI")
    if not os.path.exists(os.path.dirname(dest)):
        os.mkdir(os.path.dirname(dest))
    NDWI = ((bands[1] - bands[3]) / (bands[1] + bands[3])) * 5000. + 5000.
    if (NDWI.shape[1] < extent_AOI.ncol) or (NDWI.shape[0] < extent_AOI.nrow):
        NDWI = rsu.padArray(NDWI, scene.geotrans, scene.proj, extent_AOI)
    # Save to file
    res = rsu.array2raster(NDWI, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
    if res != True:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(res)
        else:
            print(res)
            sys.exit(1)
    del NDWI

    dest = os.path.join(output_dir, "mNDWI", output_name + "_mNDWI.tif")
    # if not os.path.exists(dest):
    print("mNDWI")
    if not os.path.exists(os.path.dirname(dest)):
        os.mkdir(os.path.dirname(dest))
    MNDWI = ((bands[1] - bands[4]) / (bands[1] + bands[4])) * 5000. + 5000.
    if (MNDWI.shape[1] < extent_AOI.ncol) or (MNDWI.shape[0] < extent_AOI.nrow):
        MNDWI = rsu.padArray(MNDWI, scene.geotrans, scene.proj, extent_AOI)
    # Save to file
    res = rsu.array2raster(MNDWI, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
    if res != True:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(res)
        else:
            print(res)
            sys.exit(1)
    del MNDWI

    if not WCRonly:

        print("NDMI")
        dest = os.path.join(output_dir, "NDMI", output_name + "_NDMI.tif")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        NDMI = ((bands[3] - bands[4]) / (bands[3] + bands[4])) * 5000. + 5000.
        if (NDMI.shape[1] < extent_AOI.ncol) or (NDMI.shape[0] < extent_AOI.nrow):
            NDMI = rsu.padArray(NDMI, scene.geotrans, scene.proj, extent_AOI)
        # Save to file
        res = rsu.array2raster(NDMI, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del NDMI

        print("ND0206")
        dest = os.path.join(output_dir, "ND0206", output_name + "_ND0206.tif")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        ND0206 = ((bands[1] - bands[5]) / (bands[1] + bands[5])) * 5000. + 5000.
        if (ND0206.shape[1] < extent_AOI.ncol) or (ND0206.shape[0] < extent_AOI.nrow):
            ND0206 = rsu.padArray(ND0206, scene.geotrans, scene.proj, extent_AOI)
        # Save to file
        res = rsu.array2raster(ND0206, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del ND0206

        print("ND0406")
        dest = os.path.join(output_dir, "ND0406", output_name + "_ND0406.tif")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        ND0406 = ((bands[3] - bands[5]) / (bands[3] + bands[5])) * 5000. + 5000.
        if (ND0406.shape[1] < extent_AOI.ncol) or (ND0406.shape[0] < extent_AOI.nrow):
            ND0406 = rsu.padArray(ND0406, scene.geotrans, scene.proj, extent_AOI)
        # Save to file
        res = rsu.array2raster(ND0406, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del ND0406

        print("NMDI")
        dest = os.path.join(output_dir, "NMDI", output_name + "_NMDI.tif")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        NMDI = ((bands[3] - (bands[4] - bands[5])) / (bands[3] + (bands[4] - bands[5]))) * 10000.
        if (NMDI.shape[1] < extent_AOI.ncol) or (NMDI.shape[0] < extent_AOI.nrow):
            NMDI = rsu.padArray(NMDI, scene.geotrans, scene.proj, extent_AOI)
        # Save to file
        res =rsu.array2raster(NMDI, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del NMDI

        # Band lengths
        f_nir = 8300
        f_swir1 = 16500
        f_swir2 = 20180

        dest = os.path.join(output_dir, "ABDI1", output_name + "_ABDI1.tif")
        print("ABDI1")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        ABDI1 = (bands[3] * np.arctan((bands[3] - bands[4]) / (f_swir1 - f_nir)))
        if (ABDI1.shape[1] < extent_AOI.ncol) or (ABDI1.shape[0] < extent_AOI.nrow):
            ABDI1 = rsu.padArray(ABDI1, scene.geotrans, scene.proj, extent_AOI)
        res = rsu.array2raster(ABDI1, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del ABDI1

        print("ABDI2")
        dest = os.path.join(output_dir, "ABDI2", output_name + "_ABDI2.tif")
        if not os.path.exists(os.path.dirname(dest)):
            os.mkdir(os.path.dirname(dest))
        ABDI2 = (bands[3] * np.arctan((bands[3] - bands[5]) / (f_swir2 - f_nir)))
        if (ABDI2.shape[1] < extent_AOI.ncol) or (ABDI2.shape[0] < extent_AOI.nrow):
            ABDI2 = rsu.padArray(ABDI2, scene.geotrans, scene.proj, extent_AOI)
        res = rsu.array2raster(ABDI2, extent_AOI.getGeotrans(), extent_AOI.getProj(), dest, gdal.GDT_Int16, NODATA)
        if res != True:
            if not DEBUG:
                raise GeoAlgorithmExecutionException(res)
            else:
                print(res)
                sys.exit(1)
        del ABDI2

        return True

# INPUT PARAMETERS ----------------------------------------------------------------------


# Initiate QGIS progress bar
if not DEBUG:
    progress.setPercentage(0)

# CHECK INPUT PARAMETERS -------------------------------------------------------------------------------------------
if AOI_type == 0:
    if not path_AOI.endswith(".shp"):
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: 'Shapefile containing AOI' is not a "
                                                 "shapefile (must have ending .shp). Please specify the path to the "
                                                 "shapefile containing the AOI or choose a different type of AOI." )
        sys.exit(1)
    if not os.path.exists(path_AOI) :
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: 'Shapefile containing AOI' was not found. "
                                                 "Please specify the correct path to the shapefile or choose a "
                                                 "different type of AOI." )
        sys.exit(1)
elif AOI_type == 1:
    if extent_coordinates is None:
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: No user defined extent given. Please "
                                                 "select an extent or choose a different type of AOI." )
        sys.exit(1)


# Directory containing imagery
if not os.path.exists(path_imagery):
    print "Invalid input parameter: 'Directory containing imagery' not found: %s" % path_imagery
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Directory containing imagery' "
                                         "not found: %s" % path_imagery)

# Output directory
if not os.path.exists(path_output):
    print "Invalid input parameter: 'Output directory' not found: %s" % path_output
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Output directory' "
                                         "not found: %s" % path_output)

# Sensor
if sensor == 0:
    sensor = "Sentinel"
elif sensor == 1:
    sensor = "Landsat"

# Only use scenes from specified Landsat path/row or Sentinel 2 granule
if tile_ID == "":
    tile_ID = None

# Create output directories
path_vrt = os.path.join(path_output, "step3_VRTfiles")
if not os.path.exists(path_vrt):
    os.mkdir(path_vrt)
path_indices = os.path.join(path_output, "step3_indices")
if not os.path.exists(path_indices):
    os.mkdir(path_indices)

# SEARCH FOR SCENES AND METADATA FILES IN IMAGERY DIRECTORY -------------------------------------------------------
if sensor == "Sentinel":

    # Search for scene directories
    scene_dirs = rsu.search_scene_directories(path_imagery, "S2[AB]*")
    scene_dirs_IDs = [] # list with (scene path, scene ID) tuples

    # Extract scene ID from metadata file
    for i, sceD in enumerate(scene_dirs):
        metadatafiles = []
        try:
            if sceD.endswith(".zip"):
                zpfile = zipfile.ZipFile(sceD)
                metadatafiles = fnmatch.filter(zpfile.namelist(), "*/GRANULE/*/MTD_TL.xml")
                if len(metadatafiles) == 0:
                    metadatafiles = fnmatch.filter(zpfile.namelist(), "*/GRANULE/*/S2*.xml")
                    if len(metadatafiles) > 0:
                        scene_dirs_IDs += [[sceD, x[-10:-4]] for x in metadatafiles]
                else:
                    scene_dirs_IDs.append([sceD, None])
                del zpfile
            else:
                granuleDir = ""
                for (root, dirnames, filenames) in os.walk(sceD):
                    for d in fnmatch.filter(dirnames, "GRANULE"):
                        granuleDir = os.path.join(root, d)
                for d in os.listdir(granuleDir):
                    for f in fnmatch.filter(os.listdir(os.path.join(granuleDir,d)), "*.xml"):
                        metadatafiles.append(os.path.join(granuleDir, d,f))

                if len(metadatafiles) > 1:
                    scene_dirs_IDs += [[sceD, os.path.basename(x)[-10:-4]] for x in metadatafiles]
                else:
                    scene_dirs_IDs.append([sceD, None])

        except Exception as e:
            if not DEBUG:
                raise GeoAlgorithmExecutionException("Invalid input data: Invalid file in 'Directory "
                                                     "containing imagery': %s " % sceD)
            else:
                print("Invalid input data: Invalid file in 'Directory containing imagery': %s" % sceD)
                sys.exit(1)

else:
    # Search Landsat scene directories
    scene_dirs = rsu.search_scene_directories(path_imagery, "L[COTE]*")
    scene_dirs_IDs = [[sD, None] for sD in scene_dirs]

# Update progress bar
if not DEBUG:
    progress.setText("Searching for %s scenes in imagery directory ..." % sensor)

# CREATE SCENES OBJECTS FROM FOUND SCENE DIRECTORIES -------------------------------------------------------------
scenes = []
for sD in scene_dirs_IDs:

    # Update progress bar
    if not DEBUG:
        progress.setText("\n%s - %s" % (sD[0], sD[1]))

    try:
        # Create scene objects
        if sensor == "Landsat":
            new_scene = rsu.LandsatScene(sD[0], ID=sD[1])
        elif sensor == "Sentinel":
            new_scene = rsu.SentinelScene(sD[0], ID=sD[1])

        if tile_ID is None or (tile_ID in new_scene.tileID):
            scenes.append(new_scene)
        else:
            if not DEBUG:
                progress.setText("Scene not included: Tile ID doesn't match %s." % tile_ID)

    except IOError as e:
        if not DEBUG:
            progress.setText("WARNING: Scene is skipped. (%s)" % (e))
        else:
            print("WARNING: Scene skipped. (%s)" % (e))
    except Exception as e:
        if not DEBUG:
            progress.setText("ERROR: Scene is skipped. (%s)" % (e))
        else:
            print("ERROR: Scene is skipped. (%s)" % e)

# Raise error if no scenes are valid
if len(scenes) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("No %s scenes found that match the selection criteria. "
                                             "Adjust the selection parameters." % sensor)
    else:
        print "No %s scenes found that match the selection criteria. Adjust the selection parameters." % sensor
        sys.exit(1)

# CHECK START AND END DATES --------------------------------------------------------------------------------------

if start_date == "":
    start_date = min([sce.date for sce in scenes])
else:
    try:
        start_date = dt.datetime.strptime(start_date, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'Start date' is not valid.")

if end_date == "":
    end_date = max([sce.date for sce in scenes])
else:
    try:
        end_date = dt.datetime.strptime(end_date, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'End date' is not valid.")

if end_date < start_date:
    raise GeoAlgorithmExecutionException("Invalid input parameters: 'Start date'  must be earlier than 'End date'.")

scenes = rsu.filter_scenes_by_date(scenes, start_date, end_date)

# Raise error if no valid scenes are left
if len(scenes) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("No %s scenes found within the given time period. "
                                             "Adjust the start and end date." % sensor)
    else:
        print "No %s scenes found within the given time period. Adjust the start and end date." % sensor
        sys.exit(1)

# GET EXTENT OF AOI -------------------------------------------------------------------------------------------
# 3 options: shapefile, user defined extent, minimum joint extent of all valid scenes
if AOI_type == 0: # 1. AOI defined by shapefile
    exRaster = scenes[0].files[-1] # use swir2 bands as reference for geotransformation
    extent_AOI = rsu.convertShapeExtentToRasterExtent(path_AOI, exRaster)
    if extent_AOI is None:
        if not DEBUG:
            raise GeoAlgorithmExecutionException("Invalid input parameter: Shapefile contains more than one "
                                                 "polygon or AOI does not intersect with input scenes.")
        sys.exit(1)
elif AOI_type == 1: # 2. user defined extent in canvas
    extent_coordinates = [float(coord) for coord in extent_coordinates.split(",")]
    if not DEBUG:
        proj_canvas_wkt = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs().toWkt()
    # Create extent object from coordinates given by user in canvas
    proj_canvas = osr.SpatialReference()
    proj_canvas.ImportFromWkt(proj_canvas_wkt)
    extent_AOI = rsu.Extent(ulX=extent_coordinates[0], ulY=extent_coordinates[3], lrX=extent_coordinates[1],
                            lrY=extent_coordinates[2], proj=proj_canvas)
    extent_AOI.convertToRasterExtent(scenes[0])

    if extent_AOI is None:
        if not DEBUG:
            progress.setText("Invalid input parameter: User defined extent is invalid.")
        sys.exit(1)

    # Create folder where user defined extents are stored as shapefiles
    path_output_extents = os.path.join(path_output, "user_defined_extents")
    if not os.path.exists(path_output_extents):
        os.mkdir(path_output_extents)
    extent_name = "userDefinedExtent_" + dt.datetime.today().strftime("%Y%m%d-h%Hm%M")
    # Write to shapefile
    res = extent_AOI.save_as_shp(path_output_extents, extent_name)
    if res != True:
        if not DEBUG:
            raise GeoAlgorithmExecutionException(res)
        else:
            print(res)
            sys.exit(1)

    # Load shapefile with user defined extent to canvas
    if not DEBUG:
        print(os.path.join(path_output_extents, extent_name + ".shp"))
        dataobjects.load(os.path.join(path_output_extents, extent_name+".shp"), extent_name)

else: # 3. minimum joint extent of all scenes
    exBands = [sce.files[-1] for sce in scenes] # use swir2 bands as reference for geotransformation
    extent_AOI = rsu.getJointExtent(exBands)

    if extent_AOI is None:
        if not DEBUG:
            progress.setText("Invalid input data: Extent of AOI is invalid. "
                             "Check if all scenes overlap each other.")
        else:
            print("Invalid input data: Extent of AOI is invalid. Check if all scenes overlap each other.")
        sys.exit(1)

# Check AOI size -------------------------------------------------------------------------------------------------
AOI_size = extent_AOI.ncol * extent_AOI.nrow
if AOI_size > 5490**2:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("AOI exceeds maximum size. Only AOIs smaller than one Sentinel-2 "
                                             "granule may be processed. Please specify smaller extent.")
    else:
        print("AOI exceeds maximum size, which is one Sentinel-2 granule. "
                                             "Please specify smaller extent.")
    sys.exit(1)

# CHECK IF ALL SCENES INTERSECT THE AOI EXTENT -------------------------------------------------------------------
scenes_within_extent = []
for sce in scenes:
    try:
        sce.updateExtent(extent_AOI)
    except RuntimeWarning as e:
        print("%s not within AOI." % sce.ID)
        if not DEBUG:
            progress.setText("%s not within AOI." % sce.ID)
        continue

    # Check whether scene has enough valid pixels within AOI
    # sce.calcCloudCoverage()
    # if sce.cloudy > max_cloud_cover:
    #     print "Cloud coverage too high. Scene is skipped."
    #     if not DEBUG:
    #         progress.setText("Cloud coverage too high. Scene is skipped.")
    #     continue

    scenes_within_extent.append(sce)
    sce.createVRT(path_vrt)
    #if not DEBUG:
    #    dataobjects.load(sce.VRTfile, os.path.basename(sce.VRTfile))

# Raise error if no valid scenes are within AOI
scenes = scenes_within_extent
if len(scenes) == 0:
    if not DEBUG:
        raise GeoAlgorithmExecutionException("Invalid input data: "
                                             "No %s scenes found that match the selection criteria." % sensor)
        sys.exit(1)
    else:
        print "Invalid input data: No %s scenes found that match the selection criteria." % sensor

if not DEBUG:
    progress.setPercentage(10)
    progress.setText("\nFound %s valid %s scenes for processing. "
                     "\nStarting calculation of spectral indices ..." % (len(scenes), sensor))

#  CALCULATION OF SPECTRAL INDICES ------------------------------------------------------------------------------
for i, sce in enumerate(scenes):

    # Update progress bar
    if not DEBUG:
        progress.setText("%s" % os.path.basename(sce.ID))

    # Calculation of indices
    try:
        if sensor == "Sentinel":
            calculate_indices_for_scene(sce, path_indices, [1, 2, 3, 7, 9, 10], extent_AOI, calculate_wetness_indices)
        elif sensor == "Landsat":
            calculate_indices_for_scene(sce, path_indices, [1, 2, 3, 4, 5, 6], extent_AOI, calculate_wetness_indices)
    except IOError as e:
        print("Error while calculating spectral indices: %s " % e)


    # Update progress bar
    if not DEBUG:
        state = ((i + 1.) / len(scenes)) * 90
        progress.setPercentage(state)

# MERGE SCENES FROM SAME DATE TO VRT FILE ----------------------------------------------------------------

# Get all dates from scenes
dates = [sce.date for sce in scenes]
unique_dates = set(dates)
index_names = os.listdir(path_indices)

for date in unique_dates:

    for index in index_names:
        index_files = [os.path.join(path_indices, index, f) for f in fnmatch.filter(
            os.listdir(os.path.join(path_indices, index)), "*" + dt.datetime.strftime(date, "%Y%m%d") + "*.tif")]

        if len(index_files) == 0:
            print("No indices found for %s" % dt.datetime.strftime(date, "%Y%m%d"))
            continue

        sensor_code = os.path.basename(index_files[0])[:3]
        vrt_file_name = os.path.join(path_indices, index, sensor_code + "_" +
                                         dt.datetime.strftime(date, "%Y%m%d") + "_" + index + ".vrt")

        try:
            rsu.createVRT(index_files, vrt_file_name, separate=False)
        except Exception as e:
            if not DEBUG:
                progress.setText("ERROR: %s" % e)
            else:
                print e

        if not DEBUG and index == "NDWI":
            try:
                dataobjects.load(vrt_file_name, os.path.basename(vrt_file_name), isRaster=True)
            except:
                dataobjects.load(vrt_file_name, os.path.basename(vrt_file_name))

# Update progress bar
if not DEBUG:
    progress.setPercentage(100)


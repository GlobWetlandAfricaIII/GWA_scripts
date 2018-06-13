#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
#
# Date created: 06.05.2017
# Date last modified: 09.06.2017
#
#
__author__ = "Christina Ludwig"
__version__ = "1.0"


##Filter SAR water and wetness frequencies=name
##Wetland Inventory=group
##ParameterFile|inDir|Directory containing SAR based water and wetness frequencies|True|False
##ParameterBoolean|water|Filter water frequencies
##ParameterBoolean|wetness|Filter wetness frequencies
##OutputDirectory|path_output|Output directory
debug = False



from osgeo import gdal
import os
import fnmatch
import time

if not debug:
    from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
    import cv2

# Functions --------------------------------------------------------
def writeFile(filename,geotransform,geoprojection,data):
    (x,y) = data.shape
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    dst_datatype = gdal.GDT_Byte
    dst_ds = driver.Create(filename,y,x,1,dst_datatype)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(geoprojection)
    return 1

# -------------------------------------------------------------------

if not water and not wetness:
    if not debug:
        raise GeoAlgorithmExecutionException("Invalid input parameter: At least one of the parameters 'Water' or 'Wetness' must be activated.")

# Check input directory
if not os.path.exists(inDir):
    if not debug:
        raise GeoAlgorithmExecutionException("Invalid input parameter: 'Directory containing SAR files' does not exist.")
        sys.exit(1)

# Output path
if not os.path.exists(path_output):
    if not debug:
        raise GeoAlgorithmExecutionException("Invalid input parameter: 'Output directory' does not exist.")
        sys.exit(1)

# Create output directory
outDirFiltered = os.path.join(path_output, "step6_SAR_filtered")
if not os.path.exists(outDirFiltered):
    os.mkdir(outDirFiltered)

# Search files
SARfiles = []
for root, dirs, files in os.walk(inDir):
    if water:
        SARfiles += [os.path.join(root, f) for f in fnmatch.filter(files, "*SFRQWATER*")]

    if wetness:
        SARfiles += [os.path.join(root, f) for f in fnmatch.filter(files, "*SFRQWET*")]

if len(SARfiles) == 0:
    if not debug:
        raise GeoAlgorithmExecutionException("Runtime Error: No SAR files found.")

for i,inFile in enumerate(SARfiles):
    print("Processing %s of %s files" % (i+1, len(SARfiles)))

    if not debug:
        progress.setText("Processing %s of %s files" % (i+1, len(SARfiles)))

    outfile = os.path.join(outDirFiltered, os.path.basename(inFile)[:-4] + "_filtered.tif")
    data = gdal.Open(inFile)
    arr = data.ReadAsArray()

    denoise = cv2.fastNlMeansDenoising(src=arr, dst=None, h=10, templateWindowSize=7, searchWindowSize=21)

    trans = data.GetGeoTransform()
    proj = data.GetProjection()

    writeFile(outfile,trans,proj,denoise)

    if not debug:
        state = ((i + 1.) / len(SARfiles[:2]))*100
        progress.setPercentage(state)

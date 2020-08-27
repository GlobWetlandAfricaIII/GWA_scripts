# Copyright (c) 2016, GeoVille Information Systems GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.

"""
Calculation of topographic Wetness Index using SAGA

Keyword arguments:
    TWI: TWI file

Output:
    TWI binary mask

Dependencies:

Date created: 09/06/2016
Date last modified: 21/09/2016

"""

__author__ = "Christina Ludwig"
__version__ = "v1"

##Create TWI binary mask=name
##Wetland Inventory=group
##ParameterRaster|path_TWI|TWI
#OutputDirectory|out_dir|Output directory


import os, sys
import numpy as np
from scipy import ndimage
from osgeo import gdal

# Load additional library
import RSutils.RSutils as rsu

DEBUG = False

if not DEBUG:
    from qgis.core import QgsProcessingException
    from processing.tools import dataobjects
    import qgis
    

out_dir = os.path.dirname(path_TWI)
print(out_dir)

attrName = None
attrVal = None
extentBuffer=0

# Create TWI binary mask ------------------------------------------------

outfile_binary = os.path.join(out_dir, "TWIbinary.tif")

if not DEBUG:
    feedback.setProgressText("Creating binary mask ...")

# Median filter
TWI, geotrans, proj = rsu.raster2array(path_TWI)
TWI = ndimage.median_filter(TWI, size=7) * 1000

path_TWI_filtered = path_TWI[:-4] + "_TWIfiltered.tif"
x = rsu.array2raster(TWI, geotrans, proj, path_TWI_filtered, gdal.GDT_Float32, -9999)
if x == False:
    raise RuntimeError("Exporting TWI failed.")


# Normalize TWI
TWI = (TWI-np.nanpercentile(TWI, 1))/(np.nanpercentile(TWI, 99)-np.nanpercentile(TWI, 1))

# Create TWI mask
TWI_binary = np.where(TWI > 0.4, 0, 1)

#Sieve mask
TWI_binary = rsu.removeNoise(TWI_binary, 2)
TWI_binary = rsu.binaryBuffer_negative(TWI_binary, 3)

#Export to file
x = rsu.array2raster(TWI_binary,geotrans, proj, outfile_binary, gdal.GDT_Byte, 255)
if x == False:
    raise RuntimeError("Exporting TWI mask failed.")



del TWI_binary, TWI

try:
    dataobjects.load(outfile_binary, os.path.basename(outfile_binary), isRaster=True)
except:
    dataobjects.load(outfile_binary, os.path.basename(outfile_binary))

try:
    dataobjects.load(path_TWI_filtered, os.path.basename(path_TWI_filtered), isRaster=True)
except:
    dataobjects.load(path_TWI_filtered, os.path.basename(path_TWI_filtered))

if not DEBUG:
    feedback.setProgressText("TWI binary mask done.")


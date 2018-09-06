##Wetland Habitat Mapping=group
##Temporal statistics_r.series=name
##ParameterFile|Select_directory|Directory containing vegetation/water index layers|True|False
##OutputRaster|output|Output temporal statistics


import glob, os
import gdal_merge as gm
from PyQt4.QtCore import QFileInfo
from qgis.core import QgsRasterLayer, QgsRectangle

os.chdir(Select_directory)
rlist = []
extent = QgsRectangle()
extent.setMinimal()
n = len(glob.glob("*.tif"))

for raster in glob.glob("*.tif"):
    fileInfo = QFileInfo(raster)
    baseName = fileInfo.baseName()
    rlayer = QgsRasterLayer(raster, baseName)
    # Combine raster layers to list
    rlist.append(rlayer)
    # Combine raster extents
    extent.combineExtentWith(rlayer.extent())

# Get extent
xmin = extent.xMinimum()
xmax = extent.xMaximum()
ymin = extent.yMinimum()
ymax = extent.yMaximum()
# Run algorithm and set relevant parameters

mean = processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 0,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": None})
                   
range = processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 9,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": None})
if n < 3: 
    del rlist
    gm.main(['', '-o', output, '-of', 'GTiff', '-separate', '-a_nodata', '-9999', '-ot', 'Int16', mean['output'], range['output']])

else:
    min = processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 3,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": None})
                   
    max = processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 6,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": None})
    sd = processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 8,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": None})
                   
    del rlist               
    gm.main(['', '-o', output, '-of', 'GTiff', '-separate', '-a_nodata', '-9999', '-ot', 'Int16', mean['output'], max['output'], min['output'], range['output'], sd['output']])
    
##MM=group
##r.series_directory=name
##Select_directory=Folder
##output=output raster

import glob, os
from PyQt4.QtCore import QFileInfo
from qgis.core import QgsRasterLayer, QgsRectangle

os.chdir(Select_directory)
rlist = []
extent = QgsRectangle()
extent.setMinimal()
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
processing.runalg("grass7:r.series",
                  {"input": rlist,
                   "-n": False,
                   "method": 3,
                   "range": '-10000000000,10000000000',
                   "GRASS_REGION_PARAMETER": "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax),
                   "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                   "output": output})

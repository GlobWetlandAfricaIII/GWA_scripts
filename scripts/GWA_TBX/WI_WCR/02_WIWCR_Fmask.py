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
__author__ = "Johannes Schmid"
__version__ = "1.0"

# GUI for QGIS ---------------------------------------------------------------

##Mask for Sentinel 2 for Wetland Inventory=name
##Wetland Inventory=group
##ParameterFile|granuledir|Image Directory (For images including subimages use target granule directory)|True|False
##ParameterFile|anglesfile|Input angles file containing satellite and sun azimuth and zenith|False|True|
##*ParameterBoolean|verbose|verbose output|True
##ParameterNumber|mincloudsize|Mininum cloud size (in pixels) to retain, before any buffering|0|None|0
##ParameterNumber|cloudbufferdistance|Distance (in metres) to buffer final cloud objects|0|None|150
##ParameterNumber|shadowbufferdistance|Distance (in metres) to buffer final cloud shadow objects|0|None|300
##ParameterNumber|cloudprobthreshold|Cloud probability threshold (percentage) (Eqn 17)|0|100|20
##*ParameterNumber|nirsnowthreshold|Threshold for NIR reflectance for snow detection (Eqn 20). Increase this to reduce snow commission errors|0|1|0.11
##*ParameterNumber|greensnowthreshold|Threshold for Green reflectance for snow detection (Eqn 20). Increase this to reduce snow commission errors|0|1|0.1

import os
import qgis
import processing

for s in os.listdir(granuledir):
        s = os.path.join(granuledir, s)
        if os.path.isdir(s) and s.endswith(".SAFE"):
                dirs = [x[0] for x in os.walk(s)]
                for dir in dirs:
                        if 'IMG_DATA' in dir:
                                filename = os.listdir(dir)[0]
                                scene = os.path.basename(filename)[:-8]
                                output = os.path.join(dir, scene + '_fmask.tif')

                processing.runalg(
                        "script:fmasksentinel2",
                        s,
                        anglesfile,
                        verbose,
                        mincloudsize,
                        cloudbufferdistance,
                        shadowbufferdistance,
                        cloudprobthreshold,
                        nirsnowthreshold,
                        greensnowthreshold,
                        output
                )

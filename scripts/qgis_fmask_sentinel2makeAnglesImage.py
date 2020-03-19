#Definition of inputs and outputs
#==================================
##FMask=group
##Sentinel 2 Make Angles Image=name
##ParameterFile|infile|Input sentinel-2 tile metafile|False|False|xml
##OutputFile|outfile|Output angles image file|tif

from argparse import Namespace
import sys
import os.path
import numpy as np

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from qgis_fmask.interfaces.fmask_sentinel2makeAnglesImage import mainRoutine

cmdargs = Namespace(
        infile=infile,
        outfile=outfile)

with np.errstate(invalid='ignore'):
    mainRoutine(cmdargs)

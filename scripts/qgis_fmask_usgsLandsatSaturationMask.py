#Definition of inputs and outputs
#==================================
##FMask=group
##Landsat Saturation Mask=name
##ParameterFile|infile|Input raw DN radiance image|False|False
##ParameterFile|mtl|MTL file|False|False|txt
##ParameterFile|anglesfile|Input angles file containing satellite and sun azimuth and zenith|False|True|
##OutputFile|outfile|Output angles image file|tif

from argparse import Namespace
import sys
import os.path
import numpy as np

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from qgis_fmask.interfaces.fmask_usgsLandsatSaturationMask import mainRoutine

cmdargs = Namespace(
        infile=infile,
        mtl=mtl,
        outfile=outfile)

with np.errstate(invalid='ignore'):
    mainRoutine(cmdargs)

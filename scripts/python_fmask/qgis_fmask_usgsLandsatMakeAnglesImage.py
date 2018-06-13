#Definition of inputs and outputs
#==================================
##FMask=group
##Landsat Make Angles Image=name
##ParameterFile|mtl|MTL file|False|False|txt
##ParameterFile|templateimg|Image file name to use as template for output angles image|False|False|TIF
##OutputFile|outfile|Output angles image file|tif

from argparse import Namespace
import sys
import os.path
import numpy as np

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from interfaces.fmask_usgsLandsatMakeAnglesImage import mainRoutine

cmdargs = Namespace(
        mtl=mtl,
        templateimg=templateimg,
        outfile=outfile)

with np.errstate(invalid='ignore'):
    mainRoutine(cmdargs)

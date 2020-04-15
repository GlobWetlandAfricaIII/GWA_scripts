# Definition of inputs and outputs
# ==================================
##FMask=group
##Landsat Top Of Atmosphere=name
##ParameterFile|productdir|Directory of Landsat product|True|False
##ParameterSelection|landsatkeynr|Landsat sensor|Landsat 4&5;Landsat 7;Landsat 8|2
##*OutputFile|anglesfile|Angles file. If not existing, it will be created in this location.
##OutputFile|outfile|Output TOA file|tif

from argparse import Namespace
import sys
import os.path
import shutil
import tempfile

import numpy as np
from processing.tools import dataobjects

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from qgis_fmask.stacks.landsat_stack import create_landsat_stack
from qgis_fmask.interfaces.fmask_usgsLandsatTOA import mainRoutine
from qgis_fmask.interfaces.fmask_usgsLandsatMakeAnglesImage import (
    mainRoutine as mainRoutine_angles,
)
from qgis_fmask.interfaces.fmask_usgsLandsatSaturationMask import (
    mainRoutine as mainRoutine_saturation,
)
from qgis_fmask.interfaces.redirect_print import redirect_print
from qgis_fmask.interfaces.landsatmeta import find_mtl_in_product_dir

landsatkey = ["4&5", "7", "8"][landsatkeynr]

tempdir = tempfile.mkdtemp()
try:
    mtl = find_mtl_in_product_dir(productdir)

    # create band stack
    feedback.pushConsoleInfo("Creating band stack ...")
    refimg = os.path.join(tempdir, "ref.vrt")
    create_landsat_stack(
        productdir, outfile=refimg, imagename="ref", landsatkey=landsatkey
    )
    feedback.pushConsoleInfo("Done.")

    # create angles file
    anglesfile = anglesfile or os.path.join(tempdir, "angles.img")
    if not os.path.isfile(anglesfile):
        feedback.pushConsoleInfo("Creating angles file ...")
        with np.errstate(invalid="ignore"):
            mainRoutine_angles(
                Namespace(mtl=mtl, templateimg=refimg, outfile=anglesfile)
            )
        feedback.pushConsoleInfo("Done.")

    feedback.pushConsoleInfo("Creating TOA image ...")
    cmdargs = Namespace(infile=refimg, mtl=mtl, anglesfile=anglesfile, output=outfile)
    with np.errstate(invalid="ignore"):
        mainRoutine(cmdargs)
    feedback.pushConsoleInfo("Done.")

finally:
    try:
        shutil.rmtree(tempdir)
    except OSError:
        pass

dataobjects.load(outfile, os.path.basename(outfile))

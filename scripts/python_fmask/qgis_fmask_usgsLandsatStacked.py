#Definition of inputs and outputs
#==================================
##FMask=group
##FMask Landsat=name
##ParameterFile|productdir|Directory of Landsat product|True|False
##ParameterSelection|landsatkeynr|Landsat sensor|Landsat 4&5;Landsat 7;Landsat 8|2
##OutputFile|anglesfile|Angles file. If not existing, it will be created in this location.
##OutputFile|saturationfile|Saturation mask file. If not existing, it will be created in this location.
##OutputFile|toafile|TOA file. If not existing, it will be created in this location.
##OutputFile|output|Output cloud mask|tif
##ParameterNumber|mincloudsize|Mininum cloud size (in pixels) to retain, before any buffering|0|None|0
##ParameterNumber|cloudbufferdistance|Distance (in metres) to buffer final cloud objects|0|None|150
##ParameterNumber|shadowbufferdistance|Distance (in metres) to buffer final cloud shadow objects|0|None|300
##ParameterNumber|cloudprobthreshold|Cloud probability threshold (percentage) (Eqn 17)|0|100|20
##*ParameterNumber|nirsnowthreshold|Threshold for NIR reflectance for snow detection (Eqn 20). Increase this to reduce snow commission errors|0|1|0.11
##*ParameterNumber|greensnowthreshold|Threshold for Green reflectance for snow detection (Eqn 20). Increase this to reduce snow commission errors|0|1|0.1

from argparse import Namespace
import sys
import os.path
import tempfile
import shutil

import numpy as np
from processing.tools import dataobjects

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from stacks.landsat_stack import create_landsat_stacks
from interfaces.fmask_usgsLandsatStacked import mainRoutine
from interfaces.fmask_usgsLandsatMakeAnglesImage import mainRoutine as mainRoutine_angles
from interfaces.fmask_usgsLandsatSaturationMask import mainRoutine as mainRoutine_saturation
from interfaces.fmask_usgsLandsatTOA import mainRoutine as mainRoutine_toa
from interfaces.redirect_print import redirect_print
from interfaces.landsatmeta import find_mtl_in_product_dir

landsatkey = ['4&5', '7', '8'][landsatkeynr]

tempdir = tempfile.mkdtemp()
try:
    mtl = find_mtl_in_product_dir(productdir)

    # create band stacks
    progress.setConsoleInfo('Creating band stacks ...')
    outfile_template = os.path.join(tempdir, 'temp_{imagename}.vrt')
    vrtfiles = create_landsat_stacks(
            productdir, outfile_template=outfile_template, landsatkey=landsatkey)
    progress.setConsoleInfo('Done.')

    # create angles file
    anglesfile = anglesfile or os.path.join(tempdir, 'angles.img')
    if not os.path.isfile(anglesfile):
        progress.setConsoleInfo('Creating angles file ...')
        with np.errstate(invalid='ignore'):
            mainRoutine_angles(
                    Namespace(
                        mtl=mtl,
                        templateimg=vrtfiles['ref'],
                        outfile=anglesfile))
        progress.setConsoleInfo('Done.')

    # create saturation file
    saturationfile = saturationfile or os.path.join(tempdir, 'saturation.img')
    if not os.path.isfile(saturationfile):
        progress.setConsoleInfo('Creating saturation mask file ...')
        mainRoutine_saturation(
                Namespace(
                    infile=vrtfiles['ref'],
                    mtl=mtl,
                    output=saturationfile))
        progress.setConsoleInfo('Done.')

    # create TOA file
    toafile = toafile or os.path.join(tempdir, 'toa.img')
    if not os.path.isfile(toafile):
        progress.setConsoleInfo('Creating TOA file ...')
        mainRoutine_toa(
                Namespace(
                    infile=vrtfiles['ref'],
                    mtl=mtl,
                    anglesfile=anglesfile,
                    output=toafile))
        progress.setConsoleInfo('Done.')

    cmdargs = Namespace(
            toa=toafile,
            thermal=vrtfiles['thermal'],
            anglesfile=anglesfile,
            saturation=saturationfile,
            mtl=mtl,
            verbose=True,
            keepintermediates=False,
            tempdir=tempdir,
            output=output,
            mincloudsize=mincloudsize,
            cloudbufferdistance=cloudbufferdistance,
            shadowbufferdistance=shadowbufferdistance,
            cloudprobthreshold=cloudprobthreshold,
            nirsnowthreshold=nirsnowthreshold,
            greensnowthreshold=greensnowthreshold)

    progress.setConsoleInfo('Running FMask (this may take a while) ...')
    with redirect_print(progress):
        mainRoutine(cmdargs)
    progress.setConsoleInfo('Done.')
finally:
    try:
        shutil.rmtree(tempdir)
    except OSError:
        pass

dataobjects.load(output, os.path.basename(output))

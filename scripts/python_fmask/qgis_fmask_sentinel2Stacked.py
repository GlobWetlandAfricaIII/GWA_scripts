#Definition of inputs and outputs
#==================================
##FMask=group
##FMask Sentinel 2=name
##ParameterFile|granuledir|Image Directory (For images including subimages use target granule directory)|True|False
##ParameterFile|anglesfile|Input angles file containing satellite and sun azimuth and zenith|False|True|
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
from glob import glob
from processing.tools import dataobjects

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)

from stacks.sentinel_stack import create_sentinel_stack
from interfaces.fmask_sentinel2Stacked import mainRoutine
from interfaces.fmask_sentinel2makeAnglesImage import mainRoutine as mainRoutine_angles
from interfaces.redirect_print import redirect_print
from interfaces.s2meta import find_xml_in_granule_dir


tempdir = tempfile.mkdtemp()
try:
    progress.setConsoleInfo('Creating Sentinel 2 band stack VRT file ...')
    tempvrt = os.path.join(tempdir, 'temp.vrt')
    create_sentinel_stack(granuledir, outfile=tempvrt)
    progress.setConsoleInfo('Done.')

    if not anglesfile:
        progress.setConsoleInfo('Creating angles file ...')
        anglesfile = os.path.join(tempdir, 'angles.img')
        cmdargs_angles = Namespace(
                infile=find_xml_in_granule_dir(granuledir),
                outfile=anglesfile)
        import numpy as np
        with np.errstate(invalid='ignore'):
            mainRoutine_angles(cmdargs_angles)
        progress.setConsoleInfo('Done.')

    dirs = [x[0] for x in os.walk(granuledir)]
    for dir in dirs:
        if 'IMG_DATA' in dir:
            scene = os.path.basename(glob(os.path.join(dir, '*.jp2'))[0])[:-8]
            outpath = os.path.join(dir, scene + '_fmask.tif')

    cmdargs = Namespace(
            toa=tempvrt,
            anglesfile=anglesfile,
            output=outpath,
            #verbose=verbose,
            tempdir=tempdir,
            keepintermediates=False,
            mincloudsize=mincloudsize,
            cloudbufferdistance=cloudbufferdistance,
            shadowbufferdistance=shadowbufferdistance,
            cloudprobthreshold=cloudprobthreshold,
            nirsnowthreshold=nirsnowthreshold,
            greensnowthreshold=greensnowthreshold)





    progress.setConsoleInfo('Running FMask (this may take a while) ...')
    with redirect_print(progress):
        mainRoutine(cmdargs)
finally:
    try:
        shutil.rmtree(tempdir)
    except OSError:
        pass

progress.setConsoleInfo('Done.')
dataobjects.load(outpath, os.path.basename(outpath))


#OutputFile|output|Output cloud mask|tif
#*ParameterBoolean|verbose|verbose output|True
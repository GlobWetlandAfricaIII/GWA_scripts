#!C:\bld\python-fmask_1491348722444\_b_env\python.exe

"""
Script that takes USGS landsat stacked separately for
reflective and thermal and runs the fmask on it.
"""
# This file is part of 'python-fmask' - a cloud masking module
# Copyright (C) 2015  Neil Flood
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
from __future__ import print_function, division

import sys
import argparse
from fmask import fmask
from fmask import config

from rios import fileinfo


def mainRoutine(cmdargs):
    """
    Main routine that calls fmask
    """
    # 1040nm thermal band should always be the first (or only) band in a
    # stack of Landsat thermal bands
    thermalInfo = config.readThermalInfoFromLandsatMTL(cmdargs.mtl)

    anglesfile = cmdargs.anglesfile
    anglesInfo = config.AnglesFileInfo(anglesfile, 3, anglesfile, 2, anglesfile, 1, anglesfile, 0)

    mtlInfo = config.readMTLFile(cmdargs.mtl)
    landsat = mtlInfo['SPACECRAFT_ID'][-1]

    if landsat == '4':
        sensor = config.FMASK_LANDSAT47
    elif landsat == '5':
        sensor = config.FMASK_LANDSAT47
    elif landsat == '7':
        sensor = config.FMASK_LANDSAT47
    elif landsat == '8':
        sensor = config.FMASK_LANDSAT8
    else:
        raise SystemExit('Unsupported Landsat sensor')

    fmaskFilenames = config.FmaskFilenames()
    fmaskFilenames.setTOAReflectanceFile(cmdargs.toa)
    fmaskFilenames.setThermalFile(cmdargs.thermal)
    fmaskFilenames.setOutputCloudMaskFile(cmdargs.output)
    if cmdargs.saturation is not None:
        fmaskFilenames.setSaturationMask(cmdargs.saturation)
    else:
        print('saturation mask not supplied - see fmask_usgsLandsatSaturationMask.py')

    fmaskConfig = config.FmaskConfig(sensor)
    fmaskConfig.setThermalInfo(thermalInfo)
    fmaskConfig.setAnglesInfo(anglesInfo)
    fmaskConfig.setKeepIntermediates(cmdargs.keepintermediates)
    fmaskConfig.setVerbose(cmdargs.verbose)
    fmaskConfig.setTempDir(cmdargs.tempdir)
    fmaskConfig.setMinCloudSize(cmdargs.mincloudsize)
    fmaskConfig.setEqn17CloudProbThresh(cmdargs.cloudprobthreshold / 100)    # Note conversion from percentage
    fmaskConfig.setEqn20NirSnowThresh(cmdargs.nirsnowthreshold)
    fmaskConfig.setEqn20GreenSnowThresh(cmdargs.greensnowthreshold)

    # Work out a suitable buffer size, in pixels, dependent on the resolution of the input TOA image
    toaImgInfo = fileinfo.ImageInfo(cmdargs.toa)
    fmaskConfig.setCloudBufferSize(int(cmdargs.cloudbufferdistance / toaImgInfo.xRes))
    fmaskConfig.setShadowBufferSize(int(cmdargs.shadowbufferdistance / toaImgInfo.xRes))

    fmask.doFmask(fmaskFilenames, fmaskConfig)

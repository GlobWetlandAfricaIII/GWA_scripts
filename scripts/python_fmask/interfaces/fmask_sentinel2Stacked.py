"""
Script that takes a stacked Sentinel 2 Level 1C image and runs
fmask on it.
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

import os
import tempfile

from rios import fileinfo

from fmask import config
from fmask import fmask


def checkAnglesFile(inputAnglesFile, toafile):
    """
    Check that the resolution of the input angles file matches that of the input
    TOA reflectance file. If not, make a VRT file which will resample it
    on-the-fly. Only checks the resolution, assumes that if these match, then everything
    else will match too.

    Return the name of the angles file to use.

    """
    toaImgInfo = fileinfo.ImageInfo(toafile)
    anglesImgInfo = fileinfo.ImageInfo(inputAnglesFile)

    outputAnglesFile = inputAnglesFile
    if (toaImgInfo.xRes != anglesImgInfo.xRes) or (toaImgInfo.yRes != anglesImgInfo.yRes):
        (fd, vrtName) = tempfile.mkstemp(prefix='angles', suffix='.vrt')
        os.close(fd)
        cmdFmt = ("gdalwarp -q -of VRT -tr {xres} {yres} -te {xmin} {ymin} {xmax} {ymax} "+
            "-r near {infile}  {outfile} ")
        cmd = cmdFmt.format(xres=toaImgInfo.xRes, yres=toaImgInfo.yRes, xmin=toaImgInfo.xMin,
            ymin=toaImgInfo.yMin, xmax=toaImgInfo.xMax, ymax=toaImgInfo.yMax,
            outfile=vrtName, infile=inputAnglesFile)
        os.system(cmd)
        outputAnglesFile = vrtName

    return outputAnglesFile


def mainRoutine(cmdargs):
    """
    Main routine that calls fmask
    """
    anglesfile = checkAnglesFile(cmdargs.anglesfile, cmdargs.toa)
    anglesInfo = config.AnglesFileInfo(anglesfile, 3, anglesfile, 2, anglesfile, 1, anglesfile, 0)

    fmaskFilenames = config.FmaskFilenames()
    fmaskFilenames.setTOAReflectanceFile(cmdargs.toa)
    fmaskFilenames.setOutputCloudMaskFile(cmdargs.output)
    #fmaskFilenames.setOutputCloudMaskFile(out)

    fmaskConfig = config.FmaskConfig(config.FMASK_SENTINEL2)
    fmaskConfig.setAnglesInfo(anglesInfo)
    fmaskConfig.setKeepIntermediates(cmdargs.keepintermediates)
    #fmaskConfig.setVerbose(cmdargs.verbose)
    fmaskConfig.setTempDir(cmdargs.tempdir)
    fmaskConfig.setTOARefScaling(10000.0)
    fmaskConfig.setMinCloudSize(cmdargs.mincloudsize)
    fmaskConfig.setEqn17CloudProbThresh(cmdargs.cloudprobthreshold / 100)    # Note conversion from percentage
    fmaskConfig.setEqn20NirSnowThresh(cmdargs.nirsnowthreshold)
    fmaskConfig.setEqn20GreenSnowThresh(cmdargs.greensnowthreshold)

    # Work out a suitable buffer size, in pixels, dependent on the resolution of the input TOA image
    toaImgInfo = fileinfo.ImageInfo(cmdargs.toa)
    fmaskConfig.setCloudBufferSize(int(cmdargs.cloudbufferdistance / toaImgInfo.xRes))
    fmaskConfig.setShadowBufferSize(int(cmdargs.shadowbufferdistance / toaImgInfo.xRes))

    fmask.doFmask(fmaskFilenames, fmaskConfig)

    if anglesfile != cmdargs.anglesfile:
        # Must have been a temporary vrt, so remove it
        os.remove(anglesfile)

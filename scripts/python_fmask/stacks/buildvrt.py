import os
import sys
import glob
import subprocess


def find_gdal_exe(gdalcmd):
    if sys.platform.startswith('linux'):
        return gdalcmd
    try:
        if not gdalcmd.endswith('.exe'):
            gdalcmd += '.exe'
        pattern = os.path.join('C:\\', 'OSGeo4W*', 'bin', gdalcmd)
        cmdpath = glob.glob(pattern)[0]
    except IndexError:
        # no OSGeo4W installed
        cmdpath = gdalcmd
    return cmdpath


gdalbuildvrt_exe = find_gdal_exe('gdalbuildvrt')


def _get_startupinfo():
    """startupinfo to suppress external command windows"""
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


def run_cmd(cmd, outfile):
    subprocess.check_output(cmd,
            stdin=subprocess.PIPE, stderr=subprocess.PIPE,  # to avoid error in pythonw
            startupinfo=_get_startupinfo())
    if not os.path.isfile(outfile):
        cmdstr = subprocess.list2cmdline(cmd)
        raise RuntimeError('GDAL command failed. No output created with '
                'cmd \'{}\'.'.format(cmdstr))


def cmd_gdalbuildvrt(infiles, outfile, resolution='average', separate=False, proj_difference=False, extra=[]):
    cmd = [gdalbuildvrt_exe]
    cmd += ['-q']
    if resolution != 'average':
        cmd += ['-resolution', resolution]
    if separate:
        cmd += ['-separate']
    if proj_difference:
        cmd += ['-allow_projection_difference']
    cmd += extra
    cmd += [outfile]
    cmd += infiles
    return cmd


def buildvrt(infiles, outfile, **kwargs):
    """GDAL build virtual raster

    Parameters
    ----------
    infiles : list of str
        paths to input files
    outfile : str
        path to output vrt
    kwargs : dict
        keyword arguments passed to
        cmd_gdalbuildvrt
    """
    cmd = cmd_gdalbuildvrt(infiles, outfile, **kwargs)
    run_cmd(cmd, outfile)

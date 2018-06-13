import os
import glob
import fnmatch

from .buildvrt import buildvrt


def recursive_glob(rootdir='.', pattern='*'):
    """Search recursively for files matching a specified pattern.

    Adapted from http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    """

    matches = []
    for root, dirnames, filenames in os.walk(rootdir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches


def create_sentinel_stack(granuledir, outfile):
    infiles = []
    for fnpattern in ['*_B0[1-8].jp2', '*_B8A.jp2', '*_B09.jp2', '*_B1[0-2].jp2']:
        #pattern = os.path.join(granuledir, 'IMG_DATA', fnpattern)
        bandfiles = recursive_glob(rootdir=granuledir, pattern=fnpattern)
        #bandfiles = sorted(glob.glob(pattern))
        #if not bandfiles:
        #    raise RuntimeError('No files found for pattern \'{}\'.'.format(pattern))
        infiles += bandfiles
    buildvrt(infiles, outfile, resolution='user', separate=True, extra=['-tr', '20', '20'])

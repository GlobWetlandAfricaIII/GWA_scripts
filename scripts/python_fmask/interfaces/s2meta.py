import os
import glob
import fnmatch


def recursive_glob(rootdir='.', pattern='*'):
    """Search recursively for files matching a specified pattern.

    Adapted from http://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
    """

    matches = []
    for root, dirnames, filenames in os.walk(rootdir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))

    return matches

def find_xml_in_granule_dir(granuledir):
    pattern = os.path.join(granuledir, '*.xml')
    #xmlfiles = glob.glob(pattern)
    xmlfiles = recursive_glob(granuledir, pattern='*MTD*TL*.xml')
    if len(xmlfiles) != 1:
        raise RuntimeError('Expecting exactly one XML file in granules dir. Found {} with pattern \'{}\'.',format(len(xmlfiles), pattern))
    return xmlfiles[0]

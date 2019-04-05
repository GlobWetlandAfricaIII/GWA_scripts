#Definition of inputs and outputs
#==================================
##Generic Tools=group
##Untar Imagery=name
##ParameterFile|infile|Landsat tar.gz file|False|False|gz
##OutputDirectory|processing_path|Folder to unpack the data to

import glob
import os
import sys
import tarfile

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)
from processing.tools import dataobjects
    
def untar(infile, processing_path):
    
    tar = tarfile.open(infile)
    tarfiles = tar.getnames()
    progress.setConsoleInfo('Unpacking data:')
    progress.setConsoleInfo(tarfiles)
    tar.extractall(processing_path)
    tar.close()
    return tarfiles
    
progress.setConsoleInfo('Starting untar')
tarfiles = untar(infile, processing_path)
progress.setConsoleInfo('Untar finished...')

lbase = os.path.basename(infile)
ltype = lbase[:4]

if ltype in 'LC08':
    bandlist = ['band2','band3','band4','band5','band6','band7', 'B2','B3','B4','B5','B6','B7']
elif ltype in ['LE07', 'LT05']:
    bandlist = ['band1','band2','band3','band4','band5','band7', 'B1','B2','B3','B4','B5','B7']
else:
    progress.setConsoleInfo('Cannot detect if it is Landsat 5, 7, or 8. Stopping')
    exit()

# paths to the .tif files
fls = [os.path.join(processing_path, f) for f in tarfiles]
progress.setConsoleInfo(fls)

bandfile_list = []
type(bandfile_list)
for item in bandlist: 
    for cont in fls:
        extension = os.path.splitext(cont)[1]
        if extension == '.tif': 
            if cont.replace(extension, '').split('_')[(len(cont.replace(extension, '').split('_'))-1)] == item:
                bandfile_list.append(cont)

for layer in bandfile_list:
        dataobjects.load(layer,  isRaster=True)
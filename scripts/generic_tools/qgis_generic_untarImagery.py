##ParameterFile|infile||False|False|gz
##OutputDirectory|processing_path|Folder to unpack the data to

import glob
import os
import sys
import tarfile
from processing.tools import dataobjects
from qgis.processing import alg

@alg(
    name="untarimagery",
    label=alg.tr("Untar Imagery"),
    group="gt",
    group_label=alg.tr("Generic Tools")
)
@alg.input(type=alg.FILE, name="infile", label="Landsat tar.gz file", behavior=0, optional=True, extension='gz')
@alg.input(type=alg.FOLDER_DEST, name='processing_path', label='processing path')
@alg.output(type=alg.FOLDER, name='out_folder', label='out folder')

def untarimagery(instance, parameters, context, feedback, inputs):
    """ untarimagery """

    processing_path = instance.parameterAsString(parameters, 'processing_path', context)
    infile = instance.parameterAsString(parameters, 'infile', context)

    def untar(infile, processing_path):
        tar = tarfile.open(infile)
        tarfiles = tar.getnames()
        feedback.pushConsoleInfo('Unpacking data:')
        feedback.pushConsoleInfo(tarfiles)
        tar.extractall(processing_path)
        tar.close()
        return tarfiles

    feedback.pushConsoleInfo('Starting untar')
    tarfiles = untar(infile, processing_path)
    feedback.pushConsoleInfo('Untar finished...')

    lbase = os.path.basename(infile)
    ltype = lbase[:4]

    if ltype in 'LC08':
        bandlist = ['band2', 'band3', 'band4', 'band5', 'band6', 'band7', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7']
    elif ltype in ['LE07', 'LT05']:
        bandlist = ['band1', 'band2', 'band3', 'band4', 'band5', 'band7', 'B1', 'B2', 'B3', 'B4', 'B5', 'B7']
    else:
        feedback.pushConsoleInfo('Cannot detect if it is Landsat 5, 7, or 8. Stopping')
        exit()

    # paths to the .tif files
    fls = [os.path.join(processing_path, f) for f in tarfiles]
    feedback.pushConsoleInfo(fls)

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

    return({'outfolder': instance.parameterAsString(parameters, 'processing_path', context)})
import os
from processing.tools.system import tempHelpFolder
from processing.core.ProcessingLog import ProcessingLog

from qgis.processing import alg

@alg(
    name="postclassificationcomparison",
    label=alg.tr("Post-classification comparison"),
    group="ts",
    group_label=alg.tr("Timeseries")
)
@alg.input(type=alg.RASTER_LAYER, name="classification", label="Select classification of \"initial state\"", default=False)
@alg.input(type=alg.RASTER_LAYER, name="reference", label="Select classification of \"final state\"", default=False)
@alg.input(type=bool, name='w', label='Wide report (132 columns)', default=False)
@alg.input(type=alg.EXTENT, name='extent', label='Region extent')
@alg.input(type=alg.FILE_DEST, name='output', label='Name for output file containing the change detection matrix')
def pg04waterqualityparameters04olcicrsselect(instance, parameters, context, feedback, inputs):
    """
    pg04waterqualityparameters04olcicrsselect
    """
    classification = instance.parameterAsString(parameters, 'classification', context)
    reference = instance.parameterAsString(parameters, 'reference', context)
    w = instance.parameterAsString(parameters, 'w', context)
    extent = instance.parameterAsString(parameters, 'extent', context)
    output = instance.parameterAsString(parameters, 'output', context)

    loglines = []
    loglines.append('Post-classification comparison script console output')
    loglines.append('')

    # set up the actual and temporary outputs
    outputFile = open(output, 'w')
    outputFile.close()
    tempOutput = tempHelpFolder() + os.sep + "postclassificationComparisionScript.txt"
    if os.path.exists(tempOutput):
        os.remove(tempOutput)

    if processing.runalg("grass7:r.kappa", classification,reference,'CHANGE DETECTION MATRIX', True, w, extent, tempOutput):
        with open(tempOutput) as inputFile, open(output, "a") as outputFile:
            lines = inputFile.readlines()
            writeLines = False
            for line in lines:
                if line.startswith('Cats') or line.startswith('cat#'):
                    break
                if writeLines:
                    outputFile.write(line)
                elif line.startswith('Error Matrix'):
                    writeLines = True
                    outputFile.write('Change detection matrix\n')
        feedback.setProgressText('Saved change detection matrix to file %s' % output)
        loglines.append('Saved change detection matrix to file %s' % output)
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)
    else:
        feedback.setProgressText('ERROR running r.kappa. Check log for details.')
        loglines.append('ERROR running r.kappa. Check log for details.')
        ProcessingLog.addToLog(ProcessingLog.LOG_INFO, loglines)
import os
import glob
import tempfile

from qgis.processing import alg


@alg(
    name="pg04waterqualityparameters01olciidepix",
    label=alg.tr("PG04_WaterQualityParameters_01_OLCI_IdePix"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.BOOL, name="CloudBuffer", label="Process cloud buffer", default=True)
@alg.input(type=alg.NUMBER, name="CloudBufferWidth", 
           label="lnsert size of cloud buffer in pixel", default=2, minValue=0)
@alg.input(type=alg.BOOL, name="OutputCloudProbabilityFeatureValue", label="Write cloud probability feature value", default=False, advanced=True)
@alg.output(type=alg.FILE, name='Input_folder', label='Input folder', behaviour=1)

def pg04waterqualityparameters01olciidepix(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    tempfolder = 'wq_scripts_'
    CloudBuffer = instance.parameterAsBool(parameters, 'CloudBuffer', context)
    CloudBufferWidth = instance.parameterAsDouble(parameters, 'CloudBufferWidth', context)
    OutputCloudProbabilityFeatureValue = instance.parameterAsBool(parameters, 'OutputCloudProbabilityFeatureValue', context)

    def folder_create(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return tempdir
        except:
            feedback.pushConsoleInfo('Temporary folder:' + tempfolder + ' does not exist and will be created.')
            tempfile.mkdtemp(prefix=tempfolder)
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return tempdir

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            feedback.pushConsoleInfo('ERROR: Temporary folder:' + tempfolder + ' cloud not be created. Check for administration rights to create folder.')
            return True

    def create_parameterfile(tempdir, CloudBuffer, CloudBufferWidth,  OutputCloudProbabilityFeatureValue):
        with open(tempdir + "WaterQualityParametersOLCI01.txt", "w") as text_file:
            text_file.write('cloudBuffer='+ str(CloudBuffer) + '\n')
            text_file.write('cloudBufferWidth='+ str(CloudBufferWidth) + '\n')
            text_file.write('outputCloudProbabilityValue='+ str(OutputCloudProbabilityFeatureValue).lower() + '\n')

    def execution(tempfolder):
        tempdir = folder_create(tempfolder) + '/'
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            create_parameterfile(tempdir, CloudBuffer, CloudBufferWidth, OutputCloudProbabilityFeatureValue)

    execution(tempfolder)
    Input_folder = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
    return {'Input_folder': Input_folder} #TODO CHECK IF WORKS
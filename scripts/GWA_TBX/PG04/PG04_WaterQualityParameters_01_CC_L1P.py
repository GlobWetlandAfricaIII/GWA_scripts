import os
import glob

from qgis.processing import alg
from qgis import processing
import tempfile

@alg(
    name="pg04waterqualityparameterscoastcolourl1p",
    label=alg.tr("PG04_WaterQualityParameters_CoastColour_L1P"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.BOOL, name="Icol", label="Icol", default=False)
@alg.input(type=alg.BOOL, name="Calibration", label="Calibration", default=False)
@alg.input(type=alg.BOOL, name="Smile", label="Smile", default=True)
@alg.input(type=alg.BOOL, name="Equalization", label="Equalization", default=True)
@alg.input(type=alg.BOOL, name="IgnoreSeaIceClim", label="Ignore sea ice climatology",
           default=False)
@alg.input(type=alg.NUMBER, name="CloudBufferWidth",
           label="lnsert size of cloud buffer in pixel", default=2, minValue=0)
@alg.input(type=alg.NUMBER, name="CloudScreeningAmbiguous",
           label="Cloud screening ambiguous threshold", default=1.4, minValue=0)
@alg.input(type=alg.NUMBER, name="CloudScreeningSure",
           label="Cloud screening sure threshold", default=1.8, minValue=0)
@alg.input(type=alg.NUMBER, name="GlintCloudThresholdAddition",
           label="Glint cloud screening addition", default=0.1, minValue=0)
@alg.input(type=alg.BOOL, name="OutputCloudProbabilityFeatureValue",
           label="Write cloud probability feature value", default=False)
@alg.output(type=alg.FILE, name="input_folder", label="Input folder", behavior=1)
def pg04waterqualityparameterscoastcolourl1p(instance, parameters, context, feedback, inputs):
    '''
    pg04waterqualityparameterscoastcolourl1p
    '''
    Icol = instance.parameterAsBool(parameters, 'Icol', context)
    Calibration = instance.parameterAsBool(parameters, 'Calibration', context)
    Smile = instance.parameterAsBool(parameters, 'Smile', context)
    Equalization = instance.parameterAsBool(parameters, 'Equalization', context)
    IgnoreSeaIceClim = instance.parameterAsBool(parameters, 'IgnoreSeaIceClim', context)
    CloudBufferWidth = instance.parameterAsDouble(parameters, 'CloudBufferWidth', context)
    CloudScreeningAmbiguous = instance.parameterAsDouble(
        parameters, 'CloudScreeningAmbiguous', context)
    CloudScreeningSure = instance.parameterAsDouble(parameters, 'CloudScreeningSure', context)
    GlintCloudThresholdAddition = instance.parameterAsDouble(
        parameters, 'GlintCloudThresholdAddition', context)
    OutputCloudProbabilityFeatureValue = instance.parameterAsDouble(
        parameters, 'OutputCloudProbabilityFeatureValue', context)

    tempfolder = 'wq_scripts_'

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

    def create_parameterfile(
        tempdir, Icol, Calibration, Smile, Equalization, IgnoreSeaIceClim,
        CloudBufferWidth, CloudScreeningAmbiguous, CloudScreeningSure,
        GlintCloudThresholdAddition, OutputCloudProbabilityFeatureValue
    ):
        with open(tempdir + "WaterQualityParameters01.txt", "w") as text_file:
            text_file.write('icol=' + str(Icol).lower() + '\n')
            text_file.write('calibration=' + str(Calibration).lower() + '\n')
            text_file.write('smile=' + str(Smile).lower() + '\n')
            text_file.write('equalization=' + str(Equalization).lower() + '\n')
            text_file.write('ignoreSeaIceClim=' + str(IgnoreSeaIceClim).lower() + '\n')
            text_file.write('cloudBufferWidth=' + str(CloudBufferWidth) + '\n')
            text_file.write('cloudScreeningAmbiguous=' + str(CloudScreeningAmbiguous) + '\n')
            text_file.write('cloudScreeningSure=' + str(CloudScreeningSure) + '\n')
            text_file.write('glintCloudThresholdAddition=' + str(GlintCloudThresholdAddition) + '\n')
            text_file.write('outputCloudProbabilityValue=' + str(OutputCloudProbabilityFeatureValue).lower() + '\n')

    def execution(tempfolder):
        tempdir = folder_create(tempfolder) + '/'
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            create_parameterfile(tempdir, Icol, Calibration, Smile, Equalization, IgnoreSeaIceClim,
                                 CloudBufferWidth, CloudScreeningAmbiguous, CloudScreeningSure,
                                 GlintCloudThresholdAddition, OutputCloudProbabilityFeatureValue)
    execution(tempfolder)
    
    input_folder = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
    return {'input_folder': input_folder} #TODO CHECK IF WORKS
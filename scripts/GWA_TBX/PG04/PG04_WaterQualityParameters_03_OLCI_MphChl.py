import os
import glob
import tempfile

from qgis.processing import alg

@alg(
    name="pg04waterqualityparameters03olcimphchl",
    label=alg.tr("PG04_WaterQualityParameters_03_OLCI_MphChl"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.STRING, name="MPHvalidPixelExpression", label="Valid pixel expression", default="not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not (pixel_classif_flags.IDEPIX_CLOUD or pixel_classif_flags.IDEPIX_CLOUD_BUFFER)")
@alg.input(type=alg.NUMBER, name="MPHcyanoMaxValue", label="Cyano maximum value", default=1000, minValue=0)
@alg.input(type=alg.NUMBER, name="MPHchlThreshForFloatFlag", label="CHL threshold for float flag", default=350, minValue=0)
@alg.input(type=alg.BOOL, name="MPHexportMph", label="Export MPH", default=False, advanced=True)
@alg.input(type=alg.FOLDER_DEST, name="Output_folder", label="Output directory")

def pg04waterqualityparameters03olcimphchl(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """

    MPHvalidPixelExpression = instance.parameterAsString(parameters, "MPHvalidPixelExpression", context)
    MPHcyanoMaxValue = instance.parameterAsEnum(parameters, "MPHcyanoMaxValue", context)
    MPHchlThreshForFloatFlag = instance.parameterAsEnum(parameters, "MPHchlThreshForFloatFlag", context)
    MPHchlThreshForFloatFlag = instance.parameterAsEnum(parameters, "MPHchlThreshForFloatFlag", context)
    MPHchlThreshForFloatFlag = instance.parameterAsEnum(parameters, "MPHchlThreshForFloatFlag", context)


    tempfolder = 'wq_scripts_'

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            progress.setConsoleInfo('ERROR: Parameter folder could not be found. Please execute step 1 first!')
            return True
            
    def convert(MPHcyanoMaxValue, MPHchlThreshForFloatFlag):
        MPHcyanoMaxValueS = '%.2f' % MPHcyanoMaxValue
        MPHchlThreshForFloatFlagS = '%.2f' % MPHchlThreshForFloatFlag
        return MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS

    def create_parameterfile(tempdir, MPHvalidPixelExpression, MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS):
        with open(tempdir + "WaterQualityParametersOLCI03.txt", "w") as text_file:
            text_file.write('mphValidExpression='+ MPHvalidPixelExpression + '\n')
            text_file.write('mphCyanoMaxValue='+ MPHcyanoMaxValueS + '\n') 
            text_file.write('mphChlThreshForFloatFlag='+ MPHchlThreshForFloatFlagS + '\n')
            #text_file.write('mphExportMph='+ str(MPHexportMph).lower() + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS = convert(MPHcyanoMaxValue, MPHchlThreshForFloatFlag)
            create_parameterfile(tempdir, MPHvalidPixelExpression, MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS)

    execution(tempfolder)
import os
import glob
import tempfile

from qgis.processing import alg

@alg(
    name="pg04waterqualityparametersmerismph",
    label=alg.tr("PG04_WaterQualityParameters_MERIS_MPH"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.STRING, name="MPHvalidPixelExpression", label="Valid pixel expression", default="not (l1p_flags.CC_LAND or l1_flags.INVALID or l1p_flags.CC_CLOUD or l1p_flags.CC_CLOUD_BUFFER or l1p_flags.CC_CLOUD_SHADOW)")
@alg.input(type=alg.NUMBER, name="MPHcyanoMaxValue", label="Cyano maximum value", default=1000, minValue=0)
@alg.input(type=alg.NUMBER, name="MPHchlThreshForFloatFlag", label="CHL threshold for float flag", default=350, minValue=0)
@alg.input(type=alg.BOOL, name="MPHexportMph", label="Export MPH", default=False)

@alg.output(type=alg.FOLDER, name='output', label='Output folder')
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(Input_folder, outpref, Output_folder, res, mem):
    MPHexportMph=False
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

    def create_parameterfile(tempdir, MPHvalidPixelExpression, MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS, MPHexportMph):
        with open(tempdir + "WaterQualityParameters04.txt", "w") as text_file:
            text_file.write('mphValidPixelExpression='+ MPHvalidPixelExpression + '\n')
            text_file.write('mphCyanoMaxValue='+ MPHcyanoMaxValueS + '\n') 
            text_file.write('mphChlThreshForFloatFlag='+ MPHchlThreshForFloatFlagS + '\n')
            text_file.write('mphExportMph='+ str(MPHexportMph).lower() + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS = convert(MPHcyanoMaxValue, MPHchlThreshForFloatFlag)
            create_parameterfile(tempdir, MPHvalidPixelExpression, MPHcyanoMaxValueS, MPHchlThreshForFloatFlagS, MPHexportMph)

    execution(tempfolder)
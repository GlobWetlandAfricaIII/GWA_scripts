import os
import glob
import tempfile

from qgis.processing import alg


# TODO enum should be the new version of 'selection'. Not sure on 'options' though 
@alg(
    name="pg04waterqualityparameterscoastcolourl2r",
    label=alg.tr("PG04_WaterQualityParameters_CoastColour_L2R"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.BOOL, name="SnTMap", label="Use SnT map", default=False)
@alg.input(type=alg.NUMBER, name="AverageSalinity", label="Average Salinity", 
           default=1, minValue=0)
@alg.input(type=alg.NUMBER, name="AverageTemperature", 
           label="Average Temperature", default=15, minValue=0)
@alg.input(type=alg.BOOL, name="ExtremeCaseMode", label="Use extreme case mode", default=False)
@alg.input(type=alg.STRING, name="LandExpression", label="Land expression", 
           default="l1p_flags.CC_LAND")
@alg.input(type=alg.STRING, name="SnowIceExpression", label="Snow ice expression",
           default="l1p_flags.CC_CLOUD or l1p_flags.CC_SNOW_ICE")
@alg.input(type=alg.BOOL, name="L2RToa", label="Calculate L2R TOA", default=False)
@alg.input(type=alg.ENUM, name="L2RReflectAs", label="Reflection as", options=["RADIANCE_REFLECTANCES", "IRRADIANCE_REFLECTANCES"])
@alg.output(type=alg.FOLDER, name="Output_folder", label="Output directory")
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(SnTMap, AverageSalinity, AverageTemperature, ExtremeCaseMode, LandExpression, SnowIceExpression, L2RToa, L2RReflectAs):
    tempfolder = 'wq_scripts_'
    SnTMap = False

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            progress.setConsoleInfo('ERROR: Parameter folder could not be found. Please execute step 1 first!')
            return True
            
    def convert(L2RReflectAs, AverageSalinity, AverageTemperature):
        if L2RReflectAs == 0:
            L2RReflectAsS = 'RADIANCE_REFLECTANCES'
        else:
            L2RReflectAsS = 'IRRADIANCE_REFLECTANCES'
        AverageSalinityS = '%.2f' % AverageSalinity
        AverageTemperatureS = '%.2f' % AverageTemperature
        
        return L2RReflectAsS, AverageSalinityS, AverageTemperatureS

    def create_parameterfile(tempdir, SnTMap, AverageSalinityS, AverageTemperatureS, ExtremeCaseMode, LandExpression, SnowIceExpression, L2RToa, L2RReflectAsS):
        with open(tempdir + "WaterQualityParameters02.txt", "w") as text_file:
            text_file.write('snTMap='+ str(SnTMap).lower() + '\n')
            text_file.write('averageSalinity='+ AverageSalinityS + '\n') 
            text_file.write('averageTemperature='+ AverageTemperatureS + '\n')
            text_file.write('extremeCaseMode='+ str(ExtremeCaseMode).lower() + '\n')
            text_file.write('landExpression='+ LandExpression + '\n')
            text_file.write('snowIceExpression='+ SnowIceExpression + '\n')
            text_file.write('l2RToab='+ str(L2RToa).lower() + '\n')
            text_file.write('l2RReflectAs='+ L2RReflectAsS + '\n')


    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            L2RReflectAsS, AverageSalinityS, AverageTemperatureS = convert(L2RReflectAs, AverageSalinity, AverageTemperature)
            create_parameterfile(tempdir, SnTMap, AverageSalinityS, AverageTemperatureS, ExtremeCaseMode, LandExpression, SnowIceExpression, L2RToa, L2RReflectAsS)

    execution(tempfolder)
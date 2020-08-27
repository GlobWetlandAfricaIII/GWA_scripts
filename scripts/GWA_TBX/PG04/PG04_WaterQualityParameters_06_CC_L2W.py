import os
import glob
import tempfile

from qgis.processing import alg

@alg(
    name="pg04waterqualityparameterscoastcolourl2w",
    label=alg.tr("PG04_WaterQualityParameters_CoastColour_L2W"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.STRING, name="invalidPixelExpression", label="Invalid pixel expression", default="l2r_flags.INPUT_INVALID")
@alg.input(type=alg.BOOL, name="outputAOT550", label="write AOT 550", default=False)
@alg.input(type=alg.ENUM, name="owtType", label="Select OWT type", default="GLASS_6C_NORMALIZED", options=["INLAND", "COASTAL", "INLAND_NO_BLUE_BAND", "GLASS_5C", "GLASS_6C", "GLASS_6C_NORMALIZED"])
@alg.output(type=alg.FOLDER, name='output', label='Output folder')
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(Input_folder, outpref, Output_folder, res, mem):

    outputAOT550=False
    tempfolder = 'wq_scripts_'

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            progress.setConsoleInfo('ERROR: Parameter folder could not be found. Please execute step 1 first!')
            return True

    def convert(owtType):
        if owtType == 0:
            owtTypeS = 'INLAND'
        if owtType == 1:
            owtTypeS = 'COASTAL'
        if owtType == 2:
            owtTypeS = 'INLAND_NO_BLUE_BAND'
        if owtType == 3:
            owtTypeS = 'GLASS_5C'
        if owtType == 4:
            owtTypeS = 'GLASS_6C'
        if owtType == 5:
            owtTypeS = 'GLASS_6C_NORMALIZED'
        return owtTypeS

    def create_parameterfile(tempdir, invalidPixelExpression, outputAOT550, owtTypeS):
        with open(tempdir + "WaterQualityParameters05.txt", "w") as text_file:
            text_file.write('L2WinvalidPixelExpression='+ invalidPixelExpression + '\n')
            text_file.write('L2WoutputAOT550='+ str(outputAOT550).lower() + '\n') 
            text_file.write('L2WowtType='+ owtTypeS + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            owtTypeS = convert(owtType)
            create_parameterfile(tempdir, invalidPixelExpression, outputAOT550, owtTypeS)

    execution(tempfolder)
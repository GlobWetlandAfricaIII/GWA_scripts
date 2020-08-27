import os
import glob
import tempfile

from qgis.processing import alg

@alg(
    name="pg04waterqualityparametersfubwater",
    label=alg.tr("PG04_WaterQualityParameters_FUB_Water"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.BOOL, name="ComputeCHL", label="Compute CHL", default=True)
@alg.input(type=alg.BOOL, name="ComputeYS", label="Compute YS", default=True)
@alg.input(type=alg.BOOL, name="ComputeTSM", label="Compute TSM", default=True)
@alg.input(type=alg.BOOL, name="ComputeAtmCorr", label="Atmospheric correction", default=True)
@alg.input(type=alg.BOOL, name="CheckWhetherSuspectIsValid", label="Check whether suspect is valid", default=True)
@alg.input(type=alg.STRING, name="FubExpression", label="Expression", default="(radiance_13- radiance_8)/(radiance_8+ radiance_13) &lt; 0.05 and radiance_13 &lt; 50 and not l1p_flags.CC_CLOUD_SHADOW and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_LAND and not l1_flags.INVALID")

@alg.output(type=alg.FOLDER, name='output', label='Output folder')
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(Input_folder, outpref, Output_folder, res, mem):
    TiePoints=True
    L1Flags=True
    OutputToar=False
    CorrectionSurfaceS='ALL_SURFACES'
    ComputeCHL=True
    ComputeYS=True
    ComputeTSM=True
    ComputeAtmCorr=True

    import os
    import glob
    import tempfile

    tempfolder = 'wq_scripts_'

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            progress.setConsoleInfo('ERROR: Parameter folder could not be found. Please execute step 1 first!')
            return True


    def create_parameterfile(tempdir, ComputeCHL, ComputeYS, ComputeTSM, ComputeAtmCorr, CheckWhetherSuspectIsValid, FubExpression,TiePoints, L1Flags, OutputToar, CorrectionSurfaceS):
        with open(tempdir + "WaterQualityParameters03.txt", "w") as text_file:
            text_file.write('tiePoints='+ str(TiePoints).lower() + '\n')
            text_file.write('l1Flags='+ str(L1Flags).lower() + '\n') 
            text_file.write('outputToar='+ str(OutputToar).lower() + '\n')
            text_file.write('correctionSurface='+ CorrectionSurfaceS + '\n')
            text_file.write('fUBcomputeCHL='+ str(ComputeCHL).lower() + '\n')
            text_file.write('fUBcomputeYS='+ str(ComputeYS).lower() + '\n') 
            text_file.write('fUBcomputeTSM='+ str(ComputeTSM).lower() + '\n')
            text_file.write('fUBcomputeAtmCorr='+ str(ComputeAtmCorr).lower() + '\n')
            text_file.write('fUBcheckWhetherSuspectIsValid='+ str(CheckWhetherSuspectIsValid).lower() + '\n')
            text_file.write('fUBexpression='+ FubExpression + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            create_parameterfile(tempdir, ComputeCHL, ComputeYS, ComputeTSM, ComputeAtmCorr, CheckWhetherSuspectIsValid, FubExpression, TiePoints, L1Flags, OutputToar, CorrectionSurfaceS)

    execution(tempfolder)
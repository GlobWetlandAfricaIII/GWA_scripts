from qgis.processing import alg


@alg(
    name="pg04waterqualityparametersmerisrayleighcorrection",
    label=alg.tr("PG04_WaterQualityParameters_MERIS_RayleighCorrection"),
    group="bc",
    group_label=alg.tr("BC")
)

@alg.input(type=alg.BOOL, name="TiePoints", label="Copy all tie points", default=True)
@alg.input(type=alg.BOOL, name="L1Flags", label="Copy L1 flags", default=True)
@alg.input(type=alg.BOOL, name="OutputToar", label="Output TOA", default=False)
@alg.input(type=alg.ENUM, name="CorrectionSurface", label="Correction Surface", options=["ALL_SURFACES", "Land", "Water"])


@alg.input(type=alg.FOLDER_DEST, name="output_folder", label="should be removed")
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()
    # remove output folder


def main(input_folder, start_month, end_month, year, res, mem, output_folder):


    TiePoints=True
    L1Flags=True
    OutputToar=False
    CorrectionSurface='ALL_SURFACES'

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
            
    def convert(CorrectionSurface):
        if CorrectionSurface == 0:
            CorrectionSurfaceS = 'ALL_SURFACES'
        if CorrectionSurface == 1:
            CorrectionSurfaceS = 'LAND'
        if CorrectionSurface == 2:
            CorrectionSurfaceS = 'WATER'
        return CorrectionSurfaceS

    def create_parameterfile(tempdir, TiePoints, L1Flags, OutputToar, CorrectionSurfaceS):
        with open(tempdir + "WaterQualityParameters03.txt", "w") as text_file:
            text_file.write('tiePoints='+ str(TiePoints).lower() + '\n')
            text_file.write('l1Flags='+ str(L1Flags).lower() + '\n') 
            text_file.write('outputToar='+ str(OutputToar).lower() + '\n')
            text_file.write('correctionSurface='+ CorrectionSurfaceS + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            CorrectionSurfaceS = convert(CorrectionSurface)
            create_parameterfile(tempdir, TiePoints, L1Flags, OutputToar, CorrectionSurfaceS)

    execution(tempfolder)
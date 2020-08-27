##Define_output_CRS=crs

import os
import glob
import tempfile

from qgis.processing import alg

@alg(
    name="pg04waterqualityparameterscrs",
    label=alg.tr("PG04_WaterQualityParameters_CRS_select"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.CRS, name="Define_output_CRS", label="Define_output_CRS")
@alg.output(type=alg.FOLDER, name='output', label='Output folder')

def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(Input_folder, outpref, Output_folder, res, mem):

    tempfolder = 'wq_scripts_'

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            return False
        except IndexError:
            progress.setConsoleInfo('ERROR: Parameter folder could not be found. Please execute step 1 first!')
            return True

    def create_parameterfile(tempdir, Define_output_CRS):
        with open(tempdir + "WaterQualityParameters06.txt", "w") as text_file:
            text_file.write('crs='+ Define_output_CRS + '\n')

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0] + '/'
            create_parameterfile(tempdir, Define_output_CRS)

    execution(tempfolder)
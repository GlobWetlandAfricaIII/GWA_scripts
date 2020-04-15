import os
import glob
import tempfile

from qgis.processing import alg


@alg(
    name="pg04waterqualityparameters04olcicrsselect",
    label=alg.tr("PG04_WaterQualityParameters_04_OLCI_CRS_select"),
    group="bc",
    group_label=alg.tr("BC"),
)
@alg.input(type=alg.CRS, name="Define_output_CRS", label="Define_output_CRS")
@alg.output(type=alg.FOLDER, name="output", label="Output folder")
def pg04waterqualityparameters04olcicrsselect(
    instance, parameters, context, feedback, inputs
):
    """
    Optical-SAR Water and Wetness Fusion
    """

    Define_output_CRS = instance.parameterAsString(
        parameters, "Define_output_CRS", context
    )
    tempfolder = "wq_scripts_"

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return False
        except IndexError:
            feedback.pushConsoleInfo(
                "ERROR: Parameter folder could not be found. Please execute step 1 first!"
            )
            return True

    def create_parameterfile(tempdir, Define_output_CRS):
        with open(tempdir + "WaterQualityParametersOLCI04.txt", "w") as text_file:
            text_file.write("crs=" + Define_output_CRS + "\n")

    def execution(tempfolder):
        if folder_check(tempfolder):
            return
        else:
            tempdir = (
                glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
                + "/"
            )
            create_parameterfile(tempdir, Define_output_CRS)

    execution(tempfolder)

    return {
        "output": glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
    }

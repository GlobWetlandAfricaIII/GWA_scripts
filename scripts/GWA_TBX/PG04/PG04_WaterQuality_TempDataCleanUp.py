import glob
import os

from qgis.processing import alg

@alg(
    name="pg04waterqualityworkflowtempdatacleanup",
    label=alg.tr("PG04_WaterQualityWorkflow_TempDataCleanUp"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.output(type=alg.FOLDER, name="Output_folder", label="Output directory")
def algorithm(instance, parameters, context, feedback, inputs):
    """
    PG04_WaterQualityWorkflow_TempDataCleanUp
    """
    #main()
    pass


def main():
    import shutil
    import tempfile

    tempfolder = 'wq_scripts_'
    tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
    shutil.rmtree(tempdir)
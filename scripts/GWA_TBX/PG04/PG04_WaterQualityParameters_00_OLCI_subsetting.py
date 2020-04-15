import os
import glob

import tempfile
from qgis.processing import alg
from qgis import processing
from qgis.core import *
from PyQt5.QtCore import *


@alg(
    name="pg04waterqualitparameters00olcisubsetting",
    label=alg.tr("PG04_WaterQualityParameters_00_OLCI_Subsetting"),
    group="bc",
    group_label=alg.tr("BC"),
)
@alg.input(
    type=alg.BOOL,
    name="dontsubset",
    label="Don't subset products - In this case no shapefile is needed",
    default=False,
)
@alg.input(type=alg.FILE, name="Input_vector", label="Input vector", optional=True)
@alg.output(type=alg.FOLDER, name="Output_folder", label="Output_folder")
def pg04waterqualitparameters00olcisubsetting(
    instance, parameters, context, feedback, inputs
):
    """
    pg04waterqualitparameters00olcisubsetting
    """
    tempfolder = "wq_scripts_"
    feedback.pushConsoleInfo(os.path.realpath(__file__))
    Input_vector1 = instance.parameterAsVectorLayer(parameters, "Input_vector", context)
    dontsubset = instance.parameterAsBool(parameters, "dontsubset", context)
    Input_vector = instance.parameterAsString(parameters, "Input_vector", context)

    def folder_create(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return tempdir
        except:
            feedback.pushConsoleInfo(
                "Temporary folder:"
                + tempfolder
                + " does not exist and will be created."
            )
            tempfile.mkdtemp(prefix=tempfolder)
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return tempdir

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return False
        except IndexError:
            feedback.pushConsoleInfo(
                "ERROR: Temporary folder:"
                + tempfolder
                + " cloud not be created. Check for administration rights to create folder."
            )
            return True

    def create_parameterfile(tempdir, dontsubset):
        with open(tempdir + "WaterQualityParametersOLCI00.txt", "w") as text_file:
            text_file.write("dontsubset=" + str(dontsubset).lower() + "\n")

    def create_subset_parameterfile(tempdir, dontsubset, wkt_string):
        with open(tempdir + "WaterQualityParametersOLCI00.txt", "w") as text_file:
            text_file.write("wkt=" + str(wkt_string) + "\n")
            text_file.write("dontsubset=" + str(dontsubset).lower() + "\n")

    def get_wkt(Input_vector):
        inlayer = Input_vector1
        for feat in inlayer.getFeatures():
            geom = feat.geometry()
            feedback.setProgressText(geom.asWkt().upper())
            wkt_string = geom.asWkt().upper()
            print(wkt_string)
        return wkt_string

    def execution(tempfolder, dontsubset):
        tempdir = folder_create(tempfolder) + "/"
        if folder_check(tempfolder):
            return
        else:
            tempdir = (
                glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
                + "/"
            )
            create_parameterfile(tempdir, dontsubset)

    def subset_execution(tempfolder, dontsubset, Input_vector):
        tempdir = folder_create(tempfolder) + "/"
        if folder_check(tempfolder):
            return
        else:
            tempdir = (
                glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
                + "/"
            )
            wkt_string = get_wkt(Input_vector)
            create_subset_parameterfile(tempdir, dontsubset, wkt_string)

    if dontsubset:
        execution(tempfolder, dontsubset)
    else:
        subset_execution(tempfolder, dontsubset, Input_vector)
    Output_folder = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
    return {"Output_folder": Output_folder}

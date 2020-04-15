##Output_folder=folder

import os
import glob
import tempfile
import fnmatch
import subprocess
from os import walk
import shutil

from qgis.processing import alg
from processing.core.ProcessingConfig import ProcessingConfig


@alg(
    name="pg04waterqualityworkflowsnapgraphprocessor",
    label=alg.tr("PG04_WaterQualityWorkflow_SNAP_graphProcessor"),
    group="bc",
    group_label=alg.tr("BC"),
)
@alg.input(
    type=alg.FILE,
    name="Input_files",
    label="Select files to be processed",
    advanced=True,
    optional=True,
)
@alg.input(
    type=alg.FILE, name="Input_folder", label="Input folder", behavior=1, optional=True
)
@alg.input(
    type=alg.STRING,
    name="ext",
    label="Define filename extension of input products (e.g. SEN3 or dim)",
    default="SEN3",
)
@alg.input(
    type=alg.NUMBER,
    name="mem",
    label="Insert the amount of RAM (inGB) available for processing",
    default=1,
    minValue=1,
    maxValue=31,
    advanced=True,
)
@alg.input(type=alg.FOLDER_DEST, name="Output_folder", label="Output folder")
def pg04waterqualityworkflowsnapgraphprocessor(
    instance, parameters, context, feedback, inputs
):
    """
    PG04_WaterQualityWorkflow_SNAP_graphProcessor
    """

    ext = instance.parameterAsString(parameters, "ext", context)
    mem = instance.parameterAsEnum(parameters, "mem", context)
    Output_folder = instance.parameterAsString(parameters, "Output_folder", context)
    Output_folder = Output_folder.replace("\\", "/") + "/"
    Input_folder = instance.parameterAsString(parameters, "Input_folder", context)
    input_folder = Input_folder.replace("\\", "/") + "/"
    # feedback.pushConsoleInfo(ProcessingConfig.settings.__repr__())
    snap_path = ProcessingConfig.getSetting("SNAP_FOLDER")
    snap_path = snap_path.replace("\\", "/")
    tempfolder = "wq_scripts_"
    param0 = "WaterQualityParametersOLCI00.txt"
    param1 = "WaterQualityParametersOLCI01.txt"
    param2 = "WaterQualityParametersOLCI02.txt"
    param3 = "WaterQualityParametersOLCI03.txt"
    param4 = "WaterQualityParametersOLCI04.txt"
    NN_PATH = ProcessingConfig.getSetting("SCRIPTS_FOLDERS")

    def execution(
        tempfolder,
        Output_folder,
        input_folder,
        ext,
        snap_path,
        param0,
        param1,
        param2,
        param3,
        param4,
        NN_PATH,
    ):

        # Reformating inputs and outputs
        NN_PATH = NN_PATH.replace("\\", "/") + "/GWA_TBX/PG04/olci_experiment"
        feedback.setProgressText("NNPath is:" + NN_PATH)
        # filenames = [name for name in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, name))]
        # input_files_list = []
        # for x in filenames:
        #    input_files_list = input_files_list + (input_folder + ''.join(x)).split()

        if ext == "SEN3":
            input_files_list = [file for file in locate("*." + ext, input_folder)]
        else:
            feedback.setProgressText(str(input_folder))
            input_files_list = [file for file in locate_file("*." + ext, input_folder)]

        if input_files_list == "":
            feedback.setProgressText("ERROR: Input folder not defined!")
            return
        elif Output_folder == "/":
            feedback.setProgressText("ERROR: Output folder not defined!")
            return
        elif folder_check(tempfolder):
            return
        elif not param_check(
            glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0] + "/",
            param0,
            param1,
            param2,
            param3,
            param4,
        ):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            feedback.setProgressText(tempdir)
            tempdir = tempdir.replace("\\", "/") + "/"
            param_results = param_check(tempdir, param0, param1, param2, param3, param4)
            if param_results:
                paramfile = concat_param(
                    tempdir, param0, param1, param2, param3, param4
                )
                if "dontsubset=false" in open(tempdir + param0).read():
                    subset = True
                else:
                    subset = False
            gpt_script = create_graph(tempdir, subset, NN_PATH)
            processing(
                tempdir,
                Output_folder,
                input_files_list,
                snap_path,
                gpt_script,
                paramfile,
            )
            # shutil.rmtree(tempdir)

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return False
        except IndexError:
            feedback.pushConsoleInfo(
                "ERROR: Parameter folder could not be found. Please execute steps 1-9 first!"
            )
            return True

    def folder_create(tempfolder):
        tempfile.mkdtemp(prefix=tempfolder)
        tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
        return tempdir

    def locate(pattern, root_path):
        for path, dirs, files in os.walk(root_path):
            for filename in fnmatch.filter(dirs, pattern):
                yield os.path.join(path, filename)

    def locate_file(pattern, root_path):
        for path, dirs, files in os.walk(root_path):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)

    def create_graph(tempdir, subset, NN_PATH):
        with open(tempdir + "ProcessingGraph.xml", "w") as text_file:
            text_file.write('<graph id="someGraphId">\n')
            text_file.write("  <version>1.0</version>\n")
            text_file.write('    <node id="Read">\n')
            text_file.write("      <operator>Read</operator>\n")
            text_file.write("      <sources/>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <file>${sourceFile}</file>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write("	\n")
            if subset:
                text_file.write('    <node id="Subset">\n')
                text_file.write("      <operator>Subset</operator>\n")
                text_file.write("      <sources>\n")
                text_file.write("          <source>Read</source>\n")
                text_file.write("      </sources>\n")
                text_file.write("      <parameters>\n")
                text_file.write("        <geoRegion>${wkt}</geoRegion>\n")
                text_file.write("        <copyMetadata>true</copyMetadata>\n")
                text_file.write("      </parameters>\n")
                text_file.write("    </node>\n")
                text_file.write("\n")
            text_file.write("\n")
            text_file.write('    <node id="IdePixNode">\n')
            text_file.write("      <operator>Idepix.Sentinel3.Olci</operator>\n")
            text_file.write("      <sources>\n")
            if subset:
                text_file.write("        <sourceProduct>Subset</sourceProduct>\n")
            else:
                text_file.write("        <sourceProduct>Read</sourceProduct>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write(
                "        <!-- leave out refl and rad bands to only join classif flags with the original product later before c2rcc -->\n"
            )
            text_file.write(
                "		<!-- <radianceBandsToCopy>${radBands}</radianceBandsToCopy>\n"
            )
            text_file.write(
                "        <reflBandsToCopy>${reflBands}</reflBandsToCopy> -->\n"
            )
            text_file.write(
                "        <outputSchillerNNValue>${outputCloudProbabilityValue}</outputSchillerNNValue>\n"
            )
            text_file.write(
                "        <computeCloudBuffer>${cloudBuffer}</computeCloudBuffer>\n"
            )
            text_file.write(
                "        <cloudBufferWidth>${cloudBufferWidth}</cloudBufferWidth>\n"
            )
            #        text_file.write('        <computeCloudShadow>false</computeCloudShadow>\n')
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write('    <node id="IdePix">\n')
            text_file.write("      <operator>Merge</operator>\n")
            text_file.write("      <sources>\n")
            if subset:
                text_file.write("          <masterProduct>Subset</masterProduct>\n")
            else:
                text_file.write("          <masterProduct>Read</masterProduct>\n")
            text_file.write("          <idepix>IdePixNode</idepix>\n")
            text_file.write("      </sources>\n")
            text_file.write("    </node>\n")
            #        text_file.write('    <node id="WriteIdePix">\n')
            #        text_file.write('      <operator>Write</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <source>IdePix</source>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #        text_file.write('        <file>${targetbasePath}_IdePix.dim</file>\n')
            #        text_file.write('        <formatName>BEAM-DIMAP</formatName>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')
            text_file.write("\n")
            text_file.write("\n")
            text_file.write('    <node id="Vicarious">\n')
            text_file.write("        <operator>BandMaths</operator>\n")
            text_file.write("        <sources>\n")
            text_file.write("            <olci>IdePix</olci>\n")
            text_file.write("        </sources>\n")
            text_file.write("        <parameters>\n")
            text_file.write("            <targetBands>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa01_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa01_radiance, 913.9812317630276, 1.0e-4) ? NaN : Oa01_radiance / ${Oa01_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>1</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>400</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>15</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa02_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa02_radiance, 877.334085884504, 1.0e-4) ? NaN : Oa02_radiance / ${Oa02_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>2</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>412.5</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa03_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa03_radiance, 796.1270730709657, 1.0e-4) ? NaN : Oa03_radiance / ${Oa03_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>3</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>442.5</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa04_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa04_radiance, 754.9514318397269, 1.0e-4) ? NaN : Oa04_radiance / ${Oa04_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>4</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>490</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa05_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa05_radiance, 661.5928710484877, 1.0e-4) ? NaN : Oa05_radiance / ${Oa05_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>5</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>510</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa06_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa06_radiance, 809.60629854351287, 1.0e-4) ? NaN : Oa06_radiance / ${Oa06_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>6</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>560</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa07_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa07_radiance, 576.1581395426765, 1.0e-4) ? NaN : Oa07_radiance / ${Oa07_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>7</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>620</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa08_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa08_radiance, 574.4398430082947, 1.0e-4) ? NaN : Oa08_radiance / ${Oa08_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>8</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>665</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa09_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa09_radiance, 623.2575185084715, 1.0e-4) ? NaN : Oa09_radiance / ${Oa09_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>9</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>673.75</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>7.5</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa10_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa10_radiance, 506.83326963800937, 1.0e-4) ? NaN : Oa10_radiance / ${Oa10_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>10</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>681.25</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>7.5</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa11_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa11_radiance, 442.70399916451424, 1.0e-4) ? NaN : Oa11_radiance / ${Oa11_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>11</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>708.75</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa12_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa12_radiance, 471.8257776950486, 1.0e-4) ? NaN : Oa12_radiance / ${Oa12_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>12</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>753.75</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>7.5</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa13_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa13_radiance, 491.30539988866076, 1.0e-4) ? NaN : Oa13_radiance / ${Oa13_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>13</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>761.25</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>2.5</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa14_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa14_radiance, 566.9563756557181, 1.0e-4) ? NaN : Oa14_radiance / ${Oa14_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>14</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>764.375</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>3.75</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa15_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa15_radiance, 345.2246211259626, 1.0e-4) ? NaN : Oa15_radiance / ${Oa15_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>15</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>767.5</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>2.5</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa16_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa16_radiance, 347.5104749179445, 1.0e-4) ? NaN : Oa16_radiance / ${Oa16_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>16</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>778.75</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>15.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa17_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa17_radiance, 323.09016273356974, 1.0e-4) ? NaN : Oa17_radiance / ${Oa17_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>17</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>865</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>20.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa18_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa18_radiance, 360.4175960831344, 1.0e-4) ? NaN : Oa18_radiance / ${Oa18_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>18</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>885</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa19_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa19_radiance, 329.54077841481194, 1.0e-4) ? NaN : Oa19_radiance / ${Oa19_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>19</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>900</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>10.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa20_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa20_radiance, 213.89181678649038, 1.0e-4) ? NaN : Oa20_radiance / ${Oa20_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>20</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>940</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>20.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>Oa21_radiance</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>feq(Oa21_radiance, 212.410729767289, 1.0e-4) ? NaN : Oa21_radiance / ${Oa21_vic}</expression>\n"
            )
            text_file.write("                    <unit>mW.m-2.sr-1.nm-1</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write(
                "                    <spectralBandIndex>20</spectralBandIndex>\n"
            )
            text_file.write(
                "                    <spectralWavelength>940</spectralWavelength>\n"
            )
            text_file.write(
                "                    <spectralBandwidth>40.0</spectralBandwidth>\n"
            )
            text_file.write("                </targetBand>\n")
            text_file.write("            </targetBands>\n")
            text_file.write("        </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write(
                '    <node id="Subset2"> <!-- remove the calibrated bands-->\n'
            )
            text_file.write("        <operator>Subset</operator>\n")
            text_file.write("        <sources>\n")
            text_file.write("            <source>IdePix</source>\n")
            text_file.write("        </sources>\n")
            text_file.write("        <parameters>\n")
            text_file.write("            <!-- all bands except radiances -->\n")
            text_file.write(
                "            <sourceBands>altitude,latitude,longitude,detector_index,FWHM_band_1,FWHM_band_2,FWHM_band_3,FWHM_band_4,FWHM_band_5,FWHM_band_6,FWHM_band_7,FWHM_band_8,FWHM_band_9,FWHM_band_10,FWHM_band_11,FWHM_band_12,FWHM_band_13,FWHM_band_14,FWHM_band_15,FWHM_band_16,FWHM_band_17,FWHM_band_18,FWHM_band_19,FWHM_band_20,FWHM_band_21,frame_offset,lambda0_band_1,lambda0_band_2,lambda0_band_3,lambda0_band_4,lambda0_band_5,lambda0_band_6,lambda0_band_7,lambda0_band_8,lambda0_band_9,lambda0_band_10,lambda0_band_11,lambda0_band_12,lambda0_band_13,lambda0_band_14,lambda0_band_15,lambda0_band_16,lambda0_band_17,lambda0_band_18,lambda0_band_19,lambda0_band_20,lambda0_band_21,solar_flux_band_1,solar_flux_band_2,solar_flux_band_3,solar_flux_band_4,solar_flux_band_5,solar_flux_band_6,solar_flux_band_7,solar_flux_band_8,solar_flux_band_9,solar_flux_band_10,solar_flux_band_11,solar_flux_band_12,solar_flux_band_13,solar_flux_band_14,solar_flux_band_15,solar_flux_band_16,solar_flux_band_17,solar_flux_band_18,solar_flux_band_19,solar_flux_band_20,solar_flux_band_21,quality_flags</sourceBands>\n"
            )
            text_file.write("            <copyMetadata>true</copyMetadata>\n")
            text_file.write("        </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write(
                '    <node id="Merged"> <!-- replace with re-calibrated bands, include idepix-->\n'
            )
            text_file.write("        <operator>Merge</operator>\n")
            text_file.write("        <sources>\n")
            text_file.write("            <masterProduct>Subset2</masterProduct>\n")
            text_file.write("<!--			<sourceProducts>vicar,idepx</sourceProducts> -->\n")
            text_file.write("		 	<vicar>Vicarious</vicar>\n")
            text_file.write("			<idepix>IdePix</idepix>\n")
            text_file.write("        </sources>\n")
            text_file.write("        <parameters>\n")
            text_file.write("            <includes>\n")
            text_file.write("                <include>\n")
            text_file.write("                    <productId>vicar</productId>\n")
            text_file.write(
                "                    <namePattern>Oa.*radiance</namePattern>\n"
            )
            text_file.write("					<productId>idepix</productId>\n")
            text_file.write("					<namePattern>pixel_classif_flags</namePattern>\n")
            text_file.write("                </include>\n")
            text_file.write("            </includes>\n")
            text_file.write("        </parameters>\n")
            text_file.write("    </node>\n")

            #        text_file.write('    <node id="WriteVic">\n')
            #        text_file.write('      <operator>Write</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <source>Merged</source>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #        text_file.write('        <file>${targetbasePath}_Vic.dim</file>\n')
            #        text_file.write('        <formatName>BEAM-DIMAP</formatName>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')

            text_file.write('    <node id="C2RCC">\n')
            text_file.write("      <operator>c2rcc.olci</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProduct>Merged</sourceProduct>\n")
            text_file.write(
                "        <!-- <tomsomiStartProduct>${tomsomiStartProduct}</tomsomiStartProduct>\n"
            )
            text_file.write(
                "        <tomsomiEndProduct>${tomsomiEndProduct}</tomsomiEndProduct>\n"
            )
            text_file.write(
                "        <ncepStartProduct>${ncepStartProduct}</ncepStartProduct>\n"
            )
            text_file.write(
                "        <ncepEndProduct>${ncepEndProduct}</ncepEndProduct> -->\n"
            )
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write(
                "        <validPixelExpression>${c2ValidExpression}</validPixelExpression>\n"
            )
            text_file.write("        <!-- set to 1.0 default is 35.0 -->\n")
            text_file.write("		      <salinity>${averageSalinity}</salinity>\n")
            text_file.write(
                "        <temperature>${averageTemperature}</temperature>\n"
            )
            text_file.write("        <ozone>330.0</ozone>\n")
            text_file.write("        <press>1000.0</press>\n")
            text_file.write("        <TSMfakBpart>1.72</TSMfakBpart>\n")
            text_file.write("        <TSMfakBwit>3.1</TSMfakBwit>\n")
            text_file.write("        <CHLexp>1.04</CHLexp>\n")
            text_file.write("        <CHLfak>21.0</CHLfak>\n")
            text_file.write(
                "        <alternativeNNPath>" + NN_PATH + "</alternativeNNPath>\n"
            )
            text_file.write("        <thresholdRtosaOOS>0.005</thresholdRtosaOOS>\n")
            text_file.write(
                "        <thresholdAcReflecOos>0.1</thresholdAcReflecOos>\n"
            )
            text_file.write(
                "        <thresholdCloudTDown865>0.955</thresholdCloudTDown865>\n"
            )
            text_file.write("        <outputAsRrs>false</outputAsRrs>\n")
            text_file.write(
                "        <deriveRwFromPathAndTransmittance>false</deriveRwFromPathAndTransmittance>\n"
            )
            text_file.write("        <useEcmwfAuxData>true</useEcmwfAuxData>\n")
            text_file.write("        <outputRtoa>true</outputRtoa>\n")
            text_file.write("        <outputRtosaGc>false</outputRtosaGc>\n")
            text_file.write("        <outputRtosaGcAann>false</outputRtosaGcAann>\n")
            text_file.write("        <outputRpath>false</outputRpath>\n")
            text_file.write("        <outputTdown>false</outputTdown>\n")
            text_file.write("        <outputTup>false</outputTup>\n")
            text_file.write("        <outputAcReflectance>true</outputAcReflectance>\n")
            text_file.write("        <outputRhown>false</outputRhown>\n")
            text_file.write("        <outputOos>false</outputOos>\n")
            text_file.write("        <outputKd>false</outputKd>\n")
            text_file.write(
                "        <outputUncertainties>false</outputUncertainties>\n"
            )
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            #        text_file.write('    <node id="WriteC2RCC">\n')
            #        text_file.write('      <operator>Write</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <source>C2RCC</source>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #        text_file.write('        <file>${targetbasePath}_C2RCC.dim</file>\n')
            #        text_file.write('        <formatName>BEAM-DIMAP</formatName>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')

            text_file.write('    <node id="TSM_NECHAD">\n')
            text_file.write("        <operator>BandMaths</operator>\n")
            text_file.write("        <sources>\n")
            text_file.write("            <c2rcc>C2RCC</c2rcc>\n")
            text_file.write("        </sources>\n")
            text_file.write("        <parameters>\n")
            text_file.write("            <targetBands>\n")
            text_file.write("                <targetBand>\n")
            text_file.write("                    <name>tsm_nechad_865</name>\n")
            text_file.write("                    <type>float32</type>\n")
            text_file.write(
                "                    <expression>not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not pixel_classif_flags.IDEPIX_CLOUD and not pixel_classif_flags.IDEPIX_CLOUD_BUFFER and not c2rcc_flags.Rtosa_OOS and not c2rcc_flags.Rtosa_OOR and not c2rcc_flags.Rhow_OOR and not c2rcc_flags.Cloud_risk and not c2rcc_flags.Iop_OOR  ? 2920 * rhow_17 / (1.0 -  rhow_17/0.21149):NaN</expression>\n"
            )
            text_file.write("                    <unit>g m^-3</unit>\n")
            text_file.write("                    <noDataValue>NaN</noDataValue>\n")
            text_file.write("                </targetBand>\n")
            text_file.write("            </targetBands>\n")
            text_file.write("        </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write("\n")

            text_file.write('    <node id="C2RCC_Subset">\n')
            text_file.write("        <operator>Subset</operator>\n")
            text_file.write("        <sources>\n")
            text_file.write("            <source>C2RCC</source>\n")
            text_file.write("        </sources>\n")
            text_file.write("        <parameters>\n")
            text_file.write(
                "            <sourceBands>conc_tsm,conc_chl,rtoa_17,rtoa_8,rhow_17,quality_flags,c2rcc_flags,pixel_classif_flags</sourceBands>\n"
            )
            text_file.write("            <copyMetadata>true</copyMetadata>\n")
            text_file.write("        </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write("\n")
            text_file.write('    <node id="MphChl">\n')
            text_file.write("      <operator>MphChl</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProduct>IdePix</sourceProduct>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write(
                "        <validPixelExpression>${mphValidExpression}</validPixelExpression>\n"
            )
            text_file.write(
                "        <cyanoMaxValue>${mphCyanoMaxValue}</cyanoMaxValue>\n"
            )
            text_file.write(
                "        <chlThreshForFloatFlag>${mphChlThreshForFloatFlag}</chlThreshForFloatFlag>\n"
            )
            text_file.write("        <exportMph>false</exportMph>\n")
            # text_file.write('        <exportMph>${mphExportMph}</exportMph>\n')
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            #        text_file.write('    <node id="WriteMphChl">\n')
            #        text_file.write('      <operator>Write</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <source>MphChl</source>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #        text_file.write('        <file>${targetbasePath}_MphChl.dim</file>\n')
            #        text_file.write('        <formatName>BEAM-DIMAP</formatName>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')
            text_file.write("\n")

            text_file.write('    <node id="C2RCC_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>C2RCC_Subset</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="MphChl_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>MphChl</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="TSM_Nechad_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>TSM_NECHAD</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write("\n")

            text_file.write('    <node id="C2RCC_tsm_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>C2RCC_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>tsm</name>\n")
            text_file.write("            <type>float32</type>\n")
            text_file.write(
                "            <expression>not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not pixel_classif_flags.IDEPIX_CLOUD and not pixel_classif_flags.IDEPIX_CLOUD_BUFFER and not c2rcc_flags.Rtosa_OOS and not c2rcc_flags.Rtosa_OOR and not c2rcc_flags.Rhow_OOR and not c2rcc_flags.Cloud_risk and not c2rcc_flags.Iop_OOR ?  conc_tsm : NaN</expression>\n"
            )
            text_file.write("			       <!-- <expression>conc_tsm</expression>-->\n")
            text_file.write(
                "            <description>Total suspended matter dry weight concentration.</description>\n"
            )
            text_file.write("            <unit>g m^-3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="C2RCC_chl_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>C2RCC_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>chl</name>\n")
            text_file.write("            <type>float32</type>\n")
            text_file.write(
                "           <expression>not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not pixel_classif_flags.IDEPIX_CLOUD and not pixel_classif_flags.IDEPIX_CLOUD_BUFFER and not c2rcc_flags.Rtosa_OOS and not c2rcc_flags.Rtosa_OOR and not c2rcc_flags.Rhow_OOR and not c2rcc_flags.Cloud_risk and not c2rcc_flags.Iop_OOR ? conc_chl : NaN</expression> \n"
            )
            text_file.write("			       <!-- <expression>conc_chl</expression>-->\n")
            text_file.write(
                "            <description>Chlorophyll 2 content.</description>\n"
            )
            text_file.write("            <unit>mg/m^3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            #        text_file.write('    <node id="C2RCC_tsm_nechad_reformat">\n')
            #        text_file.write('      <operator>BandMaths</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <sourceProducts>C2RCC_reproj</sourceProducts>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #       text_file.write('        <targetBands>\n')
            #       text_file.write('          <targetBand>\n')
            #        text_file.write('            <name>tsm_nechad</name>\n')
            #        text_file.write('            <type>float32</type>\n')
            #       text_file.write('            <!-- <expression>not quality_flags.invalid and (not pixel_classif_flags.IDEPIX_LAND or quality_flags.fresh_inland_water) and not pixel_classif_flags.IDEPIX_CLOUD and not pixel_classif_flags.IDEPIX_CLOUD_BUFFER and not c2rcc_flags.Rtosa_OOS and not c2rcc_flags.Rtosa_OOR and not c2rcc_flags.Rhow_OOR and not c2rcc_flags.Cloud_risk and not c2rcc_flags.Iop_OOR ? conc_chl : NaN</expression> -->\n')
            #       text_file.write('			       <expression>tsm_nechad_865</expression>\n')
            #       text_file.write('            <description>suspended sediment concentration derived by Nechad et al. 2010 algorithm</description>\n')
            #       text_file.write('            <unit>mg/m^3</unit>\n')
            #       text_file.write('          </targetBand>\n')
            #       text_file.write('        </targetBands>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')
            text_file.write("\n")

            text_file.write('    <node id="MphChl_chl_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>MphChl_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>chl_eutrophic</name>\n")
            text_file.write("            <type>float32</type>\n")
            text_file.write(
                "             <!--<expression>!l1_flags.INVALID or !mph_chl_flags.mph_floating ? chl : NaN</expression>-->\n"
            )
            text_file.write("            <expression>chl</expression>\n")
            text_file.write(
                "            <description>Chlorophyll 2 content</description> \n"
            )
            text_file.write("            <unit>mg/m^3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('   <node id="MphChl_floatveg_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>MphChl_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>floating_vegetation</name>\n")
            text_file.write("            <type>int8</type>\n")
            text_file.write(
                "            <!-- <expression>!l1p_flags.CC_COASTLINE and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_CLOUD_SHADOW ? floating_vegetation : NaN</expression> -->\n"
            )
            text_file.write("		         <expression>floating_vegetation</expression>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write("	\n")

            text_file.write('    <node id="finalMergeNode">\n')
            text_file.write("      <operator>Merge</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write(
                "          <masterProduct>MphChl_chl_reformat</masterProduct>\n"
            )
            text_file.write("          <mph2>MphChl_floatveg_reformat</mph2>\n")
            text_file.write("          <c2rcc>C2RCC_tsm_reformat</c2rcc>\n")
            text_file.write("          <c2rcc_chl>C2RCC_chl_reformat</c2rcc_chl>\n")
            text_file.write("          <c2rcc_tsm_n>TSM_Nechad_reproj</c2rcc_tsm_n>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("          <includes>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>masterProduct</productId>\n")
            text_file.write("                  <name>chl_eutrophic</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>c2rcc_chl</productId>\n")
            text_file.write("                  <name>chl</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>c2rcc</productId>\n")
            text_file.write("                  <name>tsm</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>c2rcc_tsm_n</productId>\n")
            text_file.write("                  <name>tsm_nechad_865</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>mph2</productId>\n")
            text_file.write("                  <name>floating_vegetation</name>\n")
            text_file.write("              </include>\n")
            text_file.write("          </includes>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write('    <node id="WriteWQ">\n')
            text_file.write("      <operator>Write</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>finalMergeNode</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <file>${targetbasePath}_WQ.dim</file>\n")
            text_file.write("        <formatName>BEAM-DIMAP</formatName>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            #        text_file.write('    <node id="WriteWQGeoTiff">\n')
            #        text_file.write('      <operator>Write</operator>\n')
            #        text_file.write('      <sources>\n')
            #        text_file.write('        <source>finalMergeNode</source>\n')
            #        text_file.write('      </sources>\n')
            #        text_file.write('      <parameters>\n')
            #        text_file.write('        <file>${targetbasePath}_WQ.tif</file>\n')
            #        text_file.write('        <formatName>GeoTiff</formatName>\n')
            #        text_file.write('      </parameters>\n')
            #        text_file.write('    </node>\n')
            text_file.write("</graph>\n")
        gpt_script = tempdir + "ProcessingGraph.xml"
        return gpt_script

    def param_check(tempdir, param0, param1, param2, param3, param4):
        if (
            os.path.isfile(tempdir + param0)
            & os.path.isfile(tempdir + param1)
            & os.path.isfile(tempdir + param2)
            & os.path.isfile(tempdir + param3)
            & os.path.isfile(tempdir + param4)
        ):
            return True
        else:
            if not os.path.isfile(tempdir + param0):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 1 missing. Please execute step 1 first!"
                )
            if not os.path.isfile(tempdir + param1):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 1 missing. Please execute step 1-2 first!"
                )
            if not os.path.isfile(tempdir + param2):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 2 missing. Please execute steps 1-3 first!"
                )
            if not os.path.isfile(tempdir + param3):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 3 missing. Please execute step 1-4 first!"
                )
            if not os.path.isfile(tempdir + param4):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 4 missing. Please execute step 1-5 first!"
                )
            return False

    def concat_param(tempdir, param0, param1, param2, param3, param4):
        filenames = [
            tempdir + param0,
            tempdir + param1,
            tempdir + param2,
            tempdir + param3,
            tempdir + param4,
        ]
        paramfile = tempdir + "params.properties"
        with open(paramfile, "w") as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
        return paramfile

    def processing(
        tempdir, Output_folder, input_files_list, snap_path, gpt_script, paramfile
    ):
        # Main script
        # files = []
        # for (dirpath, dirnames, filenames) in walk(input_folder):
        # files.extend(filenames)

        if input_files_list == []:
            feedback.setProgressText("WARNING: Input folder empty!")

        for n in range(0, len(input_files_list)):
            inputfile = input_files_list[n]
            filename = inputfile.split("/")[len(inputfile.split("/")) - 1]
            ext = filename.split(".", 1)[1]
            ext_len = len(ext) + 1
            cmnd = (
                '"'
                + snap_path
                + '/bin/gpt.exe" "'
                + gpt_script
                + '"'
                + ' -p "'
                + paramfile
                + '" '
                + ' -PsourceFile="'
                + inputfile
                + '" -PtargetbasePath="'
                + Output_folder
                + filename[:-5]
                + '"'
            )
            feedback.setProgressText('"' + snap_path + '/bin/gpt.exe"')
            feedback.setProgressText(
                '"' + gpt_script + '"' + ' -p "' + paramfile + '" '
            )
            feedback.setProgressText(' -PsourceFile="' + inputfile + '" ')
            feedback.setProgressText(
                '-PtargetbasePath="' + Output_folder + filename[:-ext_len] + '" -e'
            )
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            for line in iter(process.stdout.readline, ""):
                feedback.setProgressText(line)
        # os.remove(gpt_script)

    execution(
        tempfolder,
        Output_folder,
        input_folder,
        ext,
        snap_path,
        param0,
        param1,
        param2,
        param3,
        param4,
        NN_PATH,
    )
    # return({Output_folder: })

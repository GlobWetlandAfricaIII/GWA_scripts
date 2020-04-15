# Definition of inputs and outputs

import os
import glob
import subprocess

from qgis.processing import alg
from processing.core.ProcessingConfig import ProcessingConfig
from os import walk
import tempfile
import shutil


@alg(
    name="pg04waterqualityworkflowgraphprocessorv5",
    label=alg.tr("PG04_WaterQualityWorkflow_graphProcessor_v5"),
    group="bc",
    group_label=alg.tr("BC"),
)
@alg.input(type=alg.FILE, name="Input_files", label="Select files to be processed")
@alg.input(
    type=alg.NUMBER,
    name="mem",
    default=1,
    minValue=1,
    maxValue=31,
    label="Insert the amount of RAM (inGB) available for processing",
)
@alg.input(type=alg.FOLDER_DEST, name="Output_folder", label="folder")
def pg04waterqualityworkflowgraphprocessorv5(
    instance, parameters, context, feedback, inputs
):
    """ PG04_WaterQualityWorkflow_graphProcessor_v5 """
    Output_folder = instance.parameterAsString(parameters, "Output_folder", context)
    Input_files = instance.parameterAsString(parameters, "Input_files", context)

    # Reformating inputs and outputs
    Output_folder = Output_folder.replace("\\", "/") + "/"
    Input_files = Input_files.replace("\\", "/")
    Input_files_list = Input_files.split(";")
    # input_folder = Input_folder.replace("\\", "/")  + "/"
    beam_path = ProcessingConfig.getSetting("BEAM_FOLDER")
    beam_path = beam_path.replace("\\", "/")
    tempfolder = "wq_scripts_"
    param0 = "WaterQualityParameters00.txt"
    param1 = "WaterQualityParameters01.txt"
    param2 = "WaterQualityParameters02.txt"
    param3 = "WaterQualityParameters03.txt"
    param4 = "WaterQualityParameters04.txt"
    param5 = "WaterQualityParameters05.txt"
    param6 = "WaterQualityParameters06.txt"

    def folder_check(tempfolder):
        try:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            return False
        except IndexError:
            feedback.pushConsoleInfo(
                "ERROR: Parameter folder could not be found. Please execute steps 1-7 first!"
            )
            return True

    def folder_create(tempfolder):
        tempfile.mkdtemp(prefix=tempfolder)
        tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[0]
        return tempdir

    def create_graph(tempdir, subset):
        with open(tempdir + "ProcessingGraph.xml", "w") as text_file:
            text_file.write('<graph id="someGraphId">\n')
            text_file.write("  <version>1.0</version>\n")
            text_file.write('  <node id="Read">\n')
            text_file.write("    <operator>Read</operator>\n")
            text_file.write("    <sources/>\n")
            text_file.write("    <parameters>\n")
            text_file.write("      <file>${sourceFile}</file>\n")
            text_file.write("    </parameters>\n")
            text_file.write("  </node>\n")

            if subset:
                text_file.write('  <node id="Subset">\n')
                text_file.write("    <operator>Subset</operator>\n")
                text_file.write("    <sources>\n")
                text_file.write("        <source>Read</source>\n")
                text_file.write("    </sources>\n")
                text_file.write("    <parameters>\n")
                text_file.write("      <geoRegion>${wkt}</geoRegion>\n")
                text_file.write("      <copyMetadata>true</copyMetadata>\n")
                text_file.write("    </parameters>\n")
                text_file.write("  </node>\n")

            text_file.write('  <node id="IdePix">\n')
            text_file.write("    <operator>CoastColour.L1P</operator>\n")
            text_file.write("      <sources>\n")
            if subset:
                text_file.write("        <merisL1B>Subset</merisL1B>\n")
            else:
                text_file.write("        <merisL1B>Read</merisL1B>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <doIcol>${icol}</doIcol>\n")
            text_file.write("        <doCalibration>${calibration}</doCalibration>\n")
            text_file.write("        <doSmile>${smile}</doSmile>\n")
            text_file.write(
                "        <doEqualization>${equalization}</doEqualization>\n"
            )
            text_file.write(
                "        <ccIgnoreSeaIceClimatology>${ignoreSeaIceClim}</ccIgnoreSeaIceClimatology>\n"
            )
            text_file.write(
                "        <ccCloudBufferWidth>${cloudBufferWidth}</ccCloudBufferWidth>\n"
            )
            text_file.write(
                "        <ccCloudScreeningAmbiguous>${cloudScreeningAmbiguous}</ccCloudScreeningAmbiguous>\n"
            )
            text_file.write(
                "        <ccCloudScreeningSure>${cloudScreeningSure}</ccCloudScreeningSure>\n"
            )
            text_file.write(
                "        <ccGlintCloudThresholdAddition>${glintCloudThresholdAddition}</ccGlintCloudThresholdAddition>\n"
            )
            text_file.write(
                "        <ccOutputCloudProbabilityFeatureValue>${outputCloudProbabilityValue}</ccOutputCloudProbabilityFeatureValue>\n"
            )
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="AtmCC">\n')
            text_file.write("      <operator>CoastColour.L2R</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <ccL1P>IdePix</ccL1P>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <doCalibration>false</doCalibration>\n")
            text_file.write("        <doSmile>false</doSmile>\n")
            text_file.write("        <doEqualization>false</doEqualization>\n")
            text_file.write(
                "        <ccIgnoreSeaIceClimatology>false</ccIgnoreSeaIceClimatology>\n"
            )
            text_file.write(
                "        <ccCloudBufferWidth>${cloudBufferWidth}</ccCloudBufferWidth>\n"
            )
            text_file.write(
                "        <ccCloudScreeningAmbiguous>${cloudScreeningAmbiguous}</ccCloudScreeningAmbiguous>\n"
            )
            text_file.write(
                "        <ccCloudScreeningSure>${cloudScreeningSure}</ccCloudScreeningSure>\n"
            )
            text_file.write(
                "        <ccGlintCloudThresholdAddition>${glintCloudThresholdAddition}</ccGlintCloudThresholdAddition>\n"
            )
            text_file.write(
                "        <ccOutputCloudProbabilityFeatureValue>${outputCloudProbabilityValue}</ccOutputCloudProbabilityFeatureValue>\n"
            )
            text_file.write("        <useSnTMap>${snTMap}</useSnTMap>\n")
            text_file.write(
                "        <averageSalinity>${averageSalinity}</averageSalinity>\n"
            )
            text_file.write(
                "        <averageTemperature>${averageTemperature}</averageTemperature>\n"
            )
            text_file.write(
                "        <useExtremeCaseMode>${extremeCaseMode}</useExtremeCaseMode>\n"
            )
            text_file.write(
                "        <landExpression>${landExpression}</landExpression>\n"
            )
            text_file.write(
                "        <cloudIceExpression>${snowIceExpression}</cloudIceExpression>\n"
            )
            text_file.write("        <outputL2RToa>${l2RToab}</outputL2RToa>\n")
            text_file.write(
                "        <outputL2RReflecAs>${l2RReflectAs}</outputL2RReflecAs>\n"
            )
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="MerisBRR">\n')
            text_file.write("      <operator>Meris.Brr</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <merisL1bProduct>IdePix</merisL1bProduct>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write(
                "        <copyAllTiePoints>${tiePoints}</copyAllTiePoints>\n"
            )
            text_file.write("        <copyL1Flags>${l1Flags}</copyL1Flags>\n")
            text_file.write("        <outputToar>${outputToar}</outputToar>\n")
            text_file.write(
                "        <correctionSurface>${correctionSurface}</correctionSurface>\n"
            )
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="FUB">\n')
            text_file.write("      <operator>FUB.Water</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProduct>IdePix</sourceProduct>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <computeCHL>${fUBcomputeCHL}</computeCHL>\n")
            text_file.write("        <computeYS>${fUBcomputeYS}</computeYS>\n")
            text_file.write("        <computeTSM>${fUBcomputeTSM}</computeTSM>\n")
            text_file.write(
                "        <computeAtmCorr>${fUBcomputeAtmCorr}</computeAtmCorr>\n"
            )
            text_file.write(
                "        <checkWhetherSuspectIsValid>${fUBcheckWhetherSuspectIsValid}</checkWhetherSuspectIsValid>\n"
            )
            text_file.write("        <expression>${fUBexpression}</expression>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="MPH">\n')
            text_file.write("      <operator>MERIS.MPH</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <Name>MerisBRR</Name>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write(
                "        <validPixelExpression>${mphValidPixelExpression}</validPixelExpression>\n"
            )
            text_file.write(
                "        <cyanoMaxValue>${mphCyanoMaxValue}</cyanoMaxValue>\n"
            )
            text_file.write(
                "        <chlThreshForFloatFlag>${mphChlThreshForFloatFlag}</chlThreshForFloatFlag>\n"
            )
            text_file.write("        <exportMph>${mphExportMph}</exportMph>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="CC">\n')
            text_file.write("      <operator>CoastColour.L2W</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <ccL2R>IdePix</ccL2R>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <doCalibration>false</doCalibration>\n")
            text_file.write("        <doSmile>false</doSmile>\n")
            text_file.write("        <doEqualization>false</doEqualization>\n")
            text_file.write(
                "        <ccIgnoreSeaIceClimatology>false</ccIgnoreSeaIceClimatology>\n"
            )
            text_file.write(
                "        <ccCloudBufferWidth>${cloudBufferWidth}</ccCloudBufferWidth>\n"
            )
            text_file.write(
                "        <ccCloudScreeningAmbiguous>${cloudScreeningAmbiguous}</ccCloudScreeningAmbiguous>\n"
            )
            text_file.write(
                "        <ccCloudScreeningSure>${cloudScreeningSure}</ccCloudScreeningSure>\n"
            )
            text_file.write(
                "        <ccGlintCloudThresholdAddition>${glintCloudThresholdAddition}</ccGlintCloudThresholdAddition>\n"
            )
            text_file.write("        <useSnTMap>${snTMap}</useSnTMap>\n")
            text_file.write(
                "        <averageSalinity>${averageSalinity}</averageSalinity>\n"
            )
            text_file.write(
                "        <averageTemperature>${averageTemperature}</averageTemperature>\n"
            )
            text_file.write(
                "        <useExtremeCaseMode>${extremeCaseMode}</useExtremeCaseMode>\n"
            )
            text_file.write(
                "        <landExpression>${landExpression}</landExpression>\n"
            )
            text_file.write(
                "        <cloudIceExpression>${snowIceExpression}</cloudIceExpression>\n"
            )
            text_file.write(
                "        <invalidPixelExpression>${L2WinvalidPixelExpression}</invalidPixelExpression>\n"
            )
            text_file.write("        <outputReflec>${l2RToab}</outputReflec>\n")
            text_file.write(
                "        <outputL2WReflecAs>${l2RReflectAs}</outputL2WReflecAs>\n"
            )
            text_file.write("        <outputKdSpectrum>false</outputKdSpectrum>\n")
            text_file.write("        <outputAOT550>${L2WoutputAOT550}</outputAOT550>\n")
            text_file.write("        <owtType>${L2WowtType}</owtType>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="OWT">\n')
            text_file.write("      <operator>OWTClassification</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>AtmCC</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <owtType>${L2WowtType}</owtType>\n")
            text_file.write(
                "        <inputReflectanceIs>${l2RReflectAs}</inputReflectanceIs>\n"
            )
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="FUB_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>FUB</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="MPH_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>MPH</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="CC_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>CC</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="OWT_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>OWT</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Nearest</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            # CHL Oligotrophic
            text_file.write('    <node id="Algal_exp">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>FUB</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>chl_algorithm</name>\n")
            text_file.write("            <type>float32</type>\n")
            # valid flag included BC wiki WB proj: set 0 - DONE
            text_file.write(
                "            <expression>l1_flags.INVALID or result_flags.CHL_OUT or algal_2 == 5 ? NaN : exp10(algal_2)</expression>\n"
            )
            text_file.write(
                "            <description>Chlorophyll 2 content</description>\n"
            )
            text_file.write("            <unit>mg/m^3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            # TSM
            text_file.write('    <node id="CC_tsm_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>CC_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>tsm</name>\n")
            text_file.write("            <type>float32</type>\n")
            # valid flag included BC wiki WB proj: set 0  - DONE
            text_file.write(
                "            <expression>!l2w_flags.INVALID and not l1p_flags.CC_COASTLINE and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_CLOUD_SHADOW ? conc_tsm : NaN</expression>\n"
            )
            text_file.write(
                "            <description>Total suspended matter dry weight concentration.</description>\n"
            )
            text_file.write("            <unit>g m^-3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            # OWT
            text_file.write('    <node id="OWT_dom_class_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>OWT_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>dominant_class</name>\n")
            text_file.write("            <type>int8</type>\n")
            # valid flag included BC wiki WB proj: set 0  - DONE
            text_file.write(
                "            <expression>!l1p_flags.CC_COASTLINE and not l1_flags.INVALID and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_CLOUD_SHADOW ? dominant_class : NaN</expression>\n"
            )
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            # CHL Eutrophic
            text_file.write('    <node id="MPH_chl_reformat">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>MPH_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>chl_eutrophic</name>\n")
            text_file.write("            <type>float32</type>\n")
            # valid flag included BC wiki WB proj: set 0 - onGoing
            text_file.write(
                "            <expression>!l1_flags.INVALID or !mph_chl_flags.mph_floating ? chl : NaN</expression>\n"
            )
            text_file.write(
                "            <description>Chlorophyll 2 content</description>\n"
            )
            text_file.write("            <unit>mg/m^3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="Algal_exp_reproj">\n')
            text_file.write("      <operator>Reproject</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>Algal_exp</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <crs>${crs}</crs>\n")
            text_file.write("        <resampling>Bilinear</resampling>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="Algal_exp2">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write(
                "        <sourceProducts>Algal_exp_reproj</sourceProducts>\n"
            )
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>chl_oligotrophic</name>\n")
            text_file.write("            <type>float32</type>\n")
            # valid exp see Algal_exp node
            text_file.write("            <expression>chl_algorithm</expression>\n")
            text_file.write(
                "            <description>Chlorophyll 2 content</description>\n"
            )
            text_file.write("            <unit>mg/m^3</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            #  edit MPH valid pixel for floating_veg here
            text_file.write('    <node id="MPH_reproj2">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>MPH_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>floating_vegetation</name>\n")
            text_file.write("            <type>int8</type>\n")
            # valid flag included BC wiki WB proj: set 0
            text_file.write(
                "            <expression>!l1p_flags.CC_COASTLINE and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_CLOUD_SHADOW ? floating_vegetation : NaN</expression>\n"
            )
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            #  edit MPH valid pixel for turbidity here
            text_file.write('    <node id="CC_reproj2">\n')
            text_file.write("      <operator>BandMaths</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <sourceProducts>CC_reproj</sourceProducts>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("        <targetBands>\n")
            text_file.write("          <targetBand>\n")
            text_file.write("            <name>turbidity</name>\n")
            text_file.write("            <type>float32</type>\n")
            # valid flag included BC wiki WB proj: set 0
            text_file.write(
                "            <expression>!l2w_flags.INVALID and not l1p_flags.CC_COASTLINE and not l1p_flags.CC_CLOUD and not l1p_flags.CC_CLOUD_BUFFER and not l1p_flags.CC_CLOUD_SHADOW ? turbidity : NaN</expression>\n"
            )
            text_file.write(
                "            <description>Turbidity index in FNU (Formazine Nephelometric Unit).</description>\n"
            )
            text_file.write("            <unit>FNU</unit>\n")
            text_file.write("          </targetBand>\n")
            text_file.write("        </targetBands>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="mergeNode">\n')
            text_file.write("      <operator>Merge</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("          <masterProduct>Algal_exp2</masterProduct>\n")
            text_file.write("          <mph>MPH_reproj2</mph>\n")
            text_file.write("          <mph2>MPH_chl_reformat</mph2>\n")
            text_file.write("          <cc>CC_reproj2</cc>\n")
            text_file.write("          <cc2>CC_tsm_reformat</cc2>\n")
            text_file.write("          <owt>OWT_dom_class_reformat</owt>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            text_file.write("          <includes>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>masterProduct</productId>\n")
            text_file.write("                  <name>chl_oligotrophic</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>mph2</productId>\n")
            text_file.write("                  <name>chl_eutrophic</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>cc2</productId>\n")
            text_file.write("                  <name>tsm</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>cc</productId>\n")
            text_file.write("                  <name>turbidity</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>mph</productId>\n")
            text_file.write("                  <name>floating_vegetation</name>\n")
            text_file.write("              </include>\n")
            text_file.write("              <include>\n")
            text_file.write("                  <productId>owt</productId>\n")
            text_file.write("                  <name>dominant_class</name>\n")
            text_file.write("              </include>\n")
            text_file.write("          </includes>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")

            text_file.write('    <node id="WriteWQ">\n')
            text_file.write("      <operator>Write</operator>\n")
            text_file.write("      <sources>\n")
            text_file.write("        <source>mergeNode</source>\n")
            text_file.write("      </sources>\n")
            text_file.write("      <parameters>\n")
            #         text_file.write('        <file>${targetbasePath}_WQ.tif</file>\n')
            #         text_file.write('        <formatName>GeoTiff</formatName>\n')
            text_file.write("        <file>${targetbasePath}_WQ.dim</file>\n")
            text_file.write("        <formatName>BEAM-DIMAP</formatName>\n")
            text_file.write("      </parameters>\n")
            text_file.write("    </node>\n")
            text_file.write("  </graph>\n")
        gpt_script = tempdir + "ProcessingGraph.xml"
        return gpt_script

    def param_check(tempdir, param0, param1, param2, param3, param4, param5, param6):
        if (
            os.path.isfile(tempdir + param0)
            & os.path.isfile(tempdir + param1)
            & os.path.isfile(tempdir + param2)
            & os.path.isfile(tempdir + param3)
            & os.path.isfile(tempdir + param4)
            & os.path.isfile(tempdir + param5)
            & os.path.isfile(tempdir + param6)
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
            if not os.path.isfile(tempdir + param5):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 4 missing. Please execute step 1-6 first!"
                )
            if not os.path.isfile(tempdir + param6):
                feedback.pushConsoleInfo(
                    "ERROR: Parameter file 4 missing. Please execute step 1-7 first!"
                )
            return False

    def concat_param(tempdir, param0, param1, param2, param3, param4, param5, param6):
        filenames = [
            tempdir + param0,
            tempdir + param1,
            tempdir + param2,
            tempdir + param3,
            tempdir + param4,
            tempdir + param5,
            tempdir + param6,
        ]
        paramfile = tempdir + "params.properties"
        with open(paramfile, "w") as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
        return paramfile

    def processing(
        tempdir, Output_folder, Input_files_list, beam_path, gpt_script, paramfile
    ):
        # Main script
        # files = []
        # for (dirpath, dirnames, filenames) in walk(input_folder):
        # files.extend(filenames)

        if Input_files_list == []:
            feedback.setProgressText("WARNING: Input folder empty!")

        for n in range(0, len(Input_files_list)):
            inputfile = Input_files_list[n]
            filename = inputfile.split("/")[len(inputfile.split("/")) - 1]
            ext = filename.split(".", 1)[1]
            ext_len = len(ext) + 1
            cmnd = (
                '"'
                + beam_path
                + '/bin/gpt.bat" "'
                + gpt_script
                + '"'
                + ' -p "'
                + paramfile
                + '" '
                + ' -PsourceFile="'
                + inputfile
                + '" -PtargetbasePath="'
                + Output_folder
                + filename[:-3]
                + '"'
            )
            feedback.setProgressText('"' + beam_path + '/bin/gpt.bat"')
            feedback.setProgressText(
                '"' + gpt_script + '"' + ' -p "' + paramfile + '" '
            )
            feedback.setProgressText(' -PsourceFile="' + inputfile + '"')
            feedback.setProgressText(
                '-PtargetbasePath="' + Output_folder + filename[:-ext_len] + '"'
            )
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            #         process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE)
            for line in iter(process.stdout.readline, ""):
                feedback.setProgressText(line)
        # os.remove(gpt_script)

    def execution(
        tempfolder,
        Output_folder,
        Input_files_list,
        beam_path,
        param0,
        param1,
        param2,
        param3,
        param4,
        param5,
        param6,
    ):
        if input_files == "":
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
            param5,
            param6,
        ):
            return
        else:
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + "*"))[
                0
            ]
            tempdir = tempdir.replace("\\", "/") + "/"
            param_results = param_check(
                tempdir, param0, param1, param2, param3, param4, param5, param6
            )
            if param_results:
                paramfile = concat_param(
                    tempdir, param0, param1, param2, param3, param4, param5, param6
                )
                if "dontsubset=false" in open(tempdir + param0).read():
                    subset = True
                else:
                    subset = False
            gpt_script = create_graph(tempdir, subset)
            processing(
                tempdir,
                Output_folder,
                Input_files_list,
                beam_path,
                gpt_script,
                paramfile,
            )
            # shutil.rmtree(tempdir)

    execution(
        tempfolder,
        Output_folder,
        input_files_list,
        beam_path,
        param0,
        param1,
        param2,
        param3,
        param4,
        param5,
        param6,
    )

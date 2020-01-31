import os
import glob
import subprocess

from qgis.processing import alg

from processing.core.ProcessingConfig import ProcessingConfig
from os import walk
import tempfile
import shutil
import math


@alg(
    name="pg04waterqualityworkflowl3binning",
    label=alg.tr("PG04_WaterQualityWorkflow_l3binning"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.FILE, name="input_folder", label="Input folder", behavior=1)
@alg.input(type=alg.NUMBER, name="start_month", label="Select start month for processing",
           default=1, minValue=1, maxValue=12)
@alg.input(type=alg.NUMBER, name="year", label="Select year for processing",
           default=2008, minValue=2002, maxValue=2012)
@alg.input(type=alg.NUMBER, name="end_month", label="Select end month for processing",
           default=1, minValue=1, maxValue=12)
@alg.input(type=alg.NUMBER, name="res", label="Set spatial resolution (km/px)",
           default=0.6, minValue=0, maxValue=1000)
@alg.input(type=alg.NUMBER, name="mem", label="Insert the amount of RAM (inGB) available for processing",
           default=1, minValue=1, maxValue=31)
@alg.input(type=alg.FOLDER_DEST, name="Output_folder", label="Output directory")
def pg04waterqualityworkflowl3binning(instance, parameters, context, feedback, inputs):
    """
    Water quality workflow l3 binning
    """

    Output_folder = instance.parameterAsString(parameters, 'Output_folder', context)
    Input_folder = instance.parameterAsString(parameters, 'input_folder', context)
    res = instance.parameterAsInt(parameters, 'res', context)
    start_month = instance.parameterAsInt(parameters, 'start_month', context)
    year = instance.parameterAsInt(parameters, 'year', context)
    mem = instance.parameterAsInt(parameters, 'mem', context)
    end_month = instance.parameterAsInt(parameters, 'end_month', context)

    # Reformating inputs and outputs
    Output_folder = Output_folder.replace("\\", "/") + "/"
    Input_folder = Input_folder.replace("\\", "/") + "/"
    beam_path = ProcessingConfig.getSetting('BEAM_FOLDER')
    #beam_path = "C:\Program Files\BEAM-5.0" - for testing
    beam_path = beam_path.replace("\\", "/")
    tempfolder = 'wq_scripts_'
    RE = 6378.145

    def computeNumRows(RE, res):
        rows = int(((RE * math.pi) / res) + 1)
        return rows

    def create_graph(tempdir, start_month, end_month, year, rows):
        with open(tempdir + "BinningGraph.xml", "w") as text_file:
            text_file.write('<graph id="l3binning">\n')
            text_file.write('  <version>1.0</version>\n')
            for month in range(start_month, end_month + 1):
                if (month == 1) | (month == 3) | (month == 5) | (month == 7) | (month == 8) | (month == 10) | (
                        month == 12):
                    days = 31
                elif month == 2:
                    days = 28
                else:
                    days = 30
                text_file.write('  <node id="someNodeId' + str(month) + '">\n')
                text_file.write('    <operator>Binning</operator>\n')
                text_file.write('    <parameters>\n')
                if month < 10:
                    text_file.write('      <sourceProductPaths>' + Input_folder + '*M' + str(year) + '0' + str(
                        month) + '*.dim</sourceProductPaths>\n')
                else:
                    text_file.write('      <sourceProductPaths>' + Input_folder + '*M' + str(year) + str(
                        month) + '*.dim</sourceProductPaths>\n')
                if month < 10:
                    text_file.write('      <startDateTime>2008-0' + str(month) + '-01</startDateTime>\n')
                else:
                    text_file.write('      <startDateTime>2008-' + str(month) + '-01</startDateTime>\n')
                text_file.write('      <periodDuration>' + str(days) + '.0</periodDuration>\n')
                text_file.write('      <timeFilterMethod>TIME_RANGE</timeFilterMethod>\n')
                text_file.write('      <numRows>' + str(rows) + '</numRows>\n')
                text_file.write('      <superSampling>1</superSampling>\n')
                text_file.write('      <maskExpr>true</maskExpr>\n')
                text_file.write('      <variables/>\n')
                text_file.write('      <aggregators>\n')
                text_file.write('          <aggregator>\n')
                text_file.write('              <type>AVG</type>\n')
                text_file.write('              <varName>chl_oligotrophic</varName>\n')
                text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
                text_file.write('              <outputCounts>false</outputCounts>\n')
                text_file.write('              <outputSums>false</outputSums>\n')
                text_file.write('          </aggregator>\n')
                text_file.write('          <aggregator>\n')
                text_file.write('              <type>AVG</type>\n')
                text_file.write('              <varName>chl_eutrophic</varName>\n')
                text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
                text_file.write('              <outputCounts>false</outputCounts>\n')
                text_file.write('              <outputSums>false</outputSums>\n')
                text_file.write('          </aggregator>\n')
                text_file.write('          <aggregator>\n')
                text_file.write('              <type>AVG</type>\n')
                text_file.write('              <varName>tsm</varName>\n')
                text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
                text_file.write('              <outputCounts>false</outputCounts>\n')
                text_file.write('              <outputSums>false</outputSums>\n')
                text_file.write('          </aggregator>\n')
                text_file.write('          <aggregator>\n')
                text_file.write('              <type>AVG</type>\n')
                text_file.write('              <varName>turbidity</varName>\n')
                text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
                text_file.write('              <outputCounts>false</outputCounts>\n')
                text_file.write('              <outputSums>false</outputSums>\n')
                text_file.write('          </aggregator>\n')
                text_file.write('          <aggregator>\n')
                text_file.write('              <type>AVG</type>\n')
                text_file.write('              <varName>floating_vegetation</varName>\n')
                text_file.write('              <outputCounts>true</outputCounts>\n')
                text_file.write('              <outputSums>true</outputSums>\n')
                text_file.write('          </aggregator>\n')
                text_file.write('      </aggregators>\n')
                text_file.write('      <outputFormat>GeoTiff</outputFormat>\n')
                if month < 10:
                    text_file.write('      <outputFile>' + Output_folder + 'level-3_' + str(year) + '0' + str(
                        month) + '.tif</outputFile>\n')
                else:
                    text_file.write('      <outputFile>' + Output_folder + 'level-3_' + str(year) + str(
                        month) + '.tif</outputFile>\n')
                text_file.write('      <metadataAggregatorName>NAME</metadataAggregatorName>\n')
                text_file.write('    </parameters>\n')
                text_file.write('    </node>\n')
            text_file.write('  </graph>\n')
        gpt_script = tempdir + "BinningGraph.xml"
        return gpt_script

    def processing(beam_path, gpt_script):
        # Main script
        # files = []
        # for (dirpath, dirnames, filenames) in walk(input_folder):
        # files.extend(filenames)

        cmnd = '"' + beam_path + '/bin/gpt.bat" -c ' + str(mem) + 'G "' + gpt_script + '"'
        feedback.setProgressText('"' + beam_path + '/bin/gpt.bat" -c ' + str(mem) + 'G "')
        feedback.setProgressText(gpt_script + '"')
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True).stdout
        line =""
        for char in iter((lambda:process.read(1)),''):
            line += char
            if "\n" in line:
                feedback.setProgressText(line)
                line = ""
        # os.remove(gpt_script)

    def execution(Output_folder, Input_folder, beam_path, start_month, end_month, year):
        if Input_folder == "":
            feedback.setProgressText('ERROR: Input folder not defined!')
            return
        elif Output_folder == "/":
            feedback.setProgressText('ERROR: Output folder not defined!')
            return
        else:
            rows = computeNumRows(RE, res)
            tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
            tempdir = tempdir.replace("\\", "/") + "/"
            gpt_script = create_graph(tempdir, start_month, end_month, year, rows)
            processing(beam_path, gpt_script)

    execution(Output_folder, Input_folder, beam_path, start_month, end_month, year)
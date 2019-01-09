#Definition of inputs and outputs
#==================================
##BC=group
##PG04_WaterQualityWorkflow_SNAP_l3binning=name
##Input_folder=folder
#This returns the values 0 and 1
##ParameterSelection|sensor|Select sensor (for time string decoding)|OLCI;MERIS;manual
##ParameterString|start_date_string|Select start date for binning period (format: YYYY/MM/DD)|2017/01/01
##ParameterString|end_date_string|Select end date for binning period (format: YYYY/MM/DD)|2017/12/31
#ParameterNumber|pos1|Set start character number for date in filename (e.g. S3A_OL_1_ERR____20161212T...; it starts at 16)|0|200|16
##ParameterString|datepref|Define character pattern before date in filename (e.g. R___ for S3A_OL_1_ERR____20161212T...)|R____
# This returns the values 0, 1 and 2
##ParameterSelection|binning_type|Select binning type|period;monthly;date to date monthly
##ParameterNumber|interval|Set binning period (in days) - only required when using binning type "period"|0|366|10
##ParameterNumber|res|Set spatial resolution (km/px)|0|1000|0.6
#ParameterNumber|mem|Insert the amount of RAM (inGB) available for processing|1|31|1
##ParameterString|outpref|Prefix for output filenames (e.g. S3A_OL_ or MER_FRS_)|S3A_OL_
##Output_folder=folder

import os
import glob
import subprocess
from processing.core.ProcessingConfig import ProcessingConfig
from os import walk
import tempfile
import shutil
import math
from dateutil import parser
from datetime import timedelta, date
import calendar

#Reformating inputs and outputs
Output_folder = Output_folder.replace("\\", "/") + "/"
Input_folder = Input_folder.replace("\\", "/")  + "/"
snap_path = ProcessingConfig.getSetting('SNAP_FOLDER')
snap_path = snap_path.replace("\\", "/") 
tempfolder = 'wq_scripts_'
RE = 6378.145

def myRound(n):
    answer = round(n)
    if not answer%2:
        return answer
    if abs(answer+1-n) < abs(answer-1-n):
        return answer + 1
    else:
        return answer - 1

def computeNumRows(RE, res):
    rows = int(myRound(((RE*math.pi)/res)))
    return rows

def diff_month(d2, d1):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12)
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)

def create_graph(tempdir, files, rows, new_filename, sensor):
    if sensor == 0:
        with open(tempdir + "BinningGraph.xml", "w") as text_file:
            text_file.write('<graph id="l3binning">\n')
            text_file.write('  <version>1.0</version>\n')
            text_file.write('  <node id="Binning">\n')
            text_file.write('    <operator>Binning</operator>\n')
            text_file.write('    <parameters>\n')
            text_file.write('      <sourceProductPaths>' + files+ '</sourceProductPaths>\n')
            text_file.write('      <timeFilterMethod>NONE</timeFilterMethod>\n')
            text_file.write('      <numRows>' + str(rows) +'</numRows>\n')
            text_file.write('      <superSampling>1</superSampling>\n')
            text_file.write('      <maskExpr>true</maskExpr>\n')
            text_file.write('      <variables/>\n')
            text_file.write('      <aggregators>\n')
            text_file.write('          <aggregator>\n')
            text_file.write('              <type>AVG</type>\n')
            text_file.write('              <varName>chl_eutrophic</varName>\n')
            text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
            text_file.write('              <outputCounts>false</outputCounts>\n')
            text_file.write('              <outputSums>false</outputSums>\n')
            text_file.write('          </aggregator>\n')
            text_file.write('          <aggregator>\n')
            text_file.write('              <type>AVG</type>\n')
            text_file.write('              <varName>chl</varName>\n')
            text_file.write('              <weightCoeff>0.0</weightCoeff>\n')
            text_file.write('              <outputCounts>false</outputCounts>\n')
            text_file.write('              <outputSums>false</outputSums>\n')
            text_file.write('          </aggregator>\n')
            text_file.write('          <aggregator>\n')
            text_file.write('              <type>AVG</type>\n')
            text_file.write('              <varName>tsm_nechad_865</varName>\n')
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
            text_file.write('      <outputFile>' + new_filename + '.tif</outputFile>\n')
            text_file.write('      <metadataAggregatorName>NAME</metadataAggregatorName>\n')
            text_file.write('    </parameters>\n')
            text_file.write('    </node>\n') 
            text_file.write('  </graph>\n')
    if sensor == 1:
        with open(tempdir + "BinningGraph.xml", "w") as text_file:
            text_file.write('<graph id="l3binning">\n')
            text_file.write('  <version>1.0</version>\n')
            text_file.write('  <node id="Binning">\n')
            text_file.write('    <operator>Binning</operator>\n')
            text_file.write('    <parameters>\n')
            text_file.write('      <sourceProductPaths>' + files+ '</sourceProductPaths>\n')
            text_file.write('      <timeFilterMethod>NONE</timeFilterMethod>\n')
            text_file.write('      <numRows>' + str(rows) +'</numRows>\n')
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
            text_file.write('      <outputFile>' + new_filename + '.tif</outputFile>\n')
            text_file.write('      <metadataAggregatorName>NAME</metadataAggregatorName>\n')
            text_file.write('    </parameters>\n')
            text_file.write('    </node>\n') 
            text_file.write('  </graph>\n')
    gpt_script = tempdir + "BinningGraph.xml"
    return gpt_script 


def processing(snap_path, gpt_script):
    #Main script
    #files = []
    #for (dirpath, dirnames, filenames) in walk(input_folder):
        #files.extend(filenames)

    cmnd = '"' + snap_path + '/bin/gpt.exe" "' + gpt_script + '"'
    progress.setText('"' + snap_path + '/bin/gpt.exe"' ) 
    progress.setText( '"' + gpt_script + '"')
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, ''):
        progress.setText(line)
    #os.remove(gpt_script)
 
def execution(Output_folder, Input_folder, snap_path, start_date_string, end_date_string, binning_type, interval, res, RE, sensor):
    if Input_folder == "":
        progress.setText('ERROR: Input folder not defined!')
        return
    elif Output_folder == "/":
        progress.setText('ERROR: Output folder not defined!')
        return
    else:
        rows = computeNumRows(RE, res)
        tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
        tempdir = tempdir.replace("\\", "/") + "/"
        
        start = start_date_string.split('/')
        end = end_date_string.split('/')
        start_num = int(''.join(start))
        end_num = int(''.join(end))

        filenames = []
        for item in os.listdir(Input_folder):
            if os.path.isfile(os.path.join(Input_folder, item)):
                filenames.extend(item.split())

        start_end_filenames = []
        for n in filenames:
            pos1 = n.find(datepref)+len(datepref)
            if int(n[pos1:pos1+8]) >= start_num and int(n[pos1:pos1+8]) <= end_num:
                start_end_filenames = start_end_filenames + (''.join(n)).split()

        if binning_type == 0: #period
            # currently it searches for 10 days at the end of the period even if
            # 9 out of 10 are already outside the period.
            # -> potential improvement possible

            start_date = parser.parse(start_date_string)
            end_date = parser.parse(end_date_string)
            for n in range(0,int((end_date - start_date).days)+1, interval):
                k1 = start_date + timedelta(n)
                k1 = int(''.join(str(k1.date()).split('-')))
                k2 = start_date + timedelta(n+interval-1)
                k2 = int(''.join(str(k2.date()).split('-')))
                sel_filenames = []
                for x in start_end_filenames:
                    pos1 = x.find(datepref)+len(datepref)
                    if int(x[pos1:pos1+8]) >= k1 and int(x[pos1:pos1+8]) <= k2:
                        sel_filenames = sel_filenames + (Input_folder + ''.join(x)).split()
                #print(sel_filenames)
                if sel_filenames == []:
                    progress.setText('No files between: ' + str(parser.parse(str(k1)).date()) + ' and ' + str(parser.parse(str(k2)).date()))
                else:
                    progress.setText('Processing')
                    new_filename = Output_folder + outpref + str(k1) + '-' + str(k2)  + '_' + str(interval) + 'day_period_' + '_WQ'
                    files = ','.join(sel_filenames)
                    gpt_script = create_graph(tempdir, files, rows, new_filename, sensor)
                    processing(snap_path, gpt_script)

        elif binning_type == 1: #monthly
            datelist = []
            for n in start_end_filenames:
                pos1 = n.find(datepref)+len(datepref)
                datelist = datelist + n[pos1:pos1+6].split()
            datelist = list(set(datelist))
            
            for ymonth in datelist:
                sel_filenames = [Input_folder + s for s in start_end_filenames if ymonth in s]
                
                if sel_filenames == []:
                    progress.setText('No files in month: ' + str(ymonth))
                else:
                    progress.setText('Processing')
                    new_filename = Output_folder + outpref + str(ymonth) + '_monthly_WQ'
                    files = ','.join(sel_filenames)
                    gpt_script = create_graph(tempdir, files, rows, new_filename, sensor)
                    processing(snap_path, gpt_script)

        else: #monthly date to date
            start_date = parser.parse(start_date_string)
            end_date = parser.parse(end_date_string)
            month_diff_num = diff_month(start_date, end_date)
            month_num = month_diff_num + 1

            for n in range(month_num):
                k1 = add_months(start_date, n)
                k1 = int(''.join(str(k1).split('-')))
                k2 = add_months(start_date, n+1)
                k2 = int(''.join(str(k2).split('-')))

                sel_filenames = []
                for n in start_end_filenames:
                    pos1 = n.find(datepref)+len(datepref)
                    if int(n[pos1:pos1+8]) >= k1 and int(n[pos1:pos1+8]) < k2:
                        sel_filenames = sel_filenames + (
                        Input_folder + ''.join(n)).split()
                # print(sel_filenames)
                if sel_filenames == []:
                    progress.setText('No files between: ' + str(
                        parser.parse(str(k1)).date()) + ' and ' + str(
                        parser.parse(str(k2)).date()))
                else:
                    progress.setText('Processing')
                    new_filename = Output_folder + outpref + str(k1) + '-' + str(k2) + '_monthly_WQ'
                    files = ','.join(sel_filenames)
                    gpt_script = create_graph(tempdir, files, rows, new_filename, sensor)
                    processing(snap_path, gpt_script)

execution(Output_folder, Input_folder, snap_path, start_date_string, end_date_string, binning_type, interval, res, RE, sensor)
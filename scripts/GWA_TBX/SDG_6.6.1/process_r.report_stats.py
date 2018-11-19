# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 10:45:26 2018

@author: rmgu
"""

##SDG 6.6.1 reporting=group
##SDG 6.6.1 - process r.report statistics=name
##ParameterFile|report_file|Classification statistics file for reference period|False|False|txt
##ParameterString|filename|Statistics filename with period replaced by yyyy (single year) or yyyy-yyyy (multiple years)|report_yyyy-yyyy.txt|
##ParameterRaster|raster|Calssification map with classes in the legend|False
##ParameterString|skip_lc|Land cover class to use only in tables|Non Wetland|
##OutputFile|json_file|Output JSON file|json
##OutputFile|csv_file|Output CSV file|csv

import glob
import os
import re

import pandas as pd
import json
import xml.etree.ElementTree as et

from processing.tools import dataobjects
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

# Parse raster legend to obtain names of the landcover classes
raster_classes = {}
raster_layer =  dataobjects.getObjectFromUri(raster)
style_manager = raster_layer.styleManager()
style_XML = style_manager.style(style_manager.currentStyle()).xmlData()
xml_root = et.fromstring(style_XML)
shader = xml_root.findall("./pipe/rasterrenderer/rastershader/colorrampshader")
if not shader:
    raise GeoAlgorithmExecutionException("Raster must have singleband pseudocolor rendering!")
for item in shader[0].iter("item"):
    raster_classes[item.get("value")] = {"label": item.get("label"), "color": item.get("color")}

# Find the reference period and all the r.report output files located in the same directory as the
# report file for the reference period.
if "yyyy-yyyy" in filename:
    filename_regex = filename.replace("yyyy-yyyy","(\d+-\d+)")
    filename_glob = filename.replace("yyyy-yyyy", "*")
else:
    filename_regex = filename.replace("yyyy","(\d+)")
    filename_glob = filename.replace("yyyy", "*")
match = re.search(filename_regex+"$", report_file)
if match:
    reference_period = match.group(1)
else:
    raise GeoAlgorithmExecutionException("The provided statistics file for reference period and " +
                                         "the filename template do not match!")
report_files = glob.glob(os.path.join(os.path.dirname(report_file), filename_glob))

# Parse the text files produced by r.report
values_as_km2 = []
regionIds = []
periods = []
region = None
processing_region = False
for text_file in report_files:
    period = re.search(filename_regex+"$", text_file).group(1)
    with open(text_file, "r") as fp:
        for line in fp:
            if not processing_region:
                match = re.match("\|\s*(\d+)\|\s+\|\s*([\d\.,]+)\|", line)
                if match:
                    processing_region = True
                    region_stats = {landcover: "0.0" for landcover in  
                                                [rc["label"] for rc in list(raster_classes.values())]}
                    region_stats["yyyy"] = period
                    region = match.group(1)
                    region_stats["regionId"] = region
                    regionIds.append(region)
                    periods.append(period)
            else:
                match = re.match("\|\s*\|(\d+)\|(\s\.)+\s*\|\s*([\d\.,]+)\|", line)
                if match:
                    land_cover = match.group(1)
                    try:
                        lc_label = raster_classes[land_cover]["label"]
                    except KeyError:
                        raise GeoAlgorithmExecutionException("A landcover class is not present " +
                                                             "in the raster legend!")
                    area = match.group(3).replace(",", "")
                    region_stats[lc_label] = area
                elif re.match("\|-+\|?-+\|", line):
                    values_as_km2.append(region_stats)
                    processing_region = False
regionIds = set(regionIds)
periods = set(periods)

# Calculate percentage change of landcover classes from the reference period
reference_stats = {}
for region_stats in values_as_km2:
    if region_stats["yyyy"] == reference_period:
        reference_stats[region_stats["regionId"]] = region_stats.copy()
values_as_percentchange = []
for region_stats in values_as_km2:
    change_stats = region_stats.copy()
    regionId = region_stats["regionId"]
    for lc in region_stats.keys():
        if lc in ["yyyy", "regionId"]:
            continue
        try:   
            change = ((float(reference_stats[regionId][lc]) - float(region_stats[lc])) /
                    float(reference_stats[regionId][lc])) * 100.0
        except ZeroDivisionError:
            if float(region_stats[lc]) == 0:
                change = 0.0
            else:
                change = -100.0
        change_stats[lc] = '%.2f' % change
    values_as_percentchange.append(change_stats)

# Save the parsed data as json file
json_data = {"metadata": [{"reference_year": reference_period, "field_only_in_table": skip_lc}]}
json_data["values_as_km2"] = values_as_km2
json_data["values_as_percentchange"] = values_as_percentchange
with open(json_file, "w") as fp:
    json.dump(json_data, fp, sort_keys=True, indent=4, separators=(',', ': '))

# Save parsed data as CSV file
lc_labels = [lc["label"] for lc in raster_classes.values()]
for regionId in regionIds:
    filename = os.path.splitext(csv_file)[0]+"_"+regionId+os.path.splitext(csv_file)[1]
    df = pd.DataFrame(columns=periods, index=lc_labels)
    for region in values_as_km2:
        if region["regionId"] == regionId:
            df[region["yyyy"]] = [region[lc] if lc in region.keys() else 0.0 for lc in lc_labels]
    df.columns = ["Size in square kilometers ("+period+")" for period in df.columns]
    df.index.name = "Class"
    df.to_csv(filename)
for regionId in regionIds:
    filename = os.path.splitext(csv_file)[0] + "_change_" + regionId +\
               os.path.splitext(csv_file)[1]
    df = pd.DataFrame(columns=periods, index=lc_labels)
    for region in values_as_percentchange:
        if region["regionId"] == regionId:
            df[region["yyyy"]] = [region[lc] if lc in region.keys() else 0.0 for lc in lc_labels]
    df.columns = ["Percentage area change from "+reference_period+" ("+period+")"
                  for period in df.columns]
    df.index.name = "Class"
    df.to_csv(filename)

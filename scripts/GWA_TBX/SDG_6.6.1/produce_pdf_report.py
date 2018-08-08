# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 08:26:12 2018

@author: rmgu
"""

##SDG 6.6.1 reporting=group
##SDG 6.6.1 - produce report for a given year=name
##ParameterFile|json_file|JSON file with the statistics|False|False|json
##ParameterRaster|raster|Classified raster image for the year to report on|False
##ParameterVector|vector|Regional polygons|2|False
##ParameterNumber|year|Year to report on|1990|2030|2018
##ParameterFile|template_file|Report template file|False|False|qpt
##OutputFile|report_pdf_file|Output report PDF file|pdf

import os

import json
import pandas as pd
import xml.etree.ElementTree as et

from qgis.PyQt.QtXml import QDomDocument
from qgis.core import QgsComposition, QgsFillSymbolV2, QgsRuleBasedRendererV2, QgsComposerHtml
from qgis.utils import iface
from processing.tools import dataobjects
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException

# Parse raster legend to obtain names of the landcover classes
raster_classes = {}
raster_layer = dataobjects.getObjectFromUri(raster)
style_manager = raster_layer.styleManager()
style_XML = style_manager.style(style_manager.currentStyle()).xmlData()
xml_root = et.fromstring(style_XML)
shader = xml_root.findall("./pipe/rasterrenderer/rastershader/colorrampshader")
if not shader:
    raise GeoAlgorithmExecutionException("Raster must have singleband pseudocolor rendering!")
for item in shader[0].iter("item"):
    raster_classes[item.get("value")] = {"label": item.get("label"), "color": item.get("color")}

# Read the statistics from the json file and for each region produce a table showing land cover
# areas in the reference year and area change in the target year
with open(json_file, "r") as fp:
    data = json.load(fp)
reference_year = data["metadata"][0]["reference_year"]
report_tables = {}
lc_labels = [lc["label"] for lc in raster_classes.values()]
columns = ["Area in "+reference_year+" (km<sup>2</sup>)", "Area change in "+str(year)+" (%)"]
for region in data["values_as_km2"]:
    if region["yyyy"] == reference_year:
        df = pd.DataFrame(columns=columns, index=lc_labels)
        df.fillna(0, inplace=True)
        for lc in region.keys():
            if lc in lc_labels:
                df.iloc[:, 0][lc] = float(region[lc])
        report_tables[region["regionId"]] = df
for region in data["values_as_percentchange"]:
    if region["yyyy"] == str(year):
        df = report_tables[region["regionId"]]
        for lc in region.keys():
            if lc in lc_labels:
                df.iloc[:, 1][lc] = float(region[lc])

# Load the report template
with open(template_file) as tf:
    template_content = tf.read()
template_document = QDomDocument()
template_document.setContent(template_content)
map_settings = iface.mapCanvas().mapSettings()
composition = QgsComposition(map_settings)
composition.loadFromTemplate(template_document)

# Set up atlas to produce one report per region
vector_layer = dataobjects.getObjectFromUri(vector)
atlas = composition.atlasComposition()
atlas.setCoverageLayer(vector_layer)
atlas.setEnabled(True)
composition.setAtlasMode(QgsComposition.ExportAtlas)

atlas_map = composition.getComposerItemById("atlas_map")
atlas_map.setAtlasDriven(True)
atlas_map.setLayerSet([vector_layer.id(), raster_layer.id()])
atlas_map.setKeepLayerSet(True)
stats_table = composition.getComposerItemById("stats_table").multiFrame()
stats_table.setContentMode(QgsComposerHtml.ManualHtml)
title_label = composition.getComposerItemById("title_label")
title_text = title_label.text()
description_label = composition.getComposerItemById("description_label")
description_text = description_label.text()

# Set a rule based style to highlight the atlas feature
normal_style = QgsFillSymbolV2().createSimple({"color": "#000000",
                                               "color_border": "#000000",
                                               "width_border": "0.25",
                                               "style": "no"})
highlight_style = QgsFillSymbolV2().createSimple({"color": "#000000",
                                                  "color_border": "#ff0000",
                                                  "width_border": "0.85",
                                                  "style": "no"})
highlight_rule = QgsRuleBasedRendererV2.Rule(highlight_style)
highlight_rule.setFilterExpression("$id = @atlas_featureid")
highlight_renderer = QgsRuleBasedRendererV2(normal_style)
highlight_renderer.rootRule().appendChild(highlight_rule)
original_renderer = vector_layer.rendererV2()
vector_layer.setRendererV2(highlight_renderer)
vector_layer.triggerRepaint()

# Produce the reports
atlas.beginRender()
for i in range(atlas.numFeatures()):
    atlas.prepareForFeature(i)
    region_id = str(atlas.feature().attribute("aoi_id"))
    if region_id not in report_tables.keys():
        continue
    styled_df = report_tables[region_id].style.format("{0:.2f}")
    html = styled_df.set_table_styles([{"selector": ", table",
                                        "props": [('border-collapse', 'collapse'),
                                                  ('border-spacing', '0')]},
                                       {"selector": ", th, td",
                                        "props": [('border', '1px solid black')]},
                                       {"selector": ", td",
                                        "props": [('text-align', 'right')]},
                                       {"selector": ", th",
                                        "props": [('text-align', 'center')]}]).render()
    stats_table.setHtml(html)
    stats_table.loadHtml()
    region_name = atlas.feature().attribute("aoi_name")
    title_label.setText(title_text.replace("%REGION_NAME%", region_name))
    description = description_text.replace("%REGION_NAME%", region_name)
    description = description.replace("%REF_YEAR%", reference_year)
    description = description.replace("%TARGET_YEAR%", str(year))
    description_label.setText(description)
    filename = os.path.splitext(report_pdf_file)[0] + "_" + region_id +\
               os.path.splitext(report_pdf_file)[1]
    composition.exportAsPDF(filename)
atlas.endRender()

# The two lines below should reset the vector style to the original but they crash QGIS so for
# now they are commented out.
#vector_layer.setRendererV2(original_renderer)
#vector_layer.triggerRepaint()

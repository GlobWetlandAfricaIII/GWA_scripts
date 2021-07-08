# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 08:26:12 2018

@author: rmgu
"""

import os
from collections import OrderedDict

import json
import numpy as np
import pandas as pd
import xml.etree.ElementTree as et

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingAlgorithm,
                       QgsProject,
                       QgsReadWriteContext,
                       QgsLayoutExporter,
                       QgsPrintLayout,
                       QgsFillSymbol,
                       QgsRuleBasedRenderer,
                       QgsLayoutItemHtml,
                       QgsLegendRenderer,
                       QgsLegendStyle)


# Cannot use @alg decorator because we need to set no-threding flag to parse HTML properly
class ProduceSDGReportAlgorithm(QgsProcessingAlgorithm):

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Must return a new copy of your algorithm.
        return ProduceSDGReportAlgorithm()

    def name(self):
        """
        Returns the unique algorithm name.
        """
        return 'sdg661producereportforagivenperiod'

    def displayName(self):
        """
        Returns the translated algorithm name.
        """
        return self.tr('SDG 6.6.1 - produce report for a given period')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('SDG 6.6.1 reporting')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs
        to.
        """
        return 'sdg661reporting'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr('SDG 6.6.1 - produce report for a given period')

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """
        # 'INPUT' is the recommended name for the main input
        # parameter.
        self.addParameter(
            QgsProcessingParameterFile(
                'json_file',
                self.tr("JSON file with the statistics"),
                behavior=0,
                optional=False,
                fileFilter="*.json"
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'raster',
                self.tr("Classification map for the period to report on"),
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'vector',
                self.tr("Regional polygons"),
            )
        )
        self.addParameter(
            QgsProcessingParameterString(
                'period',
                self.tr("Period to report on"),
                defaultValue="2018"
            )
        )
        self.addParameter(
            QgsProcessingParameterFile(
                'template_file',
                self.tr("Report template file"),
                behavior=0,
                optional=False,
                fileFilter="*.qpt"
            )
        )
        self.addParameter(
            QgsProcessingParameterFileDestination(
                'report_pdf_file',
                self.tr("Output report PDF file"),
                fileFilter="*.pdf"
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        instance = self
        """sdg661producereportforagivenperiod"""
        json_file = instance.parameterAsString(parameters, "json_file", context)
        raster_layer = instance.parameterAsLayer(parameters, "raster", context)
        vector_layer = instance.parameterAsLayer(parameters, "vector", context)
        period = instance.parameterAsString(parameters, "period", context)
        template_file = instance.parameterAsString(parameters, "template_file", context)
        report_pdf_file = instance.parameterAsString(parameters, "report_pdf_file", context)

        # Parse raster legend to obtain names of the landcover classes
        raster_classes = OrderedDict()
        style_manager = raster_layer.styleManager()
        style_XML = style_manager.style(style_manager.currentStyle()).xmlData()
        xml_root = et.fromstring(style_XML)
        shader = xml_root.findall("./pipe/rasterrenderer/rastershader/colorrampshader")
        if not shader:
            raise QgsProcessingException("Raster must have singleband pseudocolor rendering!")
        for item in shader[0].iter("item"):
            raster_classes[item.get("value")] = {"label": item.get("label"),
                                                 "color": item.get("color")}

        # Read the statistics from the json file and for each region produce a table showing land
        # cover areas in the reference period and area change in the target period
        with open(json_file, "r") as fp:
            data = json.load(fp)
        reference_period = data["metadata"][0]["reference_year"]
        report_tables = {}
        lc_labels = [lc["label"] for lc in raster_classes.values()]
        columns = ["Area in "+reference_period+" (km<sup>2</sup>)",
                   "Area change in "+str(period)+" (%)"]
        for region in data["values_as_km2"]:
            if region["yyyy"] == reference_period:
                df = pd.DataFrame(columns=columns, index=lc_labels, dtype=np.float32)
                df.fillna(0, inplace=True)
                for lc in region.keys():
                    if lc in lc_labels:
                        df.iloc[:, 0][lc] = float(region[lc])
                report_tables[region["regionId"]] = df
        for region in data["values_as_percentchange"]:
            if region["yyyy"] == str(period):
                df = report_tables[region["regionId"]]
                for lc in region.keys():
                    if lc in lc_labels:
                        df.iloc[:, 1][lc] = float(region[lc])

        # Load the report template
        with open(template_file) as tf:
            template_content = tf.read()
        template_document = QDomDocument()
        template_document.setContent(template_content)
        composition = QgsPrintLayout(QgsProject.instance())
        composition.loadFromTemplate(template_document, QgsReadWriteContext())

        # Set up atlas to produce one report per region
        atlas = composition.atlas()
        atlas.setCoverageLayer(vector_layer)
        atlas.setEnabled(True)

        atlas_map = composition.itemById("atlas_map")
        atlas_map.setAtlasDriven(True)
        atlas_map.setLayers([vector_layer, raster_layer])
        atlas_map.setKeepLayerSet(True)
        atlas_legend = composition.itemById("atlas_legend")
        raster_legend = atlas_legend.model().rootGroup().addLayer(raster_layer)
        QgsLegendRenderer.setNodeLegendStyle(raster_legend, QgsLegendStyle.Hidden)
        atlas_legend.updateLegend()
        stats_table = composition.itemById("stats_table").multiFrame()
        stats_table.setContentMode(QgsLayoutItemHtml.ManualHtml)
        title_label = composition.itemById("title_label")
        title_text = title_label.text()
        description_label = composition.itemById("description_label")
        description_text = description_label.text()

        # Set a rule based style to highlight the atlas feature
        normal_style = QgsFillSymbol().createSimple({"color": "#000000",
                                                     "color_border": "#000000",
                                                     "width_border": "0.25",
                                                     "style": "no"})
        highlight_style = QgsFillSymbol().createSimple({"color": "#000000",
                                                        "color_border": "#ff0000",
                                                        "width_border": "0.85",
                                                        "style": "no"})
        highlight_rule = QgsRuleBasedRenderer.Rule(highlight_style)
        highlight_rule.setFilterExpression("$id = @atlas_featureid")
        highlight_renderer = QgsRuleBasedRenderer(normal_style)
        highlight_renderer.rootRule().appendChild(highlight_rule)
        vector_layer.setRenderer(highlight_renderer)
        vector_layer.triggerRepaint()

        # Produce the reports
        atlas.beginRender()
        for i in range(atlas.count()):
            atlas.seekTo(i)
            region_id = str(vector_layer.getFeature(i).attribute("aoi_id"))
            if region_id not in report_tables.keys():
                continue
            styled_df = report_tables[region_id].style.format("{:.2f}")
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
            region_name = vector_layer.getFeature(i).attribute("aoi_name")
            title_label.setText(title_text.replace("%REGION_NAME%", region_name))
            description = description_text.replace("%REGION_NAME%", region_name)
            description = description.replace("%REF_PERIOD%", reference_period)
            description = description.replace("%TARGET_PERIOD%", str(period))
            description_label.setText(description)
            filename = os.path.splitext(report_pdf_file)[0] + "_" + region_id +\
                       os.path.splitext(report_pdf_file)[1]
            exporter = QgsLayoutExporter(composition)
            exporter.exportToPdf(filename, QgsLayoutExporter.PdfExportSettings())
        atlas.endRender()
        return {}

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading

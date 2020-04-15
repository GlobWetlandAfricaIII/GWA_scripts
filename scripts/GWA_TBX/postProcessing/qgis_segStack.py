import os
import sys
from qgis.processing import alg

if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
import segStack


@alg(
    name="preparepostprocessingstack",
    label=alg.tr("Stack bands for segmentation"),
    group="gt",
    group_label=alg.tr("Generic Tools"),
)
@alg.input(type=alg.RASTER_LAYER, name="inRst1", label="Input Stack")
@alg.input(type=alg.BOOL, name="B1", label="Band 1", default=False)
@alg.input(type=alg.BOOL, name="B2", label="Band 2", default=False)
@alg.input(type=alg.BOOL, name="B3", label="Band 3", default=False)
@alg.input(type=alg.BOOL, name="B4", label="Band 4", default=False)
@alg.input(type=alg.BOOL, name="B5", label="Band 5", default=False)
@alg.input(type=alg.BOOL, name="B6", label="Band 6", default=False)
@alg.input(type=alg.BOOL, name="B7", label="Band 7", default=False)
@alg.input(type=alg.BOOL, name="B8", label="Band 8", default=False)
@alg.input(type=alg.BOOL, name="B9", label="Band 9", default=False)
@alg.input(type=alg.BOOL, name="B10", label="Band 10", default=False)
@alg.input(type=alg.RASTER_LAYER, name="inRst2", label="Classification Raster")
@alg.input(
    type=alg.RASTER_LAYER_DEST, name="outPath", label="Output Stack for Segmentation"
)
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Stack rasters for segmentation
    """
    outBands = []
    if instance.parameterAsBool(parameters, "B1", context) is True:
        outBands.append(1)
    if instance.parameterAsBool(parameters, "B2", context) is True:
        outBands.append(2)
    if instance.parameterAsBool(parameters, "B3", context) is True:
        outBands.append(3)
    if instance.parameterAsBool(parameters, "B4", context) is True:
        outBands.append(4)
    if instance.parameterAsBool(parameters, "B5", context) is True:
        outBands.append(5)
    if instance.parameterAsBool(parameters, "B6", context) is True:
        outBands.append(6)
    if instance.parameterAsBool(parameters, "B7", context) is True:
        outBands.append(7)
    if instance.parameterAsBool(parameters, "B8", context) is True:
        outBands.append(8)
    if instance.parameterAsBool(parameters, "B9", context) is True:
        outBands.append(9)
    if instance.parameterAsBool(parameters, "B10", context) is True:
        outBands.append(10)
    if len(outBands) == 0:
        feedback.reportError("ERROR: No bands selected", fatalError=True)

    feedback.setProgressText("Starting preparation of stack...")

    # run script
    segStack.prepSegStack(
        instance.parameterAsRasterLayer(parameters, "inRst1", context).source(),
        outBands,
        instance.parameterAsRasterLayer(parameters, "inRst2", context).source(),
        instance.parameterAsOutputLayer(parameters, "outPath", context),
    )

    feedback.setProgressText("Finished!")
    return {"outPath": instance.parameterAsOutputLayer(parameters, "outPath", context)}

from qgis.processing import alg
from qgis import processing


@alg(
    name="reprojectrasterandvectorlayers",
    label=alg.tr("Reproject raster and vector layers"),
    group="sdg661reporting",
    group_label=alg.tr("SDG 6.6.1 reporting"),
)
@alg.input(type=alg.RASTER_LAYER, name="inputRaster", label="Raster layer")
@alg.input(type=alg.VECTOR_LAYER, name="inputVector", label="Vector layer")
@alg.input(type=alg.CRS, name="projection", label="Metric coordinate system (UTM)")
@alg.input(
    type=alg.RASTER_LAYER_DEST, name="outputRaster", label="Reprojected raster layer"
)
@alg.input(
    type=alg.VECTOR_LAYER_DEST, name="outputVector", label="Reprojected vector layer"
)
def reproject_raster_and_vector(instance, parameters, context, feedback, inputs):
    """
    Reproject raster and vector layers
    """
    feedback.setProgressText("Reprojecting vector...")
    params = {
        "INPUT": parameters["inputVector"],
        "TARGET_CRS": parameters["projection"],
        "OUTPUT": parameters["outputVector"],
    }
    vector_result = processing.run(
        "native:reprojectlayer",
        params,
        is_child_algorithm=True,
        context=context,
        feedback=feedback,
    )

    feedback.setProgressText("Reprojecting raster...")
    params = {
        "INPUT": parameters["inputRaster"],
        "TARGET_CRS": parameters["projection"],
        "OUTPUT": parameters["outputRaster"],
    }
    raster_result = processing.run(
        "gdal:warpreproject",
        params,
        is_child_algorithm=True,
        context=context,
        feedback=feedback,
    )

    return {
        "OUTPUT_RASTER": raster_result["OUTPUT"],
        "OUTPUT_VECTOR": vector_result["OUTPUT"],
    }

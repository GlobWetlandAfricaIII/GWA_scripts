from qgis.processing import alg
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools import dataobjects, system
from qgis import processing

@alg(
    name="burncloudmask",
    label=alg.tr("Burn cloud mask"),
    group="fmask",
    group_label=alg.tr("FMask")
)
@alg.input(type=alg.RASTER_LAYER, name="dataFile", label="An image file to burn the cloud mask into", optional=False)
@alg.input(type=alg.RASTER_LAYER, name="maskFile", label="Could mask from FMask", optional=False)
@alg.input(type=bool, name="maskNull", label="Mask FMask null pixels", default=True)
@alg.input(type=bool, name="maskCloud", label="Mask FMask cloud pixels", default=True)
@alg.input(type=bool, name="maskShadow", label="Mask FMask shadow pixels", default=True)
@alg.input(type=bool, name="maskSnow", label="Mask FMask snow pixels", default=True)
@alg.input(type=bool, name="maskWater", label="Mask FMask water pixels", default=False, advanced=True)
@alg.input(type=bool, name="maskLand", label="Mask FMask land pixels", default=False, advanced=True)
@alg.output(type=alg.RASTER_LAYER, name="outputFile", label="Maked output image")


def burncloudmask(instance, parameters, context, feedback, inputs):
    ''' burncloudmask '''
    # Run GDAL warp to make sure that the mask file exactly aligns with the image file
    feedback.setProgressText("Aligning mask raster to image raster...")
    dataRaster = dataobjects.getObject(dataFile)
    proj = dataRaster.crs().authid()
    resolution = dataRaster.rasterUnitsPerPixelX()
    bandCount = dataRaster.bandCount()
    extent = dataobjects.extent([dataRaster])
    warpMask = system.getTempFilename("tif")
    params = {"INPUT": maskFile, "DEST_SRS": proj, "TR": resolution, "USE_RASTER_EXTENT": True,
            "RASTER_EXTENT": extent, "EXTENT_CRS": proj, "METHOD": 0, "RTYPE": 0, "OUTPUT": warpMask}
    processing.run("gdalogr:warpreproject", params, context, feedback)

    feedback.setProgressText("Applying mask to image...")
    # First reclassify fmask output into two classes
    flags = [maskNull, maskLand, maskCloud, maskShadow, maskSnow, maskWater]
    maskClass = [str(i) for i in range(len(flags)) if flags[i]]
    leaveClass = [str(i) for i in range(len(flags)) if not flags[i]]
    reclassString = " ".join(maskClass) + " = 0\n" + " ".join(leaveClass) + " = 1"
    reclassMask = system.getTempFilename("tif")
    params = {"input": warpMask, "txtrules": reclassString, "output": reclassMask,
            "GRASS_REGION_PARAMETER": extent, "GRASS_REGION_CELLSIZE_PARAMETER": resolution}
    processing.run("grass7:r.reclass", params, context, feedback)

    # Then use OTB band maths on all bands
    params = {"-il":  dataFile+";"+reclassMask, "-exp": "im1*im2b1", "-out": outputFile}
    processing.run("otb:bandmathx", params, context, feedback)

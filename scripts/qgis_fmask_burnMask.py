#Definition of inputs and outputs
#==================================
##Fmask=group
##Burn cloud mask=name
##ParameterRaster|dataFile|An image file to burn the cloud mask into|False
##ParameterRaster|maskFile|Could mask from FMask|False
##*ParameterBoolean|maskNull|Mask FMask null pixels|True
##*ParameterBoolean|maskCloud|Mask FMask cloud pixels|True
##*ParameterBoolean|maskShadow|Mask FMask shadow pixels|True
##*ParameterBoolean|maskSnow|Mask FMask snow pixels|True
##*ParameterBoolean|maskWater|Mask FMask water pixels|False
##*ParameterBoolean|maskLand|Mask FMask land pixels|False
##OutputRaster|outputFile|Maked output image

from processing.tools import dataobjects, system

# Run GDAL warp to make sure that the mask file exactly aligns with the image file
progress.setText("Aligning mask raster to image raster...")
dataRaster = dataobjects.getObject(dataFile)
proj = dataRaster.crs().authid()
resolution = dataRaster.rasterUnitsPerPixelX()
bandCount = dataRaster.bandCount()
extent = dataobjects.extent([dataRaster])
warpMask = system.getTempFilename("tif")
params = {"INPUT": maskFile, "DEST_SRS": proj, "TR": resolution, "USE_RASTER_EXTENT": True,
          "RASTER_EXTENT": extent, "EXTENT_CRS": proj, "METHOD": 0, "RTYPE": 0, "OUTPUT": warpMask}
processing.runalg("gdalogr:warpreproject", params)

progress.setText("Applying mask to image...")
# First reclassify fmask output into two classes
flags = [maskNull, maskLand, maskCloud, maskShadow, maskSnow, maskWater]
maskClass = [str(i) for i in range(len(flags)) if flags[i]]
leaveClass = [str(i) for i in range(len(flags)) if not flags[i]]
reclassString = " ".join(maskClass) + " = 0\n" + " ".join(leaveClass) + " = 1"
reclassMask = system.getTempFilename("tif")
params = {"input": warpMask, "txtrules": reclassString, "output": reclassMask,
          "GRASS_REGION_PARAMETER": extent, "GRASS_REGION_CELLSIZE_PARAMETER": resolution}
processing.runalg("grass7:r.reclass", params)

# Then use OTB band maths on all bands
params = {"-il":  dataFile+";"+reclassMask, "-exp": "im1*im2b1", "-out": outputFile}
processing.runalg("otb:bandmathx", params)

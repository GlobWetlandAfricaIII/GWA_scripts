#Definition of inputs and outputs
#==================================
##SDG 6.6.1 reporting=group
##Reproject raster and vector layers=name
##ParameterRaster|inputRaster|Raster layer|
##ParameterVector|inputVector|Vector layer|2
##ParameterCrs|projection|Metric coordinate system (UTM)|
##OutputRaster|outputRaster|Reprojected raster layer
##OutputVector|outputVector|Reprojected vector layer

# This script is not made as a model because there is no ParameterCrs in the QGIS 2.x 
# modeler (it exists in QGIS 3.x)

# Run GDAL warp to reproject raster layer
progress.setText("Reprojecting raster...")
params = {'INPUT': inputRaster, 'DEST_SRS': projection, 'METHOD': 0,  
                 'RTYPE': 1, 'OUTPUT': outputRaster}
processing.runalg("gdalogr:warpreproject", params)

# Run ReprojectLayer to reproject vector layer
progress.setText("Reprojecting vector...")
params = {'INPUT': inputVector, 'TARGET_CRS': projection,  'OUTPUT': outputVector}
processing.runalg("qgis:reprojectlayer", params)
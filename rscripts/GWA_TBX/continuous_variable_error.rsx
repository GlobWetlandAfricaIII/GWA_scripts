##[Accuracy Assessment]=group


##Continuous_Variable_Raster=raster
##Validation_Samples=vector
##Validation_Label_Field= Field Validation_Samples
##Error_Statistics=output table

# Check for packages required, and if they are not installed, instal them.
tryCatch(find.package("Metrics"), error=function(e) install.packages("Metrics", lib=file.path(.Library[1])))

library(Metrics)

# first make sure that the class ID field is not a factor, and change it to numeric if it is
if (class(eval(parse(text = paste('Validation_Samples@data$', Validation_Label_Field, sep = '')))) == 'factor'){

eval(parse(text = paste0('Validation_Samples@data$', Validation_Label_Field, '<- as.numeric(as.character(Validation_Samples@data$', Variable_Name, '))')))

}

img <- Continuous_Variable_Raster

# First, if the training data are vector polygons they must be coverted to points
# to speed things up
if (class(Validation_Samples)[1] == 'SpatialPolygonsDataFrame'){
# rasterize
poly_rst <- rasterize(Validation_Samples, img[[1]], field = Validation_Label_Field)
# convert pixels to points
Validation_Samples_P <- rasterToPoints(poly_rst, spatial=TRUE)
# give the point ID the 'Validation_Label_Field' name
names(Validation_Samples_P@data) <- Validation_Label_Field
# note for some strange reason, the crs of the spatial points did not match the imagery!
# here the crs of the sample points is changed back to match the input imagery
crs(Validation_Samples_P) <- crs(img[[1]])
}

# extract the training data
if (class(Validation_Samples)[1] == 'SpatialPolygonsDataFrame'){
data_frame <- extract(img, y = Validation_Samples_P)
} else {
data_frame <- extract(img, y = Validation_Samples)
}
data_frame <- data.frame(data_frame)
names(data_frame) <- 'image'


# add the classification ID to the model training data
if (class(Validation_Samples)[1] == 'SpatialPolygonsDataFrame'){
data_frame$actual <- as.vector(eval(parse(text = paste('Validation_Samples_P@data$', Validation_Label_Field, sep = ''))))
} else {
data_frame$actual <- as.vector(eval(parse(text = paste('Validation_Samples@data$', Validation_Label_Field, sep = ''))))
}

# remove any points with NAs
complete <- data_frame[complete.cases(data_frame),]

# get statistics (root mean square error, and mean absolute error)
rmse_res <- rmse(complete$actual, complete$image)
mae_res <- mae(complete$actual, complete$image)

stats <- round(data.frame(cbind(rmse_res, mae_res)), 3)
names(stats) <- c('Root Mean Square Error', 'Mean Absolute Error')
row.names(stats) <- 'Errors'

Error_Statistics <- stats

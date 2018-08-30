##[Classification]=group
##Data_to_be_Classified=raster
##Training_Data=vector
##Class_ID_Field=string
##Mask_Raster=optional raster
##Output_Raster=output raster

# Advanced parameters
##Number_of_Cores_for_Processing=advanced number 2
##Number_of_Trees=advanced number 150

# TODO: make sure that the training date crs matches the raster crs. project training data if necessary.


# Check for packages required, and if they are not installed, instal them.
tryCatch(find.package("maptools"), error=function(e) install.packages("maptools", lib=file.path(.Library[1])))
tryCatch(find.package("randomForest"), error=function(e) install.packages("randomForest", lib=file.path(.Library[1])))
tryCatch(find.package("snow"), error=function(e) install.packages("snow", lib=file.path(.Library[1])))
tryCatch(find.package("snowfall"), error=function(e) install.packages("snowfall", lib=file.path(.Library[1])))
tryCatch(find.package("tcltk2"), error=function(e) install.packages("tcltk", lib=file.path(.Library[1])))


# load all libraries used
library(maptools)
library(randomForest)
library(snow)
library(snowfall)
library(tcltk2)

# Define raster options
rasterOptions(datatype = 'INT2S', progress = 'window', timer = T, chunksize = 1e+07, maxmemory = 1e+08, tmptime = 24)

# get image data used in the classification
img <- stack(Data_to_be_Classified)

# first make sure that the class ID field is not a factor, and change it to numeric if it is
if (class(eval(parse(text = paste('Training_Data@data$', Class_ID_Field, sep = '')))) == 'factor'){

eval(parse(text = paste0('Training_Data@data$', Class_ID_Field, '<- as.numeric(as.character(Training_Data@data$', Class_ID_Field, '))')))

}

# extract training data in parallel using snowfall
pb <- tkProgressBar("Random Forest Progress", "Extracting Training Data", 0, 100, 50)

# First, if the training data are vector polygons they must be coverted to points
# to speed things up
if (class(Training_Data)[1] == 'SpatialPolygonsDataFrame'){
# rasterize
poly_rst <- rasterize(Training_Data, img[[1]], field = Class_ID_Field)
# convert pixels to points
Training_Data_P <- rasterToPoints(poly_rst, spatial=TRUE)
# give the point ID the 'Class_ID_Field' name
names(Training_Data_P@data) <- Class_ID_Field
# note for some strange reason, the crs of the spatial points did not match the imagery!
# here the crs of the sample points is changed back to match the input imagery
crs(Training_Data_P) <- crs(img[[1]])
}


# extract the training data using snowflake
imgl <- unstack(img)
sfInit(parallel=TRUE, cpus = Number_of_Cores_for_Processing)
sfLibrary(raster)
sfLibrary(rgdal)
if (class(Training_Data)[1] == 'SpatialPolygonsDataFrame'){
data <- sfSapply(imgl, extract, y = Training_Data_P)
} else {
data <- sfSapply(imgl, extract, y = Training_Data)
}
sfStop()
data <- data.frame(data)
names(data) <- names(img)


# add the classification ID to the model training data
if (class(Training_Data)[1] == 'SpatialPolygonsDataFrame'){
data$LUC <- as.vector(eval(parse(text = paste('Training_Data_P@data$', Class_ID_Field, sep = ''))))
} else {
data$LUC <- as.vector(eval(parse(text = paste('Training_Data@data$', Class_ID_Field, sep = ''))))
}
close(pb)



# run random forest classifier
pb <- tkProgressBar("Random Forest Progress", "Training Random Forest Model", 0, 100, 50)
RandomForestModel <- randomForest(data[,1:(ncol(data)-1)], as.factor(data$LUC), ntree = Number_of_Trees, importance = T, scale = F)
close(pb)


# get out-of-bag error
OOBE <- as.data.frame(RandomForestModel[[5]])

# Classify the image
beginCluster(Number_of_Cores_for_Processing)
map_rf <- clusterR(img, raster::predict, args = list(model = RandomForestModel, na.rm = TRUE))
endCluster()
gc()


# mask the resulting classification
if (Mask_Raster != ''){
pb <- tkProgressBar("Random Forest Progress", "Applying Mangrove Mask", 0, 100, 50)
msk <- raster(Mask_Raster)
map_rf <- mask(map_rf, msk, progress='window')
close(pb)
}

Output_Raster <- map_rf

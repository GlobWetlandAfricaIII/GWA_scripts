##[Regression]=group
##Regression_Data=raster
##Training_Data=vector
##Variable_Name=string
##Mask_Raster=optional raster

# Advanced parameters
##Number_of_Cores_for_Processing=advanced number 2
##Gamma_for_Radial_Kernel=advanced,optional number
##Cost_for_Radial_Kernel=advanced, number 10

##Output_Raster = output raster

# TODO: make sure that the training date crs matches the raster crs. project training data if necessary.

# Check for packages required, and if they are not installed, instal them.
tryCatch(find.package("maptools"), error=function(e) install.packages("maptools", lib=file.path(.Library[1])))
tryCatch(find.package("e1071"), error=function(e) install.packages("e1071", lib=file.path(.Library[1])))
tryCatch(find.package("snow"), error=function(e) install.packages("snow", lib=file.path(.Library[1])))
tryCatch(find.package("snowfall"), error=function(e) install.packages("snowfall", lib=file.path(.Library[1])))
tryCatch(find.package("rpanel"), error=function(e) install.packages("tcltk", lib=file.path(.Library[1])))

# load all libraries used
library(maptools)
library(e1071)
library(snow)
library(snowfall)
library(rpanel)

# Define raster options
rasterOptions(datatype = 'INT2S', progress = 'window', timer = T, chunksize = 1e+07, maxmemory = 1e+08, tmptime = 24)

# get image data used in the classification
img <- stack(Regression_Data)

# first make sure that the class ID field is not a factor, and change it to numeric if it is
if (class(eval(parse(text = paste('Training_Data@data$', Variable_Name, sep = '')))) == 'factor'){

eval(parse(text = paste0('Training_Data@data$', Variable_Name, '<- as.numeric(as.character(Training_Data@data$', Variable_Name, '))')))

}

# First, if the training data are vector polygons they must be coverted to points
# to speed things up
if (class(Training_Data)[1] == 'SpatialPolygonsDataFrame'){
# rasterize
poly_rst <- rasterize(Training_Data, img[[1]], field = Variable_Name)
# convert pixels to points
Training_Data_P <- rasterToPoints(poly_rst, spatial=TRUE)
# give the point ID the 'Variable_Name' name
names(Training_Data_P@data) <- Variable_Name
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
data_frame <- sfSapply(imgl, extract, y = Training_Data_P)
} else {
data_frame <- sfSapply(imgl, extract, y = Training_Data)
}
sfStop()
data_frame <- data.frame(data_frame)
names(data_frame) <- names(img)


# add the classification ID to the model training data
if (class(Training_Data)[1] == 'SpatialPolygonsDataFrame'){
data_frame$LUC <- as.vector(eval(parse(text = paste('Training_Data_P@data$', Variable_Name, sep = ''))))
} else {
data_frame$LUC <- as.vector(eval(parse(text = paste('Training_Data@data$', Variable_Name, sep = ''))))
}

# train the model
if (Gamma_for_Radial_Kernel!=0){
svm_model  <- svm(LUC ~ ., data = data_frame, kernel = 'radial', cost=Cost_for_Radial_Kernel, gamma=Gamma_for_Radial_Kernel)
} else {
svm_model  <- svm(LUC ~ ., data = data_frame, kernel = 'radial', cost=Cost_for_Radial_Kernel)
}

# classify the image
panel <- rp.control(title = "Progess Message. . .", size = c(500, 50))
rp.text(panel, "Applying the regression model to imagery. . .", font="Arial", pos = c(10, 10), title = 'bottom', name = 'prog_panel')
beginCluster(Number_of_Cores_for_Processing)
map_svm <- clusterR(img, raster::predict, args = list(model = svm_model, na.rm = TRUE))
endCluster()
gc()

# mask the resulting classification
if (!is.null(Mask_Raster)){
panel <- rp.control(title = "Progess Message. . .", size = c(500, 50))
rp.text(panel, "Applying mask. . .", font="Arial", pos = c(10, 10), title = 'bottom', name = 'prog_panel')
map_svm <- mask(map_svm, Mask_Raster, progress='window')
rp.control.dispose(panel)
}

Output_Raster <- map_svm

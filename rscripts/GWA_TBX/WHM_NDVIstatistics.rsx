##[Wetland Habitat Mapping] = group
##Directory_containing_multitemporal_images=folder
##satellite = selection Sentinel-2; Landsat
##Mean = boolean True
##Maximum = boolean True
##Minimum = boolean True
##Range = boolean True
##StandardDeviation = boolean False
##Output_NDVI_statistics = output raster

require(raster)
setwd(Directory_containing_multitemporal_images)
img <- list.files(pattern='\\.tif$')
rast.list<-list()
ndvi<-list()

#calculate NDVI
for(i in 1:length(img)){
rast.list[i] <-stack(img[i])
if(satellite==0){
band3=subset(rast.list[[i]], 3)
band7=subset(rast.list[[i]], 7)
ndvi[i]<-(band7-band3)/(band7+band3)*1000
}
if(satellite==1){
band3=subset(rast.list[[i]], 3)
band4=subset(rast.list[[i]], 4)
ndvi[i]<-(band4-band3)/(band4+band3)*1000
}
}
ndvi<-stack(ndvi)

#calculate statistics of multi-temporal NDVI
stats<-stack()
if(Mean) stats$mean=calc(ndvi,mean, na.rm=TRUE)
if(Maximum) stats$max=calc(ndvi,max, na.rm=TRUE)
if(Minimum) stats$min=calc(ndvi,min, na.rm=TRUE)
if(Range) stats$range=max(ndvi, na.rm=TRUE)-min(ndvi, na.rm=TRUE)
if(StandardDeviation) stats$std=calc(ndvi, sd, na.rm=TRUE)

#stats<-round(stats)
stats[]=as.integer(stats[])

Output_NDVI_statistics<-stats

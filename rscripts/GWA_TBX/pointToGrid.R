                              
  #---------------------------------------------------------------------------------#

  # This function takes a point shapefile and makes a square grid for every point
  # based on the grid of a specified raster.

  # For each point that fall within a raster pixel cell, a square ploygon is made 
  # with the outline being the raster pixel

  #---------------------------------------------------------------------------------#

  
  # function to convert a pixel (cell) to polygon
  # can be used in a loop if you have a vector of cell numbers
  # x = base raster
  # cell = cell number of the base raster (these are converted to polygons)  
  PixToPoly<-function (cell, x) {
    
    # get the xy position
    cell <- as.vector(xyFromCell(x, cell))
    
    # get the center offset
    off<-(res(x)/2)[1]
    
    # make the polygon - accounting for the center offset
    e <- extent(c(cell[1]-off, cell[1]-off + res(x)[1], cell[2]-off, cell[2]-off + res(x)[2]))
    e <- as(e, "SpatialPolygons")
    projection(e) <- projection(x)
    return(e)
  }
  
  # function same as above, but makes a 3 x 3 grid instead of a single pixel square
  
  PixToPoly_3x3<-function (cell, x) {
    
    # get the xy position
    cell <- as.vector(xyFromCell(x, cell))
    
    # get the center offset
    off<-(res(x)/2)[1]
    
    # make the polygon - accounting for the center offset
    e <- extent(c(cell[1]-off, cell[1]-off + res(x)[1], cell[2]-off, cell[2]-off + res(x)[2]))
    e <- as(e, "SpatialPolygons")
    
    # now make the 3 x 3 grid
    
    # first get coordinates of the pixel corners
    co<-e@polygons[[1]]@Polygons[[1]]@coords
    
    # then make a grid of X and Y values for the 3 x 3 grid
    # get x intervals for matrix
    rx<-res(x)[1]
    xmn<-co[1,1]-rx
    xmx<-co[3,1]+rx
    # make x intervals
    xint<-seq(xmn,xmx, rx)
    
    # get y intervals for matrix
    ry<-res(x)[2]
    ymn<-co[1,2]-ry
    ymx<-co[3,2]+ry
    # make x intervals
    yint<-seq(ymn,ymx, ry)
    
    # build matrix xmin > xmax (col1), ymin > ymax (col2)
    # make grid
    grd<-expand.grid(xint, yint)
    
    # now pick the coordinates for the grid
    cp<-as.matrix(grd[c(6,10,11,7,6,2,3,7,8,12,11,15,14,10,9,5,6,5,1,2,3,4,8,12,16,15,14,13,9,5,6),])
    
    
    # this function converts the grid into a spatial polygon
    matrix_to_poly<-function(coord_matrix){
      
      cmp<-Polygon(coord_matrix)
      # convert to polygons
      cmps<-Polygons(list(cmp), ID='1')
      # convert to spatila polygon
      cmpsp<-SpatialPolygons(list(cmps))
      
      
    }
    
    eg<-matrix_to_poly(cp)
    
    projection(eg) <- projection(x)
    return(eg)
  }
  
  
  PointToGrid<-function(inRst, smp, g3x3=TRUE){
    
    # get attribute data
    att<-smp@data
    
    # get the cell number raster corresponding to each points
    clnum<-as.matrix(cellFromXY(inRst, smp))
    
    
    if (g3x3==FALSE){
      
      # apply PixToPoly function to create grid polygons based on cell numbers
      pol_lst<-apply(clnum,  1, PixToPoly, x=inRst)
      
    } else {
      
      # apply PixToPoly function to create grid polygons based on cell numbers
      pol_lst<-apply(clnum,  1, PixToPoly_3x3, x=inRst)
      
    }
    
    
    # merge the list of grid polygons
    pol<-do.call(bind, pol_lst)
    
    # add attribute data to pixel polygons  
    pol_spd<-SpatialPolygonsDataFrame(pol, data=att)
    
    return(pol_spd)
    
  }
  
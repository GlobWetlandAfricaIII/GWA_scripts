"""
Script for preparing a multiband stack for segmentation, specifically desinged for
post-processing of classified maps. Mulitspectral bands from an input raster stack
are combined with the classification results. In this way the segmentation results
should to some extent comform with the class borders.

"""

## test inputs. . .
#inRst1 = r'C:\o\demo_GWA_III\preprocess\atmos\S2_saloum_clipped_dos.tif'
#outBands = [1,2,3,7]
#inRst2 = r'C:\o\demo_GWA_III\preprocess\classified\S2_saloum_class_mmu.tif'
#outPath = r'C:\o\demo_GWA_III\preprocess\seg\segStack2.tif'
## test run. . .
#prepSegStack(inRst1, outBands, inRst2, outPath)

import gdal
import numpy as np

# function to get raster specs
def rst_specs(stk):
    """ Function to extract useful specifications from a raster image"""
    
    xsize = stk.RasterXSize
    ysize = stk.RasterYSize
    zsize = stk.RasterCount
    proj = stk.GetProjection()
    geotransform = stk.GetGeoTransform()
    
    band = stk.GetRasterBand(1)
    dtype = gdal.GetDataTypeName(band.DataType)

    spec = [xsize, ysize, zsize, proj, geotransform, dtype]

    return spec

def extract_band(stack, bnd_num):
    """Function to extract a band from a raster stack"""
    
    b = stack.GetRasterBand(bnd_num)
    band = b.ReadAsArray().astype(np.float32)
    return band


def prepSegStack(inRst1, outBands, inRst2, outPath):
    
    """
    Main function for preparing image stack for segmentation (GWA post processing)    
    
    Parameters
    ----------
    inRst1 : str
        path to input stack used for segmentation
    outBands : list
        list of bands to be extracted from inout stack
    inRst2 : str
        path to classification raster - classes must be represented by integers (e.g. 1-10)
    outDir : str
        path to output dir
        
    Returns
    ----------
    Write a new stack of selected bands from Rst1, together with the classification
    
    
    """
    
    # open stacks
    stk1 = gdal.Open(inRst1)
    stk2 = gdal.Open(inRst2)
    
    # get number of bands for output stack
    numBands = len(outBands)+1
    
    # get specs from the input stack
    specs1 = rst_specs(stk1)
    
    # create new stack from extracted input
    drv = gdal.GetDriverByName('GTiff')
    outTif = drv.Create(outPath, specs1[0], specs1[1], numBands, gdal.GDT_Int16)
    outTif.SetProjection(specs1[3])
    outTif.SetGeoTransform(specs1[4])
    
    
    # extract the specified bands from stack and combine with classification
    try:
        
        for i in range(len(outBands)):
            
            band2write = extract_band(stk1, outBands[i])
            outTif.GetRasterBand(i+1).WriteArray(band2write)
    
        classBand = extract_band(stk2, 1)*10000
        outTif.GetRasterBand(numBands).WriteArray(classBand)
         
    finally:
        outTif = None
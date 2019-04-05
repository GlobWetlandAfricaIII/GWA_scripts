# function for calculating a selction of Landsat Spectral indices
# Kenneth Grogan 3/11/2016

import os
import gdal
import numpy as np

def standard_index(band1, band2):
    """Function for standard index calculation"""
    idx = (band1 - band2) / (band1 + band2) * 10000
    return idx

def extract_band(stack, bnd_num):
    """Function to extract single bands from stack; stack = input stack, bnd_num = the band number to extract"""
    b = stack.GetRasterBand(bnd_num)
    band = b.ReadAsArray().astype(np.float32)
    return band


def calc_index(stack, bnd_num1, bnd_num2):
    """ Function to calculate an index; stack = input stack, bnd_numx = the band number in the stack"""
    band1 = extract_band(stack, bnd_num1)
    band2 = extract_band(stack, bnd_num2)
    any_index = standard_index(band1, band2)
    return any_index


def landsat_indices(inRst, outDir):
    """
    Main function for calculating a selction of Sentinel 2 Spectral indices
    """
    stk = gdal.Open(inRst)

    # get raster specs
    xsize = stk.RasterXSize
    ysize = stk.RasterYSize
    proj = stk.GetProjection()
    geotransform = stk.GetGeoTransform()

    # calculate indices: these indices were chosen based on variable importance ranking from Random Forest classification
    # calc ndvi
    ndvi = calc_index(stk, 4, 3)

    # calc ndvi using 8a
    ndmi = calc_index(stk, 4, 5)

    # calc red edge ndi b8a_b5
    nbr = calc_index(stk, 4, 6)

    # calc red edge ndi b8a_b6
    nbr2 = calc_index(stk, 5, 6)

    # Stack and write to disk
    # get base filename and combine with outpath
    sName = os.path.splitext(os.path.basename(inRst))[-2]
    stkPath = os.path.join(outDir, sName + '_indices.tif')
    drv = gdal.GetDriverByName('GTiff')
    outTif = drv.Create(stkPath, xsize, ysize, 4, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(ndvi)
    outTif.GetRasterBand(2).WriteArray(ndmi)
    outTif.GetRasterBand(3).WriteArray(nbr)
    outTif.GetRasterBand(4).WriteArray(nbr2)
    outTif = None
    return stkPath

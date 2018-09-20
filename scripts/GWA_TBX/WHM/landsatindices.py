
# function for calculating a selction of Landsat Spectral indices
# Yiwen Sun 16/03/2017

import os
import gdal
import numpy as np


def standard_index(band1, band2):
    """Function for standard index calculation"""
    idx = (band1 - band2)/(band1 + band2)*1000
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


def landsatindices(inRst, outDir):
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
    ndvi_b4_b3 = calc_index(stk, 4, 3)

    # calc mNDWI
    ndwi_b2_b5 = calc_index(stk, 2, 5)

    # calc NDWI
    ndwi_b2_b4 = calc_index(stk, 2, 4)

    # calc DVW
    dvw = ndvi_b4_b3 - ndwi_b2_b4

    # calc TCB
    tcb = 0.3037 * extract_band(stk, 1) + 0.2793 * extract_band(stk, 2) + 0.4743 * extract_band(stk, 3) + 0.5585 * extract_band(stk, 4) + 0.5082 * extract_band(stk, 5) + 0.1863 * extract_band(stk, 6)

    # calc TCG
    tcg = -0.2848 * extract_band(stk, 1) - 0.2435 * extract_band(stk, 2) - 0.5436 * extract_band(stk, 3) + 0.7243 * extract_band(stk, 4) + 0.0840 * extract_band(stk, 5) - 0.1800 * extract_band(stk, 6)

    # calc TCW
    tcw = 0.1509 * extract_band(stk, 1) + 0.1973 * extract_band(stk, 2) + 0.3279 * extract_band(stk, 3) + 0.3406 * extract_band(stk, 4) - 0.7112 * extract_band(stk, 5) - 0.4572 * extract_band(stk, 6)

    # Stack and write to disk
    # get base filename and combine with outpath
    sName = os.path.splitext(os.path.basename(inRst))[-2]
    stkPath = os.path.join(outDir, sName +'_indices.tif')
    drv = gdal.GetDriverByName('GTiff')
    outTif = drv.Create(stkPath, xsize, ysize, 6, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(ndvi_b4_b3)
    outTif.GetRasterBand(2).WriteArray(ndwi_b2_b5)
    outTif.GetRasterBand(3).WriteArray(dvw)
    outTif.GetRasterBand(4).WriteArray(tcb)
    outTif.GetRasterBand(5).WriteArray(tcg)
    outTif.GetRasterBand(6).WriteArray(tcw)
    outTif = None
    return stkPath

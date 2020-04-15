# GUI for QGIS ---------------------------------------------------------------

##Vegetation and Water Indices=name
##Wetland Habitat Mapping=group
##ParameterFile|input_dir|Directory containing imagery|True|False
##ParameterSelection|sensor|Sensor|Sentinel-2;Landsat|Sentinel-2
##OutputDirectory|output_dir|Output directory

# IMPORTS -------------------------------------------------------------------------
import os, sys
import glob
import gdal
import numpy as np
import RSutils.RSutils as rsu

# FUNCTIONS -------------------------------------------------------------------------
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


def calculate_Sentinel2_indices(inRst, outDir):
    """
    Main function for calculating a selction of Sentinel 2 Spectral indices
    """
    stk = gdal.Open(inRst)

    sName = os.path.splitext(os.path.basename(inRst))[-2]

    # get raster specs
    xsize = stk.RasterXSize
    ysize = stk.RasterYSize
    proj = stk.GetProjection()
    geotransform = stk.GetGeoTransform()

    drv = gdal.GetDriverByName("GTiff")

    # calc ndvi
    stkPath = os.path.join(outDir, "NDVI", sName + "_NDVI.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDVI = calc_index(stk, 7, 3)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(NDVI)
    outTif = None

    # calc DVW
    stkPath = os.path.join(outDir, "DVW", sName + "_DVW.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDWI = calc_index(stk, 2, 7)
    DVW = NDVI - NDWI
    del NDVI
    del NDWI
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(DVW)
    outTif = None
    del DVW

    # calc red edge ndi b8a_b5
    stkPath = os.path.join(outDir, "NDI8a5", sName + "_NDI8a5.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDI8a5 = calc_index(stk, 8, 4)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(NDI8a5)
    outTif = None
    del NDI8a5

    # calc red edge ndi b7_b5
    stkPath = os.path.join(outDir, "NDI705", sName + "_NDI705.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDI705 = calc_index(stk, 6, 4)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(NDI705)
    outTif = None
    del NDI705

    # calc mNDWI
    stkPath = os.path.join(outDir, "mNDWI", sName + "_mNDWI.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    mNDWI = calc_index(stk, 2, 9)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(mNDWI)
    outTif = None
    del mNDWI


def calculate_Landsat_indices(inRst, outDir):
    """
    Main function for calculating a selction of Landsat Spectral indices
    """
    stk = gdal.Open(inRst)

    sName = os.path.splitext(os.path.basename(inRst))[-2]

    # get raster specs
    xsize = stk.RasterXSize
    ysize = stk.RasterYSize
    proj = stk.GetProjection()
    geotransform = stk.GetGeoTransform()

    drv = gdal.GetDriverByName("GTiff")

    # calc ndvi
    stkPath = os.path.join(outDir, "NDVI", sName + "_NDVI.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDVI = calc_index(stk, 4, 3)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(NDVI)
    outTif = None

    # calc DVW
    stkPath = os.path.join(outDir, "DVW", sName + "_DVW.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    NDWI = calc_index(stk, 2, 4)
    DVW = NDVI - NDWI
    del NDVI
    del NDWI
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(DVW)
    outTif = None
    del DVW

    # calc mNDWI
    stkPath = os.path.join(outDir, "mNDWI", sName + "_mNDWI.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    mNDWI = calc_index(stk, 2, 5)
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(mNDWI)
    outTif = None
    del mNDWI

    # calc TCB
    stkPath = os.path.join(outDir, "TCB", sName + "_TCB.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    TCB = (
        0.3037 * extract_band(stk, 1)
        + 0.2793 * extract_band(stk, 2)
        + 0.4743 * extract_band(stk, 3)
        + 0.5585 * extract_band(stk, 4)
        + 0.5082 * extract_band(stk, 5)
        + 0.1863 * extract_band(stk, 6)
    )
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(TCB)
    outTif = None
    del TCB

    # calc TCG
    stkPath = os.path.join(outDir, "TCG", sName + "_TCG.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    TCG = (
        -0.2848 * extract_band(stk, 1)
        - 0.2435 * extract_band(stk, 2)
        - 0.5436 * extract_band(stk, 3)
        + 0.7243 * extract_band(stk, 4)
        + 0.0840 * extract_band(stk, 5)
        - 0.1800 * extract_band(stk, 6)
    )
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(TCG)
    outTif = None
    del TCG

    # calc TCW
    stkPath = os.path.join(outDir, "TCW", sName + "_TCW.tif")
    if not os.path.exists(os.path.dirname(stkPath)):
        os.mkdir(os.path.dirname(stkPath))
    TCW = (
        0.1509 * extract_band(stk, 1)
        + 0.1973 * extract_band(stk, 2)
        + 0.3279 * extract_band(stk, 3)
        + 0.3406 * extract_band(stk, 4)
        - 0.7112 * extract_band(stk, 5)
        - 0.4572 * extract_band(stk, 6)
    )
    outTif = drv.Create(stkPath, xsize, ysize, 1, gdal.GDT_Int16)
    outTif.SetProjection(proj)
    outTif.SetGeoTransform(geotransform)
    outTif.GetRasterBand(1).WriteArray(TCW)
    outTif = None
    del TCW


#  Call function to calculate indices -------------------------
os.chdir(input_dir)
for raster in glob.glob("*.tif"):

    if sensor == 0:
        calculate_Sentinel2_indices(raster, output_dir)
    elif sensor == 1:
        calculate_Landsat_indices(raster, output_dir)

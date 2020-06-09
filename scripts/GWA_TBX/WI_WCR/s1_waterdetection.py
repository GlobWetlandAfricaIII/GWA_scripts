#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
#
# Date created: 20.10.2017
# Date last modified: 22.11.2017
#
#
# __author__ = "Bjoern Dulleck"
# __version__ = "1.0"

from osgeo import gdal, ogr
import cv2
import numpy as np



### FUNCTIONS

def multiTempMin(path_tiff_stack):
    '''
    Create Multitemporal backscatter minimum
    :param path_tiff_stack: 
    :return: 
    '''
    dataset = gdal.Open(path_tiff_stack)
    gt = dataset.GetGeoTransform()
    proj = dataset.GetProjection()
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize

    # read stack blockwise and compute backscatter minimum
    divs = divmod(rows, 16.)
    splits = np.full((16),divs[0])
    splits[15] = divs[0] + divs[1]

    min_img = np.empty((0, cols), dtype=np.float32)
    i=0
    for split in splits:
        split = int(split)
        w = dataset.ReadAsArray(0, i, cols, split)

        min_sig = np.nanmin(w, axis=0)
        w = None
        min_img = np.vstack([min_img, min_sig])
        min_sig = None
        i=i+split
        #print i

    dataset = None  # Close the file
    # export to GTIFF
    path_stack_min = path_tiff_stack[:-4] + '_min.tif'
    write_geotiff(path_stack_min, min_img, geo_transform=gt, projection=proj)
    w = None
    min_img = None

    # remove stack
    #os.remove(path_tiff_stack)

    return path_stack_min

def rescale_to_8bit(fname):
    data = gdal.Open(fname)
    arr = data.ReadAsArray()
    arr = np.where(arr == 0.0, np.nan, arr)

    minVal_db = np.nanmin(arr)
    maxVal_db = np.nanmax(arr)

    scaled_8bit = (arr - minVal_db) / (maxVal_db - minVal_db) * 255
    arr = None
    scaled_8bit = np.asarray(scaled_8bit,dtype=np.uint8)

    trans = data.GetGeoTransform()
    proj = data.GetProjection()
    return (minVal_db, maxVal_db, scaled_8bit, trans, proj)

def rescale_to_db(arr, minVal_db, maxVal_db):

    minVal = np.nanmin(arr)
    maxVal = np.nanmax(arr)

    filt_rescaled = minVal_db + (arr - minVal) * ((maxVal_db - minVal_db) / (maxVal - minVal))

    return filt_rescaled

def apply_nlm(img_8bit):

    denoise = cv2.fastNlMeansDenoising(src=img_8bit, dst=None, h=10, templateWindowSize=7, searchWindowSize=21)

    return denoise

def createWaterMask(array, glob_thresh):
    preMask = np.where(array < glob_thresh-5, 0, 1)

    # apply binarization
    tileSize = 99
    c_sub = 19

    th1 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)

    shape_arr = array.shape
    tileSize = int(shape_arr[0] / 20)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th2 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)
    tileSize = int(shape_arr[0] / 10)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th3 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)
    tileSize = int(shape_arr[0] / 5)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th4 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)
    tileSize = int(shape_arr[0] / 4)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th5 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)
    tileSize = int(shape_arr[0] / 3)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th6 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)
    tileSize = int(shape_arr[0] / 2)
    mod = tileSize % 2
    if mod <= 0:
        tileSize += 1
    th7 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)

    tileSize = int(shape_arr[0])
    if (tileSize % 2) == 0:
        tileSize += 1
    tileSize -= 50
    c_sub = 21
    th8 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)

    tileSize = int(shape_arr[1])
    if (tileSize % 2) == 0:
        tileSize += 1
    tileSize -= 50
    th9 = cv2.adaptiveThreshold(array, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, tileSize, c_sub)

    th = np.where((th1 == 0) | (th2 == 0) | (th3 == 0) | (th4 == 0) | (th5 == 0) | (th6 == 0) | (th7 == 0) | (th8 == 0) | (th9 == 0) | (preMask == 0) , 0, 1)

    th1 = th2 = th3 = th4 = th5 = th6 = th7 = th8 = th9 = preMask =None

    th_2 = np.where(array != 0, th, np.nan)
    th_3 = np.where(np.isnan(th_2), 255, th_2).astype(np.uint8)

    return th_3

def write_geotiff(fname, data, geo_transform, projection):
    """Create a GeoTIFF file with the given data."""
    driver = gdal.GetDriverByName('GTiff')
    rows, cols = data.shape
    dataset = driver.Create(fname, cols, rows, 1, gdal.GDT_Float32)
    dataset.SetGeoTransform(geo_transform)
    dataset.SetProjection(projection)
    band = dataset.GetRasterBand(1)
    band.WriteArray(data)
    dataset = None  # Close the file

def writeFile(outfile,geotransform,geoprojection,data,fileType):
    (x,y) = data.shape
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    if fileType == 'integer8':
        dst_datatype = gdal.GDT_Byte
    elif fileType == 'float32':
        dst_datatype = gdal.GDT_Float32
    dst_ds = driver.Create(outfile,y,x,1,dst_datatype, options = [ 'COMPRESS=LZW' ])
    dst_ds.GetRasterBand(1).WriteArray(data)
    #if fileType == 'integer8':
    #    dst_ds.GetRasterBand(1).SetNoDataValue(255)
    dst_ds.SetGeoTransform(geotransform)
    dst_ds.SetProjection(geoprojection)
    return 1

def get_otsu_thresh(denoise_tif):
    ds = gdal.Open(denoise_tif)
    array = ds.ReadAsArray()
    ds = None
    ret2, th2 = cv2.threshold(array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return ret2


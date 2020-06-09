#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
#
# Date created: 20.10.2017
# Date last modified: 05.11.2017
#
#
# __author__ = "Bjoern Dulleck"
# __version__ = "1.0"

##SAR Water Detection = name
##Water Cycle Regime=group
##ParameterFile|path_imagery|Directory containing Sentinel-1 GRDH imagery (Zip format)|True|False
##OutputDirectory|pathOUT|Output directory
##ParameterVector|path_AOI|Shapefile containing AOI (Area of Interest)
##ParameterString|startDate|Start date (YYYYMMDD)
##ParameterString|endDate|End date (YYYYMMDD)

debug = False


# IMPORTS ----------------------------------------------------------------------------------------------

from datetime import timedelta, datetime
import fnmatch
import zipfile as zp
import re
from osgeo import ogr, gdal
import numpy as np
import subprocess as sub
from glob import glob
import os, sys, gc
import tempfile
import shutil


import snappy
from snappy import ProductIO
from snappy import HashMap
from snappy import GPF

System = snappy.jpy.get_type('java.lang.System')
Runtime = snappy.jpy.get_type('java.lang.Runtime')
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
HashMap = snappy.jpy.get_type('java.util.HashMap')

si = sub.STARTUPINFO()
si.dwFlags |= sub.STARTF_USESHOWWINDOW

if not debug:
    from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
    import qgis
    here = os.path.dirname(scriptDescriptionFile)
    sys.path.append(os.path.join(here))
    import s1_waterdetection as s1



# FUNCTIONS #########################################################################################

def zip2kml(zipf):

    zip_files = []
    zpfile = zp.ZipFile(zipf)

    k_ending = ["map-overlay"]
    for k in k_ending:
        kml = ["/".join(["/vsizip", zipf, k]) for k in fnmatch.filter(zpfile.namelist(), "*%s*.kml" % k)]
        kml = kml[0]
        zip_files.append(kml)

    zpfile.close()

    kml_path = zip_files[0]
    return kml_path

def write_shapefile(poly, out_shp):
    """
    https://gis.stackexchange.com/a/52708/8104
    """
    # Now convert it to a shapefile with OGR
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(out_shp)
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()

    ## If there are multiple geometries, put the "for" loop here

    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', 123)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkt(poly)
    feat.SetGeometry(geom)

    layer.CreateFeature(feat)
    feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None

def createFootprintShp(path_S1_Zip, path_tmp_files):
    '''
    Function to create S1 Footprint out ouf S1-Zipfile
    '''
    archive = zp.ZipFile(path_S1_Zip, 'r')
    if not os.path.exists(path_tmp_files):
        os.makedirs(path_tmp_files)
    archive.extract(os.path.basename(path_S1_Zip[:-4]) + '.SAFE/preview/map-overlay.kml', path_tmp_files)

    path_kml = os.path.join(path_tmp_files, os.path.basename(path_S1_Zip[:-4]) + '.SAFE/preview/map-overlay.kml')

    with open(path_kml, 'r') as f:
        for line in f:
            if 'coordinates' in line:
                coords = line

    coords = coords.strip()
    cleancoords = re.compile('<.*?>')
    cleantextcoords = re.sub(cleancoords, '', coords)

    coords_sep = cleantextcoords.replace(' ', ',')
    coords_list = coords_sep.split(",")

    coords_ring = [(coords_list[0], coords_list[1]), (coords_list[2], coords_list[3]), (coords_list[4], coords_list[5]),
                   (coords_list[6], coords_list[7]), (coords_list[0], coords_list[1])]

    ring = ogr.Geometry(ogr.wkbLinearRing)
    for coord in coords_ring:
        ring.AddPoint(float(coord[0]), float(coord[1]))

    # Create polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)

    out_shp = os.path.join(path_tmp_files, os.path.basename(path_S1_Zip[:-4]) + '.shp')

    write_shapefile(poly.ExportToWkt(), out_shp)

def getIntersectWKT(path_aoi, path_footprint):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds_aoi = driver.Open(path_aoi,0)
    layer_aoi = ds_aoi.GetLayer()
    feature_aoi = layer_aoi.GetFeature(0)
    vectorGeometry_aoi = feature_aoi.GetGeometryRef()

    ds_fp = driver.Open(path_footprint, 0)
    layer_fp = ds_fp.GetLayer()
    feature_fp = layer_fp.GetFeature(0)
    vectorGeometry_fp = feature_fp.GetGeometryRef()

    intersection = vectorGeometry_aoi.Intersection(vectorGeometry_fp)
    (minX, maxX, minY, maxY) = intersection.GetEnvelope()

    # Create ring
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(minX, minY)
    ring.AddPoint(maxX, minY)
    ring.AddPoint(maxX, maxY)
    ring.AddPoint(minX, maxY)
    ring.AddPoint(minX, minY)

    # Create polygon
    poly_envelope = ogr.Geometry(ogr.wkbPolygon)
    poly_envelope.AddGeometry(ring)


    wkt = poly_envelope.ExportToWkt()

    return wkt

def Sentinel1_preproc(path_zip, path_tmp_files, date, path_aoi):

    ### CALIBRATION
    sentinel_1 = ProductIO.readProduct(path_zip)

    parameters = HashMap()
    parameters.put('outputSigmaBand', True)
    parameters.put('selectedPolarisations', 'VV')
    parameters.put('outputImageScaleInDb', True)

    # calib = date + "_Sigma0_db_" + 'VV'
    target_0 = GPF.createProduct("Calibration", parameters, sentinel_1)
    # ProductIO.writeProduct(target_0, calib, 'BEAM-DIMAP')



    ### SUBSET

    wkt = getIntersectWKT(path_aoi, path_fp)

    # calibration = ProductIO.readProduct(calib + ".dim")
    WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')

    geom = WKTReader().read(wkt)

    parameters = HashMap()
    parameters.put('geoRegion', geom)
    parameters.put('outputImageScaleInDb', True)

    # subset = date + "_subset_" + 'VV'

    target_1 = GPF.createProduct("Subset", parameters, target_0)
    # ProductIO.writeProduct(target_1, subset, 'BEAM-DIMAP')

    ### LINEAR TO DB

    # subset_S1 = ProductIO.readProduct(subset + '.dim')

    parameters = HashMap()

    linToDB = date + "_subset_db_" + 'VV'
    target_2 = GPF.createProduct("LinearToFromdB", parameters, target_1)
    # ProductIO.writeProduct(target_2, linToDB, 'BEAM-DIMAP')


    ### TERRAIN CORRECTION

    parameters = HashMap()
    parameters.put('demResamplingMethod', 'NEAREST_NEIGHBOUR')
    parameters.put('imgResamplingMethod', 'NEAREST_NEIGHBOUR')
    parameters.put('demName', 'SRTM 3Sec')
    parameters.put('pixelSpacingInMeter', 10.0)
    parameters.put('nodataValueAtSea', False)
    # parameters.put('sourceBands', 'Sigma0_' + 'VV')

    #terrain = os.path.join(path_tmp_files, date + "_TC_" + 'VV')
    terrain = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '_VV.tif')
    target_3 = GPF.createProduct("Terrain-Correction", parameters, target_2)
    ProductIO.writeProduct(target_3, terrain, 'GeoTIFF')

    # dispose
    sentinel_1.dispose()
    target_0.dispose()
    target_1.dispose()
    target_2.dispose()
    target_3.dispose()
    Runtime.getRuntime().gc()
    System.gc()

    return terrain

def getScenes4Period(dateStart, dateEnd, path_zips):

    # Get list of Zips for a specific time frame
    files = os.listdir(path_zips)
    DATE_FORMAT = '%Y%m%d'
    start_date = datetime.strptime(str(dateStart), DATE_FORMAT).date()
    end_date = datetime.strptime(str(dateEnd), DATE_FORMAT).date()
    delta_one_day = timedelta(days=1)
    date = start_date
    zips_filtered = []
    while date <= end_date:
        # print date
        date_y_m_d = str(date)
        date_ymd = date_y_m_d.replace('-', '')
        pattern = '*_IW_GRDH_*' + date_ymd + '*.zip'

        for name in files:
            if fnmatch.fnmatchcase(name, pattern):
                zips_filtered.append(name)
        date += delta_one_day

    return zips_filtered



# INPUT PARAMETERS ##################################################################################

if not debug:
    progress.setPercentage(0)

# AOI
if not path_AOI.endswith(".shp"):
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Shapefile containing AOI' is not a shapefile (must have ending .shp). Please specify the path to the shapefile containing the AOI or choose a different type of AOI." )
    sys.exit(1)
if not os.path.exists(path_AOI):
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Shapefile containing AOI' was not found. Please specify the correct path to the shapefile or choose a different type of AOI." )
    sys.exit(1)


# Imagery
if not os.path.exists(path_imagery):
    print "Invalid input parameter: 'Directory containing imagery' not found: %s" % path_imagery
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Directory containing imagery' not found: %s" % path_imagery)

# Output directory
if not os.path.exists(pathOUT):
    print "Invalid input parameter: 'Output directory' not found: %s" % path_imagery
    raise GeoAlgorithmExecutionException("Invalid input parameter: 'Output directory' not found: %s" % path_imagery)



# Check start and end dates ---------------------------------------------------------------------------------------------------------------------------------
if startDate == "":
    raise GeoAlgorithmExecutionException("Please fill in a valid start date.")
else:
    try:
        startDate_format = datetime.strptime(startDate, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'Start date' is not valid.")

if endDate == "":
    raise GeoAlgorithmExecutionException("Please fill in a valid end date.")
else:
    try:
        endDate_format = datetime.strptime(endDate, "%Y%m%d")
    except:
        raise GeoAlgorithmExecutionException("Invalid input parameter: Format of 'End date' is not valid.")

if endDate_format < startDate_format:
    raise GeoAlgorithmExecutionException("Invalid input parameters: 'Start date'  must be earlier than 'End date'.")


# Check scenes an start pre-processing ------------------------------------------------------------------------------------------------------------------------

path_tmp_files = tempfile.mkdtemp()
print path_tmp_files

zips_filtered = getScenes4Period(startDate, endDate, path_imagery)

if len(zips_filtered) == 0:
    if not debug:
        raise GeoAlgorithmExecutionException(
            "No scenes found within the given time period. Adjust the start and end date or download scenes for this time period.")
    else:
        print "No Scenes found within the given time period. Adjust the start and end date or download scenes for this time period."
        sys.exit(1)

# Snappy pre-processing
for idx, zip in enumerate(zips_filtered):
    #print 'Begin processing of', str(len(zips_filtered)), ' Sentinel-1 scenes'
    feedback.setProgressText('Start pre-processing ' + str(idx + 1) + ' of ' + str(
         len(zips_filtered)) + ' Sentinel-1 scene(s). This could take some time')

    path_zip = os.path.join(path_imagery, zip)
    if len(zips_filtered) > 5 and (zip == zips_filtered[5]):
     raise GeoAlgorithmExecutionException(
         "You reached the maximum number of processable scenes! Please start processing with new scenes.")
     #sys.exit(1)
    if os.path.isfile(path_zip):
        date = zip[17:32]

        ### Create Footprint
        createFootprintShp(path_zip, path_tmp_files)
        path_fp = os.path.join(path_tmp_files, zip[:-4] + '.shp')

        try:
            dst = Sentinel1_preproc(path_zip, path_tmp_files, date, path_AOI)
        except:
            feedback.setProgressText("Scene and AOI not overlapping?...skip scene")
            continue

progress.setPercentage(50)
feedback.setProgressText('Compute watermask')
# Compute watermasks
# call compiled version of s1_waterdetection.py (input args: path_tmp_files, path_AOI, pathOUT)



paths_TC_tiffs_db = [w for x in os.walk(path_tmp_files) for w in glob(os.path.join(x[0], '*_VV.tif'))]

if (len(paths_TC_tiffs_db) == 1):
    date = os.path.basename(paths_TC_tiffs_db[0])[:8]
    minVal_db, maxVal_db, scaled_8bit, trans, proj = s1.rescale_to_8bit(paths_TC_tiffs_db[0])
    dst_8bit = os.path.splitext(paths_TC_tiffs_db[0])[0] + '_8bit.tif'
    s1.writeFile(dst_8bit, trans, proj, scaled_8bit, fileType='integer8')

    # Apply fast NLM filter
    denoise = s1.apply_nlm(scaled_8bit)
    denoise = np.where(denoise == 0, np.nan, denoise).astype(np.uint8)
    path_out_denoised = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '.tif')
    s1.writeFile(path_out_denoised, trans, proj, denoise, fileType='integer8')
    path_out_denoised_cliped = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '.tif')
    cmd = 'gdalwarp -cutline ' + path_AOI + ' -crop_to_cutline -dstnodata 1 ' + path_out_denoised + ' ' + path_out_denoised_cliped
    sub.call(cmd, shell=True)
    otsu_glob = s1.get_otsu_thresh(path_out_denoised_cliped)

    # Create Water mask
    min_nlm = s1.rescale_to_db(denoise, minVal_db, maxVal_db)
    watmask = s1.createWaterMask(array=denoise, glob_thresh=otsu_glob)

    path_masks = os.path.join(pathOUT, 'step6_sar_watermasks')
    if not os.path.exists(path_masks):
        os.makedirs(path_masks)
    path_out_mask_temp = os.path.join(path_masks, str(date) + '_watermask_temp.tif')
    s1.writeFile(path_out_mask_temp, trans, proj, watmask, fileType='integer8')

    ### Subset watermask with original AoI
    path_out_mask = os.path.join(path_masks, str(date) + '_watermask.tif')
    cmd = 'gdalwarp -cutline ' + path_AOI + ' -crop_to_cutline -dstnodata 1 ' + path_out_mask_temp + ' ' + path_out_mask
    sub.call(cmd, shell=True)
    os.remove(path_out_mask_temp)
else:
    # Create Stack
    date = os.path.basename(paths_TC_tiffs_db[0])[:6]
    path_vrt = os.path.join(path_tmp_files, 'stack.vrt')  # .encode('utf-8')
    path_tiff_stack = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '_stack_VV.tif')
    outds = gdal.BuildVRT(path_vrt, paths_TC_tiffs_db, separate=True)
    outds = gdal.Translate(path_tiff_stack, outds)
    outds = None

    # Compute minimum backscatter
    path_stack_min = s1.multiTempMin(path_tiff_stack)
    # Speckle filtering and watermask
    minVal_db, maxVal_db, scaled_8bit, trans, proj = s1.rescale_to_8bit(path_stack_min)
    denoise = s1.apply_nlm(scaled_8bit)
    denoise = np.where(denoise == 0, np.nan, denoise).astype(np.uint8)
    path_out_denoised = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '.tif')
    s1.writeFile(path_out_denoised, trans, proj, denoise, fileType='integer8')
    path_out_denoised_cliped = os.path.join(path_tmp_files, next(tempfile._get_candidate_names()) + '.tif')
    cmd = 'gdalwarp -cutline ' + path_AOI + ' -crop_to_cutline -dstnodata 1 ' + path_out_denoised + ' ' + path_out_denoised_cliped
    sub.call(cmd, shell=True)
    otsu_glob = s1.get_otsu_thresh(path_out_denoised_cliped)


    #stack_min_nlm = s1.rescale_to_db(denoise, minVal_db, maxVal_db)

    watmask = s1.createWaterMask(array=denoise, glob_thresh=otsu_glob)
    # watmaskTest = np.where(watmask == 255, np.nan, watmask).astype(np.uint8)

    # Export
    path_masks = os.path.join(pathOUT, 'step6_sar_watermasks')
    if not os.path.exists(path_masks):
        os.makedirs(path_masks)
    path_out_mask_temp = os.path.join(path_masks, str(date) + '_watermask_temp.tif')
    s1.writeFile(path_out_mask_temp, trans, proj, watmask, fileType='integer8')

    ### Subset watermask with original AoI
    path_out_mask = os.path.join(path_masks, str(date) + '_watermask.tif')
    cmd = 'gdalwarp -cutline ' + path_AOI + ' -crop_to_cutline -dstnodata 1 ' + path_out_mask_temp + ' ' + path_out_mask
    sub.call(cmd, shell=True)
    os.remove(path_out_mask_temp)

shutil.rmtree(path_tmp_files)

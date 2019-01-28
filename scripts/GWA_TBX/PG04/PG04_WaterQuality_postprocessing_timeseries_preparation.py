#Definition of inputs and outputs
#==================================
##BC=group
##PG04_WaterQuality_PostProcessing_for_timeseries_OLCI=name
##ParameterFile|Input_files|Select files to be processed| 
##ParameterString|outpref|Output prefix|S3A_OL
##Output_folder=folder

import gdal, osr
import time
import tempfile
import glob, os, fnmatch, subprocess
from processing.core.ProcessingConfig import ProcessingConfig
import shutil

outdir = Output_folder.replace("\\", "/") + "/"
input_files = Input_files.replace("\\", "/") 
files = input_files.split(";")
chl_folder = 'wq_postprocess_chl_'
tsm_folder = 'wq_postprocess_tsm_'
chl_eutrophic_folder = 'wq_postprocess_chl_eutrophic_'
#float_folder = 'wq_postprocess_veg_'

def folder_create(tempfolder):
    try:
        tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
        return tempdir
    except:
        #progress.setConsoleInfo('Temporary folder:' + tempfolder + ' does not exist and will be created.')
        tempfile.mkdtemp(prefix=tempfolder)
        tempdir = glob.glob(os.path.join(tempfile.gettempdir(), tempfolder + '*'))[0]
        return tempdir

def locate_file(pattern, root_path):
    for path, dirs, files in os.walk(root_path):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

def GetGeoInfo(inData):
    inWkt = inData.GetProjection()
    GeoT = inData.GetGeoTransform()
    rows = inData.RasterYSize
    cols = inData.RasterXSize
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(inData.GetProjectionRef())
    pixelRes = inData.GetGeoTransform()[1]
    return (inWkt, GeoT, rows, cols, Projection, pixelRes)


def writeGTiff(outFn, Array, driver, rows, cols, GeoT, Projection):
    DataSet = driver.Create(outFn, cols, rows, 1, gdal.GDT_Float32)
    # DataSet = driver.Create(outFn, cols, rows, 1, gdal.GDT_UInt16)
    DataSet.SetGeoTransform(GeoT)
    DataSet.SetProjection(Projection.ExportToWkt())
    DataSet.GetRasterBand(1).WriteArray(Array)


def execution(outdir, files, chl_folder, tsm_folder, chl_eutrophic_folder):
    
    ##chl
    tempdir_chl = folder_create(chl_folder) + '/'
    for x in range(len(files)):
        start = time.time()
        filename = files[x].split("/")[len(files[x].split("/")) - 1]
        name = outpref
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        inData1 = gdal.Open(files[x])
        raster1 = inData1.GetRasterBand(5)
        rasterAr1 = raster1.ReadAsArray()
        inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData1)
        if x < 10:
            outFn = tempdir_chl + name + '_chl00' + str(x) + '.tif'
        elif x < 100:
            outFn = tempdir_chl + name + '_chl0' + str(x) + '.tif'
        else:
            outFn = tempdir_chl + name + '_chl' + str(x) + '.tif'
        writeGTiff(outFn, rasterAr1, driver, rows, cols, GeoT, Projection)
        
    chl_files_list = [file for file in locate_file('*.tif', tempdir_chl)]
    cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_chl_timeseries.tif" '

    for n in range(len(chl_files_list)):
        cmnd += '"' + str(chl_files_list[n]) + '" '

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, ''):
        progress.setText(line)

    shutil.rmtree(tempdir_chl)

    ## tsm
    tempdir_tsm = folder_create(tsm_folder) + '/'
    for x in range(len(files)):
        start = time.time()
        filename = files[x].split("/")[len(files[x].split("/")) - 1]
        name = outpref
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        inData2 = gdal.Open(files[x])
        raster2 = inData2.GetRasterBand(7)
        rasterAr2 = raster2.ReadAsArray()
        inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData2)
        if x < 10:
            outFn = tempdir_tsm + name + '_tsm00' + str(x) + '.tif'
        elif x < 100:
            outFn = tempdir_tsm + name + '_tsm0' + str(x) + '.tif'
        else:
            outFn = tempdir_tsm + name + '_tsm' + str(x) + '.tif'
        writeGTiff(outFn, rasterAr2, driver, rows, cols, GeoT, Projection)

    tsm_files_list = [file for file in locate_file('*.tif', tempdir_tsm)]
    cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_tsm_timeseries.tif" '

    for n in range(len(tsm_files_list)):
        cmnd += '"' + str(tsm_files_list[n]) + '" '

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, ''):
        progress.setText(line)

    shutil.rmtree(tempdir_tsm)

    ##chl_eutrophic
    tempdir_chl_eutrophic = folder_create(chl_eutrophic_folder) + '/'
    for x in range(len(files)):
        start = time.time()
        filename = files[x].split("/")[len(files[x].split("/")) - 1]
        name = outpref
        driver = gdal.GetDriverByName('GTiff')
        driver.Register()
        inData3 = gdal.Open(files[x])
        raster3 = inData3.GetRasterBand(3)
        rasterAr3 = raster3.ReadAsArray()
        inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData3)
        if x < 10:
            outFn = tempdir_chl_eutrophic + name + '_chl_eutrophic00' + str(x) + '.tif'
        elif x < 100:
            outFn = tempdir_chl_eutrophic + name + '_ch_eutrophicl0' + str(x) + '.tif'
        else:
            outFn = tempdir_chl_eutrophic + name + '_chl_eutrophic' + str(x) + '.tif'
        writeGTiff(outFn, rasterAr3, driver, rows, cols, GeoT, Projection)
        
    chl_eutrophic_files_list = [file for file in locate_file('*.tif', tempdir_chl_eutrophic)]
    cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_chl_eutrophic_timeseries.tif" '

    for n in range(len(chl_eutrophic_files_list)):
        cmnd += '"' + str(chl_eutrophic_files_list[n]) + '" '

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, ''):
        progress.setText(line)

    shutil.rmtree(tempdir_chl_eutrophic)


execution(outdir, files, chl_folder, tsm_folder, chl_eutrophic_folder)
import gdal, osr
import time

from qgis.processing import alg


@alg(
    name="pg04waterqualitypostprocessingfortimeseriesmeris",
    label=alg.tr("PG04_WaterQuality_PostProcessing_for_timeseries_MERIS"),
    group="bc",
    group_label=alg.tr("BC")
)
@alg.input(type=alg.FILE, name="Input_folder", label="Select files to be processed")
@alg.input(type=alg.STRING, name="outpref", label="Output prefix", default="MER_FRS")
@alg.input(type=alg.FOLDER_DEST, name="Output_folder", label="Output directory")
def algorithm(instance, parameters, context, feedback, inputs):
    """
    Optical-SAR Water and Wetness Fusion
    """
    main()


def main(Input_folder, outpref, Output_folder, res, mem):
    import tempfile
    import glob, os, fnmatch, subprocess
    from processing.core.ProcessingConfig import ProcessingConfig
    import shutil

    outdir = Output_folder.replace("\\", "/") + "/"
    input_files = Input_files.replace("\\", "/") 
    files = input_files.split(";")
    chl_oli_folder = 'wq_postprocess_chl_oli_'
    chl_eu_folder = 'wq_postprocess_chl_eu_'
    tsm_folder = 'wq_postprocess_tsm_'
    turb_folder = 'wq_postprocess_turb_'

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


    def execution(outdir, files, chl_oli_folder, chl_eu_folder, tsm_folder, turb_folder):
        
        ##chl_oli
        tempdir_chl_oli = folder_create(chl_oli_folder) + '/'
        for x in range(len(files)):
            start = time.time()
            filename = files[x].split("/")[len(files[x].split("/")) - 1]
            name = outpref
            driver = gdal.GetDriverByName('GTiff')
            driver.Register()
            inData1 = gdal.Open(files[x])
            raster1 = inData1.GetRasterBand(3)
            rasterAr1 = raster1.ReadAsArray()
            inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData1)
            if x < 10:
                outFn = tempdir_chl_oli + name + '_chl_oli00' + str(x) + '.tif'
            elif x < 100:
                outFn = tempdir_chl_oli + name + '_chl_oli0' + str(x) + '.tif'
            else:
                outFn = tempdir_chl_oli + name + '_chl_oli' + str(x) + '.tif'
            writeGTiff(outFn, rasterAr1, driver, rows, cols, GeoT, Projection)
            
        chl_oli_files_list = [file for file in locate_file('*.tif', tempdir_chl_oli)]
        cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_chl_oligotrophic_timeseries.tif" '

        for n in range(len(chl_oli_files_list)):
            cmnd += '"' + str(chl_oli_files_list[n]) + '" '

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, ''):
            progress.setText(line)

        shutil.rmtree(tempdir_chl_oli)
        
            ##chl_eu
        tempdir_chl_eu = folder_create(chl_eu_folder) + '/'
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
                outFn = tempdir_chl_eu + name + '_chl_eu00' + str(x) + '.tif'
            elif x < 100:
                outFn = tempdir_chl_eu + name + '_chl_eu0' + str(x) + '.tif'
            else:
                outFn = tempdir_chl_eu + name + '_chl_eu' + str(x) + '.tif'
            writeGTiff(outFn, rasterAr1, driver, rows, cols, GeoT, Projection)
            
        chl_eu_files_list = [file for file in locate_file('*.tif', tempdir_chl_eu)]
        cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_chl_eutrophic_timeseries.tif" '

        for n in range(len(chl_eu_files_list)):
            cmnd += '"' + str(chl_eu_files_list[n]) + '" '

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, ''):
            progress.setText(line)

        shutil.rmtree(tempdir_chl_eu)

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
        
        
        ## turbidity
        tempdir_turb = folder_create(turb_folder) + '/'
        for x in range(len(files)):
            start = time.time()
            filename = files[x].split("/")[len(files[x].split("/")) - 1]
            name = outpref
            driver = gdal.GetDriverByName('GTiff')
            driver.Register()
            inData2 = gdal.Open(files[x])
            raster2 = inData2.GetRasterBand(9)
            rasterAr2 = raster2.ReadAsArray()
            inWkt, GeoT, rows, cols, Projection, pixelRes = GetGeoInfo(inData2)
            if x < 10:
                outFn = tempdir_turb + name + '_turb00' + str(x) + '.tif'
            elif x < 100:
                outFn = tempdir_turb + name + '_turb0' + str(x) + '.tif'
            else:
                outFn = tempdir_turb + name + '_turb' + str(x) + '.tif'
            writeGTiff(outFn, rasterAr2, driver, rows, cols, GeoT, Projection)

        turb_files_list = [file for file in locate_file('*.tif', tempdir_turb)]
        cmnd = 'python gdal_merge.py -separate -o "'+ outdir + name + '_turbidity_timeseries.tif" '

        for n in range(len(turb_files_list)):
            cmnd += '"' + str(turb_files_list[n]) + '" '

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmnd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in iter(process.stdout.readline, ''):
            progress.setText(line)

        shutil.rmtree(tempdir_turb)


    execution(outdir, files, chl_oli_folder, chl_eu_folder, tsm_folder, turb_folder)
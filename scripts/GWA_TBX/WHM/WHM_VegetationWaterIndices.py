#Definition of inputs and outputs
#==================================
##Vegetation and Water Indices WHM=name
##Wetland Habitat Mapping=group
##ParameterRaster|input|Input Reflectance Stack|False
##ParameterSelection|sat|Satellite|Sentinel-2;Landsat|Sentinel-2
##OutputDirectory|outputDirectory|Folder to save the stack of Indices

# Call the function for Sentinel 2 /Landsat indices calculation
#==================================
import os
import sys
here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)
import sen2indices_whm
import landsatindices

progress.setConsoleInfo('Starting index calculation...')
if sat == 0:
    sen2indices_whm.sen2indices(input, outputDirectory)
elif sat == 1:
    landsatindices.landsatindices(input, outputDirectory)
progress.setConsoleInfo('Done.')
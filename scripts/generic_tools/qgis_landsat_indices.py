#Definition of inputs and outputs
#==================================
##Landsat Indices=name
##Landsat Tools=group
##ParameterRaster|input|Input Reflectance Stack|False
##OutputDirectory|outputDirectory|Folder to save the stack of Indices
#OutputRaster|output|Name for Index Stack

# Call the function for Landsat index calculation
#==================================
import os
import sys

here = os.path.dirname(scriptDescriptionFile)
if here not in sys.path:
    sys.path.append(here)
import landsat_indices
from processing.tools import dataobjects

print 'Starting index calculation...'
out_file = landsat_indices.landsat_indices(input, outputDirectory)
dataobjects.load(out_file, isRaster=True)
print 'Finished writing to disk...'


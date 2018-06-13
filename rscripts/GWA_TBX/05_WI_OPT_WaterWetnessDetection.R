#  Copyright (c) 2017, GeoVille Information Systems GmbH
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, is prohibited for all commercial applications without
# licensing by GeoVille GmbH.
#
#
# Date created: 06.05.2017
# Date last modified: 09.06.2017
#
#
# __author__ = "Christina Ludwig"
# __version__ = "1.0"


# INPUT PARAMTERS

# -> FOR QGIS Processing modules
##Water and Wetness Detection=name
##Wetland Inventory=group
##Directory_containing_indices=folder
##Directory_containing_TWI=folder
##Output_Directory=folder
##Start_Date=optional string
##End_Date=optional string
##Minimum_water_probability=number 45
##Minimum_wetness_probability_bare_soil=number 50
##Minimum_wetness_probability_sparse_vegetation=number 50
##Minimum_wetness_probability_dense_vegetation=number 50
##Minimum_mapping_unit=number 3
##Plot_probability= Boolean False
##Plot_certainty_indicator= Boolean False

DEBUG <- F

# -> Test parameters for execution in R
if (DEBUG) {
  #Directory_containing_indices= "T:\\Processing\\2687_GW_A\\03_Products\\GWA-TOOLBOX\\02_InterimProducts\\WI\\indices"
  Directory_containing_indices= "I:\\temp\\GWA_TBX_137\\indices"
  Directory_containing_TWI= "T:\\Processing\\2687_GW_A\\03_Products\\GWA-TOOLBOX\\workshop_June2017\\Trainingkits_UCD\\WI\\WI\\02_InterimProducts\\example_site\\step05_TWI"
  Output_Directory="I:\\temp\\GWA_TBX_137_2"
  Minimum_water_probability = 50
  Minimum_wetness_probability_bare_soil = 55
  Minimum_wetness_probability_sparse_vegetation = 55
  Minimum_wetness_probability_dense_vegetation = 65
  Start_Date <- "20170101"
  End_Date <- "20170301"
  Minimum_mapping_unit = 3
  Plot_certainty_indicator = F
  Plot_probability <- T
  .libPaths("C:\\Users\\ludwig\\.qgis2\\processing\\rlibs")
}


# Load libraries ----------------------------------------------------------
library(raster)
library(rgdal)
library(rpanel)
library(stringr)

#source("I:\\2687_GW_A\\04_CODE\\git_repos\\GWA_scripts\\rscripts\\GWA_TBX\\GWAutils\\R\\GWAutils.R")
library(GWAutils)

WI_workflow(Directory_containing_indices,
            Directory_containing_TWI,
            Output_Directory,
            Minimum_water_probability, 
            Start_Date,
            End_Date,
            Minimum_mapping_unit,
            Plot_certainty_indicator,
            Plot_probability)

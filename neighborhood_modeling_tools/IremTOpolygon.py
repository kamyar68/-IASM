# this tool converts IREM to polygon based on specified expsoure values
# this tool needs a raster file for each individual as the exposure model
# developer: Kamyar Hasanzadeh, date: 11.2017
# Developed in Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
# original version 1.0.0
# Working with GUI - comments added
# last modified 6.3.2018
## -------------------------------------------------------------
# Importing required modules
import arcpy  
from arcpy import env  
from arcpy.sa import * 
import numpy
# dumping old files from memory
arcpy.Delete_management("in_memory")
## specifying input and output files/parameteres
# setting workspace to the same folder where raster files are stored
# the raster must have 1 band only
env.workspace = arcpy.GetParameterAsText(0)
# the folder where output will be saved
workpath=arcpy.GetParameterAsText(1)
# name of the output file (it will be a shapefile)
outputname=arcpy.GetParameterAsText(2)
# the percentile used for extracting high exposure areas
# 0 <= prcntil <= 100
prcntil=arcpy.GetParameter(3)
#do you want to simplify ouput polygon's shape? Boolean (true or false)
simplified=arcpy.GetParameter(4)
#---- preparing the parameteres and paths
# tempol is a working shapefile that will be deleted after the process
tempol= workpath+'/workingfile.shp'
tempuni=workpath+'/workingunifile.shp'
outputname=outputname+'.shp'
if simplified==1:
    simplification='SIMPLIFY'
else:
    simplification= 'NO_SIMPLIFY'
## main functionalities
env.overwriteOutput=True
# list existing raster files for iteration
rasters = arcpy.ListRasters() 
i=1 #iteration controller1
# here we identify percentile eposure value for each IREM 
for inRaster in rasters:
    #read uid from raster files name
    # files must be named according to instructions for this to work
    # valid file name structure: LETTERS_uid where uid is the unique numerical identifier for individuals
    uid=int(inRaster .rsplit('_', 1)[1])
    print uid
    arcpy.AddMessage( "start creating boundaries for uid %u"%uid)
    array = arcpy.RasterToNumPyArray(inRaster, nodata_to_value = 0)
    a=array.flatten()
    b=numpy.trim_zeros(a)
    print b
    d= b[b != 0]
    e=numpy.unique(d)
    pcl_value= numpy.percentile(e, prcntil)
    max=numpy.amax(a) 
    print pcl_value
    myRemapRange = RemapRange ([[0,pcl_value,0],[pcl_value, max,1]])
    arcpy.CheckOutExtension("spatial")
    #reclassify the raster using the identified exposure value
    reclassified=Reclassify (inRaster, "Value", myRemapRange)
    arcpy.CheckInExtension("spatial")
    # convert raster to polygon - this creates boundaries for extracted areas
    arcpy.RasterToPolygon_conversion(reclassified, tempol, simplification)
    # write the individual unique identifier to the file (as a field named 'uid')
    arcpy.AddField_management (tempol, 'uid', "LONG", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(tempol, "uid", uid,"PYTHON")
    count=0 # iteration controller2
    # check if the extracted areas for the individual include multiple polygons
    with arcpy.da.UpdateCursor(tempol, ["gridcode"]) as cursor:
        for row in cursor:
            count=count+1
            if row[0] == 0:
                cursor.deleteRow()
                count=count-1
    # if the extracted area for the individual includes several polygons 
    if count >1:
        
        # perform union and dissolve to assign multiple polygones to one individual an done row in output
        arcpy.Union_analysis (tempol, tempuni, "ALL")
        arcpy.Dissolve_management (tempol, tempuni, 'uid', '#', 'MULTI_PART', '#')
        poly='yes'
        
    else:
        
        poly='no'
    #in the follwoing lines the output will be copied form the temp work file to the output file specified by user 
    if i==1:
        arcpy.CreateFeatureclass_management (workpath, outputname, "POLYGON", tempol, "DISABLED", "DISABLED", tempol, '#', '#', '#', '#')
        
    i=i+1
    output=workpath+'/'+outputname
    if poly=='yes':
        arcpy.Append_management (tempuni, output, 'NO_TEST', '#', '#')
    else:
        arcpy.Append_management (tempol, output, 'NO_TEST', '#', '#')
    # delete remaining working files from hard disk
    arcpy.Delete_management(tempol)
    arcpy.Delete_management(reclassified)

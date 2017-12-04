# this tool converts IREM to polygon based on given values
# developer: Kamyar Hasanzadeh, date: 11.2017
# YTK, Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
# original version 1.0.0
# Working with GUI
# last modified 4.12.2017
import arcpy  
from arcpy import env  
from arcpy.sa import * 
import numpy
arcpy.Delete_management("in_memory")
env.workspace = arcpy.GetParameterAsText(0)
workpath=arcpy.GetParameterAsText(1)
outputname=arcpy.GetParameterAsText(2)
prcntil=arcpy.GetParameter(3)
simplified=arcpy.GetParameter(4)
#---- prepare inputs
tempol= workpath+'/workingfile.shp'
tempuni=workpath+'/workingunifile.shp'
outputname=outputname+'.shp'
if simplified==1:
    simplification='SIMPLIFY'
else:
    simplification= 'NO_SIMPLIFY'
# ----
env.overwriteOutput=True
rasters = arcpy.ListRasters() 
i=1 #so that we create feature class only in the first iteration
# identify percentile value for each IREM then reclassify and then polyg
for inRaster in rasters:
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
    reclassified=Reclassify (inRaster, "Value", myRemapRange)
    arcpy.CheckInExtension("spatial")
    arcpy.RasterToPolygon_conversion(reclassified, tempol, simplification)
    arcpy.AddField_management (tempol, 'uid', "LONG", "", "", "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management(tempol, "uid", uid,"PYTHON")
    count=0 # this is to check if we need to perform union
    with arcpy.da.UpdateCursor(tempol, ["gridcode"]) as cursor:
        for row in cursor:
            count=count+1
            if row[0] == 0:
                cursor.deleteRow()
                count=count-1
    #arcpy.CreateFeatureclass_management ('in_memory', 'unipol', "POLYGON", outPolygons, "DISABLED", "DISABLED", '#', '#', '#', '#', '#')
    if count >1:
        arcpy.Union_analysis (tempol, tempuni, "ALL")
        arcpy.Dissolve_management (tempol, tempuni, 'uid', '#', 'MULTI_PART', '#')
        poly='yes'
        
    else:
        
        poly='no'
    
    if i==1:
        arcpy.CreateFeatureclass_management (workpath, outputname, "POLYGON", tempol, "DISABLED", "DISABLED", tempol, '#', '#', '#', '#')
        
    i=i+1
    output=workpath+'/'+outputname
    if poly=='yes':
        arcpy.Append_management (tempuni, output, 'NO_TEST', '#', '#')
    else:
        arcpy.Append_management (tempol, output, 'NO_TEST', '#', '#')
    arcpy.Delete_management(tempol)
    arcpy.Delete_management(reclassified)

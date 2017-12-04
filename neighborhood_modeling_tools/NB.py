# This is part 2: Creating dynamic neighborhood boundary 
import arcpy
from arcpy import env
env.workspace = r"in_memory"
env.overwriteOutput=True
poif=arcpy.GetParameterAsText(0)  #filtered poi
home= arcpy.GetParameterAsText(1)   #home locations
output= arcpy.GetParameterAsText(2)  # this will be the output file
poibufd= arcpy.GetParameter(3)
hombufd= arcpy.GetParameter(4)
arcpy.Buffer_analysis(home, 'bufhom', hombufd, "FULL", "ROUND", "NONE", "", "PLANAR")
arcpy.Buffer_analysis(poif, 'bufpoi', poibufd, "FULL", "ROUND", "NONE", "", "PLANAR")
arcpy.CreateFeatureclass_management ('in_memory', 'tempnb', "POLYGON", 'bufhom', "DISABLED", "DISABLED", home, '#', '#', '#', '#')
cursor3 = arcpy.SearchCursor('bufhom')
for row in cursor3:
    u=row.uid
    print u
    delimfield = arcpy.AddFieldDelimiters('bufhom', 'uid')
    arcpy.Select_analysis('bufhom', 'homsel', "{0} = {1}".format(delimfield, u))
    arcpy.Select_analysis('bufpoi', 'poisel', "{0} = {1}".format(delimfield, u))
    arcpy.Union_analysis(['poisel','homsel'], 'union1', "ALL", "", "GAPS")
    arcpy.Dissolve_management('union1', 'solidnb', "", "", "SINGLE_PART", "DISSOLVE_LINES")
    arcpy.MinimumBoundingGeometry_management('solidnb', 'mcp', "CONVEX_HULL", "ALL", "", "MBG_FIELDS")
    # make sure that the field uid exists
    if len(arcpy.ListFields('mcp',"uid"))==0:
        arcpy.AddField_management ('mcp', "uid", "LONG", "#", "#", "#", "#", "NULLABLE", "REQUIRED", '#')
        arcpy.CalculateField_management ('mcp', 'uid', u)
    arcpy.Append_management ('mcp', 'tempnb', 'NO_TEST', '#', '#')
del row, cursor3
arcpy.CopyFeatures_management('tempnb', output)
arcpy.Delete_management("in_memory") 
print "Process completed, output files are Ready"
    
    


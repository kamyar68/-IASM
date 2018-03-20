# this tool creates a home range boundary for individuals
# the tool iterates through individuals using a unique udentifier names 'uid'
# developer: Kamyar Hasanzadeh, date: 11.2017
# Developed in Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
# external reference (Hasanzadeh, 2017) accessible at: https://www.sciencedirect.com/science/article/pii/S0143622817304034
# original version 1.0.1
# Working with GUI
# Comments added
# last modified 6.03.2018
## ---------------------------------------------------------------
# Importing required modules
import arcpy
from arcpy import env
# seting work enviornment to memory for a faster process
# consider changing the workspace to hard disk if low on physical memory (RAM)
env.workspace = r"in_memory"
env.overwriteOutput=True
## specifying input and output files/parameteres
#activity points (must include uid field)
poif=arcpy.GetParameterAsText(0)
#home points (must include uid field)  
home= arcpy.GetParameterAsText(1)
# this will be the output file (shapefile)   
output= arcpy.GetParameterAsText(2)  
# buffer around visited points (140 m by default, according to Hasanzadeh,2017)
poibufd= arcpy.GetParameter(3)
# buffer around home points (500 m by default, according to Hasanzadeh,2017)
hombufd= arcpy.GetParameter(4)
#Do you want to apply home range distance (d3) threshold?
apply_d3=arcpy.GetParameter(5)
# d3 value  (home range distance)
d3=arcpy.GetParameter(6)
## apply d3 (if True)- filter points
if apply_d3==1:
    poi_filtered=r'in_memory/poifiltered'
    delimfield = arcpy.AddFieldDelimiters(poif, 'dist')
    arcpy.Select_analysis(poif, poi_filtered, "{0} <= {1}".format(delimfield, d3))
    poif=poi_filtered
## Main functionalities
# applying buffer around home and activity points
arcpy.Buffer_analysis(home, 'bufhom', hombufd, "FULL", "ROUND", "NONE", "", "PLANAR")
arcpy.Buffer_analysis(poif, 'bufpoi', poibufd, "FULL", "ROUND", "NONE", "", "PLANAR")
# creating a temporary working feature class in Memory
arcpy.CreateFeatureclass_management ('in_memory', 'tempnb', "POLYGON", 'bufhom', "DISABLED", "DISABLED", home, '#', '#', '#', '#')
# Cursor iterating through individuals using unique numerical identifier field 'uid'
cursor3 = arcpy.SearchCursor('bufhom')
for row in cursor3:
    u=row.uid
    print u
    # identifying the proper Field delimiters for the follwoing Select step 
    delimfield = arcpy.AddFieldDelimiters('bufhom', 'uid')
    # Selecting activity and home points for each individual for iteration
    arcpy.Select_analysis('bufhom', 'homsel', "{0} = {1}".format(delimfield, u))
    arcpy.Select_analysis('bufpoi', 'poisel', "{0} = {1}".format(delimfield, u))
    # Uniting and dissolving the home and activity points buffers to apply the bounding geometry (convex hull)
    arcpy.Union_analysis(['poisel','homsel'], 'union1', "ALL", "", "GAPS")
    arcpy.Dissolve_management('union1', 'solidnb', "", "", "SINGLE_PART", "DISSOLVE_LINES")
    # applying a convex hull
    arcpy.MinimumBoundingGeometry_management('solidnb', 'mcp', "CONVEX_HULL", "ALL", "", "MBG_FIELDS")
    # this makes sure that the field uid exists in the newly created file (the convex hull)
    if len(arcpy.ListFields('mcp',"uid"))==0:
        arcpy.AddField_management ('mcp', "uid", "LONG", "#", "#", "#", "#", "NULLABLE", "REQUIRED", '#')
    arcpy.CalculateField_management ('mcp', 'uid', u)
        # append the individual home range to the temporary output file in memory
    arcpy.Append_management ('mcp', 'tempnb', 'NO_TEST', '#', '#')
del row, cursor3
# copy the temporary output file from memory to the specified location of hard disk 
arcpy.CopyFeatures_management('tempnb', output)
# clean memory
arcpy.Delete_management("in_memory") 
print "Process completed, output files are Ready"
    
    


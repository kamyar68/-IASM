# This tool creates an individualized residential exporsure model for individuals(IREM)
# the tool iterates through individuals using a unique udentifier names 'uid'
# if needed, this tool also includes the home range boundary modeling code -required if not modeled already
# Author: Kamyar Hasanzadeh
# Developed in Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
# Version 2.1.4
# bugs fixed
# Changes: working with GUI - comments added
## ---------------------------
# Import required modules for code part one: home range modeling
import arcpy
from arcpy import env
# dumping old files from memory
arcpy.Delete_management("in_memory")
# for calculating the elapsed time
t1 = time.time()
# seting work enviornment to memory for a faster process
# consider changing the workspace to hard disk if low on physical memory (RAM)
from arcpy import env
env.workspace = r"in_memory"
env.overwriteOutput=True
## specifying input and output files/parameteres
# consider path in creating boundaries - recommended:'yes'
consider_paths= 'yes'
#home points (must include uid field)
home= arcpy.GetParameterAsText(0)
#activity points (must include uid field)
poi=arcpy.GetParameterAsText(1) 
#travel routes taken to reach activity points (estimated or actual) 
roads=arcpy.GetParameterAsText(2)
# output for home range boundary file
output=arcpy.GetParameterAsText(3)
# folder for saving output raster files (IREM)
directory=arcpy.GetParameterAsText(4) #raster output
# buffer around home points (500 m by default, according to Hasanzadeh,2017)
hombufd= arcpy.GetParameter(5)
# buffer around visited points (140 m by default, according to Hasanzadeh,2017)
poibufd= arcpy.GetParameter(6)
# maximum weight assigned to features - e.g. 30 as a maxumum frequency of visit (30 times per month)
maxw=arcpy.GetParameter(7)
# travel modes affect the exposure estimation - Boolean (0 or 1)
consider_mod= arcpy.GetParameter(8)
# if the previous parameter was set True, then prvovide values for the following
# in the field 'tmode', how is mode 1 named? string
mode1=arcpy.GetParameterAsText(9)
# what is the average travel speed for mode 1 -double
speed1=arcpy.GetParameter(10)
# in the field 'tmode', how is mode 2 named? string
mode2=arcpy.GetParameterAsText(11)
# what is the average travel speed for mode 2 -double
speed2=arcpy.GetParameter(12)
# what is the average travel speed for mode 3 -double
# enter any random value  if no other modes exist
speed3=arcpy.GetParameter(13)
# Do you want to reduce deatails in output raster? (generalized, less detailed, better visualization)
make_smooth=arcpy.GetParameter(14)
# if the previous was set to true, enter radius for generalization below
rad=arcpy.GetParameter(15)
# have yo already created home range boundaries? - Boolean (True or False)
have_boundaries=arcpy.GetParameter(16)
# if above parametere is true, provide the path for it below
already_boundary=arcpy.GetParameterAsText(17)

## create home range boundaries
# this step will be skipped if boundaries are already available and provided
if have_boundaries==0:
    buf_dist=10 # road buffer distance
    
    # creating boundary
    print "start creating boundary"
    # counting number of individuals for use in progress estimator
    result = arcpy.GetCount_management(home)
    fc_count = int(result.getOutput(0))
    arcpy.SetProgressor("step", "Step1: Creating boundaries...",0, fc_count, 1)
    arcpy.AddMessage( "start creating boundary") 
    # applying buffer around travel routes, home, and activity points
    arcpy.Buffer_analysis(home, 'bufhom', hombufd, "FULL", "ROUND", "NONE", "", "PLANAR")
    arcpy.Buffer_analysis(poi, 'bufpoi', poibufd, "FULL", "ROUND", "NONE", "", "PLANAR")
    if consider_paths== 'yes':
        arcpy.Buffer_analysis(roads, 'bufroad', buf_dist, "FULL", "ROUND", "NONE", "", "PLANAR")
    # create temporary output in memory    
    arcpy.CreateFeatureclass_management ('in_memory', 'tempnb', "POLYGON", 'bufhom', "DISABLED", "DISABLED", home, '#', '#', '#', '#')
    # iterate through individuals in this cursor
    cursor3 = arcpy.SearchCursor('bufhom')
    for row in cursor3:
        u=row.uid
        print u
        delimfield = arcpy.AddFieldDelimiters('bufhom', 'uid')
        arcpy.Select_analysis('bufhom', 'homsel', "{0} = {1}".format(delimfield, u))
        arcpy.Select_analysis('bufpoi', 'poisel', "{0} = {1}".format(delimfield, u))
        if consider_paths== 'yes':
            arcpy.Select_analysis('bufroad', 'roadsel', "{0} = {1}".format(delimfield, u))
            arcpy.Union_analysis(['poisel','homsel','roadsel'], 'union1', "ALL", "", "GAPS")
        elif consider_paths== 'no':
            arcpy.Union_analysis(['poisel','homsel'], 'union1', "ALL", "", "GAPS")
        arcpy.Dissolve_management('union1', 'solidnb', "", "", "SINGLE_PART", "DISSOLVE_LINES")
        arcpy.MinimumBoundingGeometry_management('solidnb', 'mcp', "CONVEX_HULL", "ALL", "", "MBG_FIELDS")
        # make sure that the field uid exists
        if len(arcpy.ListFields('mcp',"uid"))==0:
            arcpy.AddField_management ('mcp', "uid", "LONG", "#", "#", "#", "#", "NULLABLE", "REQUIRED", '#')
            arcpy.CalculateField_management ('mcp', 'uid', u)
        arcpy.Append_management ('mcp', 'tempnb', 'NO_TEST', '#', '#')
        arcpy.SetProgressorPosition()
    del row, cursor3
    # export home range output to the path in hard disk as specified by user
    arcpy.CopyFeatures_management('tempnb',output)
    print "Boundaries are created"
    arcpy.ResetProgressor()
    arcpy.AddMessage("Boundaries are created")
##----------------------------
## ---------------------------
## code part two: creating IREM
# Import modules
import arcpy, arcinfo
import time
import sys
import os
from arcpy import AddError
from arcpy import AddField_management
from arcpy import AddMessage
from arcpy import AddWarning
from arcpy import ApplySymbologyFromLayer_management
from arcpy import Array
from arcpy import CopyFeatures_management
from arcpy import env
from arcpy import Exists
from arcpy import MakeFeatureLayer_management
from arcpy import Point
from arcpy import Polyline
from arcpy import SaveToLayerFile_management
from os.path import join
from sys import argv
from sys import path
from arcpy.sa import *
# clear memory
arcpy.Delete_management("in_memory")
# for calculating elapsed time
t1 = time.time()
# seting work enviornment to memory for a faster process
# consider changing the workspace to hard disk if low on physical memory (RAM)
env.workspace = r"in_memory"
env.overwriteOutput=True
buf_dist=25 # road buffer distance
# assign the home range boundary file to the variable
if have_boundaries==0:
    solid_nb=output
else:
    solid_nb=already_boundary
# #################
## Convert lines to points
# when this function is called the input line will be converted to a pointed line with equal intervals -as specified.
def pointmaker(infc,outfc,intvl,uid_or_w):
    #print "running line to point tool"
    #arcpy.AddMessage("running line to point tool")
    in_fc = infc
    out_fc = outfc
    interval = intvl
    use_percentage = "VALUE"
    end_points = "NO_END_POINTS"
    desc = arcpy.Describe(in_fc)
# Create output feature class
    # arcpy.CreateFeatureclass_management(
    # os.path.dirname(out_fc),
    # os.path.basename(out_fc),
    # geometry_type="POINT",
    # spatial_reference=desc.spatialReference)
    arcpy.CreateFeatureclass_management('in_memory',out_fc,"POINT")
    # Add a field to transfer FID from input
    if uid_or_w=='w':
        fid_name = "w"
        arcpy.AddField_management(out_fc, fid_name, "DOUBLE")
        # Create new points based on input lines
        with arcpy.da.SearchCursor(
    # in_fc, ['SHAPE@', desc.OIDFieldName]) as search_cursor:
            in_fc, ['SHAPE@', 'w_road']) as search_cursor:    
                with arcpy.da.InsertCursor(
                    out_fc, ['SHAPE@', fid_name]) as insert_cursor:
                        for row in search_cursor:
                            line = row[0]
    
                            if line:  # if null geometry--skip
                                if end_points:
                                    insert_cursor.insertRow([line.firstPoint, row[1]])
    
                                cur_length = interval
                                
                            
    
                                max_position = line.length
                                
    
                                while cur_length < max_position:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(
                                            cur_length), row[1]])
                                    cur_length += interval
                                    
    
                                if end_points:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(1, True), row[1]])
    if uid_or_w=='uid':
        fid_name = "uid"
        arcpy.AddField_management(out_fc, fid_name, "SHORT")
        # Create new points based on input lines
        with arcpy.da.SearchCursor(
    # in_fc, ['SHAPE@', desc.OIDFieldName]) as search_cursor:
            in_fc, ['SHAPE@', 'uid']) as search_cursor:    
                with arcpy.da.InsertCursor(
                    out_fc, ['SHAPE@', fid_name]) as insert_cursor:
                        for row in search_cursor:
                            line = row[0]
    
                            if line:  # if null geometry--skip
                                if end_points:
                                    insert_cursor.insertRow([line.firstPoint, row[1]])
    
                                cur_length = interval
                         
    
                                max_position = line.length
                                
                                while cur_length < max_position:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(
                                            cur_length), row[1]])
                                    cur_length += interval
                                    
    
                                if end_points:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(1, True), row[1]])
                                        
    if uid_or_w=='POI_ID':
        fid_name = "POI_ID"
        arcpy.AddField_management(out_fc, fid_name, "SHORT")
        # Create new points based on input lines
        with arcpy.da.SearchCursor(
    # in_fc, ['SHAPE@', desc.OIDFieldName]) as search_cursor:
            in_fc, ['SHAPE@', 'POI_ID']) as search_cursor:    
                with arcpy.da.InsertCursor(
                    out_fc, ['SHAPE@', fid_name]) as insert_cursor:
                        for row in search_cursor:
                            line = row[0]
    
                            if line:  # if null geometry--skip
                                if end_points:
                                    insert_cursor.insertRow([line.firstPoint, row[1]])
    
                                cur_length = interval
                         
    
                                max_position = line.length
                                
                                while cur_length < max_position:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(
                                            cur_length), row[1]])
                                    cur_length += interval
                                    
    
                                if end_points:
                                    insert_cursor.insertRow(
                                        [line.positionAlongLine(1, True), row[1]])
                                    

## calculate weights
# making sure that the field doesn't already exist in activity points file
arcpy.DeleteField_management(poi,"w")
arcpy.AddField_management(poi, "w", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
# defining weights for activity points using formula described in (Hasanzadeh, 2018)
# This works by frequncy of visit by default. this can also work with spent time at a destination.
codeblock= """
def weight(x):
  x=float(x)
  o=float(-1* x/%i)
  value= 1/(1+ math.exp(o))
  return value """ %(maxw)
expression= "weight(!freq!)"
arcpy.CalculateField_management(poi, "w", expression,"PYTHON",codeblock)
# calculate weight for home using maxw
arcpy.DeleteField_management (home, ['w'])
arcpy.AddField_management(home, "w", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
x=float(maxw)
o=float(-1* x/maxw)
home_max_weight= 1/(1+ math.exp(o))
arcpy.CalculateField_management(home, "w", home_max_weight,"PYTHON")
## run main
i=1 # to controle creation of new fc

infc=roads
# make points along the travel routes
# the interval is 5 m by default. For faster processing (less deatails) the interval can be increased below
itvl=5
pointed_path='pointed_path'
pointmaker(infc,pointed_path,itvl,'POI_ID') 
#the following parts will calculate weights along the road using home, destination, and travel mode
#more detail on the formula used in the external reference (Hasanzadeh, 2018) 
w2=float(home_max_weight)
arcpy.JoinField_management (pointed_path, 'POI_ID', poi, 'OBJECTID', ['tmode','w','uid'])                                                                                                                                                                                                                                                                                                                                                                                 
arcpy.AddField_management(pointed_path, "w_road", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
cursor4 = arcpy.UpdateCursor(pointed_path)
for row in cursor4:
  if consider_mod==1:
    mod=row.tmode
  w1=row.w
  if consider_mod==0:
    rw=math.sqrt(w1*w2) 
  else:  
    if mod==mode1:
        speed_effect=speed1/5.0
        rw=math.sqrt(w1*w2)/speed_effect
    elif mod== mode2:
        speed_effect=speed2/5.0
        rw=(math.sqrt(w1*w2))/speed_effect
    else:
        speed_effect=speed3/5.0
        rw=(math.sqrt(w1*w2))/speed_effect
    if consider_mod==0:
        rw=math.sqrt(w1*w2)    
  row.setValue('w_road', rw)
  cursor4.updateRow(row)
del row, cursor4
arcpy.DeleteField_management(pointed_path,"w")  
arcpy.AddField_management(pointed_path, "w", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
arcpy.CalculateField_management (pointed_path, 'w', '!w_road!',"PYTHON_9.3")
# break path into points
## creating the exposure surface (raster)
print "raster making initiated"
# counting individuals for use in progressor 
result = arcpy.GetCount_management(home)
fc_count = int(result.getOutput(0))
arcpy.SetProgressor("step", "Step2: Creating AS rasters...",0, fc_count, 1)
arcpy.AddMessage( "started creating AS rasters") 
# iterate through individuals using uid
rows = arcpy.SearchCursor(home)
for row in rows:
    u=row.uid
    arcpy.SetProgressorLabel("Creating AS raster for user %u ..."%u)
    arcpy.AddMessage( "Creating IREM for user %u"%u) 
    progress=(float(u)/float(fc_count))*100.0
    arcpy.AddMessage( "%x percent completed"%progress)
    print u
    # make selections individual by individual using uid
    delimfield = arcpy.AddFieldDelimiters(home, 'uid')
    arcpy.Select_analysis(home, 'homsel', "{0} = {1}".format(delimfield, u))
    delimfield = arcpy.AddFieldDelimiters('poi', 'uid')
    arcpy.Select_analysis(poi, 'poisel', "{0} = {1}".format(delimfield, u))
    delimfield = arcpy.AddFieldDelimiters('pointed_path', 'uid')
    arcpy.Select_analysis('pointed_path', 'pathsel', "{0} = {1}".format(delimfield, u))
    count=arcpy.GetCount_management('pathsel')
    count=int(count.getOutput(0))
    delimfield = arcpy.AddFieldDelimiters('solid_nb', 'uid')
    arcpy.Select_analysis(solid_nb, 'boundsel', "{0} = {1}".format(delimfield, u))
    arcpy.PolygonToLine_management ('boundsel', 'lined_nb')
    arcpy.AddField_management ('lined_nb', 'uid', "SHORT", 10, 5, "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management ('lined_nb', 'uid', u)
    pointed_nb="pointed_nb%u"%u
    # convert home range boundary to points to enable IDW
    pointmaker('lined_nb',pointed_nb,30,'uid')
    arcpy.AddField_management (pointed_nb, 'w', "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management (pointed_nb, 'w', 0.05)
    # merge all features into one file and perform IDW
    # 'if count' checks if there are information available on individual's activity points and travel routes
    # if available: 
    if count > 0:
      arcpy.Merge_management (['homsel','poisel',pointed_nb], 'merge1' )
      if arcpy.management.GetCount('pathsel')[0] != "0":
        arcpy.Merge_management (['pathsel',pointed_nb], 'merge2' )
      arcpy.CheckOutExtension("spatial")
      idw1=Idw ('merge1', 'w', 5, 2, "", "")
      if arcpy.management.GetCount('pathsel')[0] != "0":
        idw2=Idw ('merge2', 'w', 5, 2, "", "")
      if arcpy.management.GetCount('pathsel')[0] != "0":
        summed = CellStatistics([idw1, idw2], "SUM", "DATA")
      else:
        summed=idw1

      arcpy.CheckInExtension("spatial")
      arcpy.CheckOutExtension("spatial")
      # generalize raster using block statitics if desired so
      if make_smooth==1:
        neighborhood = NbrCircle(rad, "MAP")
        summed=BlockStatistics (summed,neighborhood,'MEAN')
      # name raster files in the valid format to work with other related tools  
      new_name="nb_%u"%u
      # clip raster using home range boundary to match the defined extents
      clippedrast=directory
      arcpy.Clip_management (summed, "#",clippedrast, 'boundsel', "0", "ClippingGeometry", "MAINTAIN_EXTENT")  

      arcpy.Rename_management (clippedrast, new_name, "")
      arcpy.CheckInExtension("spatial")
    # 'if count' checks if there are information available on individual's activity points and travel routes
    # if not available:      
    else:
      if make_smooth==1:
          # generalize raster using block statitics if desired so
        neighborhood = NbrCircle(rad, "MAP")
        summed=BlockStatistics (summed,neighborhood,'MEAN')
      arcpy.Merge_management (['homsel','poisel',pointed_nb], 'merge1' )
      arcpy.CheckOutExtension("spatial")
      idw1=Idw ('merge1', 'w', 5, 2, "", "")
      # name raster files in the valid format to work with other related tools 
      new_name="nb_%u"%u
      clippedrast=directory
      # clip raster using home range boundary to match the defined extents
      arcpy.Clip_management (idw1, "#",clippedrast, 'boundsel', "0", "ClippingGeometry", "MAINTAIN_EXTENT")  
      arcpy.Rename_management (clippedrast, new_name, "")
      arcpy.CheckInExtension("spatial") 
    arcpy.SetProgressorPosition()      
del row, rows
t2 = time.time()
s = t2 - t1
print round(s/60, 2)
x=round(s/60, 2)
arcpy.AddMessage( "process took %x minutes"%x) 
arcpy.ResetProgressor()
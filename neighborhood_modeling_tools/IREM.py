# This tool creates an individualized residential exporsure model for individuals(IREM)
# Author: Kamyar Hasanzadeh
# Development started on 4.5.2016  _ Reassembled and integrated on 9.10.2017
# Bugs fixed 10.11.2017
# Changes: working with GUI
# Version 2.1.3
#bug fixed: if no poi or path, GUI improved
# YTK, Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
## ---------------------------
# Import modules
import arcpy
from arcpy import env
arcpy.Delete_management("in_memory")
t1 = time.time()
from arcpy import env
env.workspace = r"in_memory"
env.overwriteOutput=True
consider_paths= 'yes'
# input files
home= arcpy.GetParameterAsText(0)
poi=arcpy.GetParameterAsText(1)   #filtered
roads=arcpy.GetParameterAsText(2)
output=arcpy.GetParameterAsText(3)
directory=arcpy.GetParameterAsText(4) #raster output
#if consider_paths== 'yes':
hombufd= arcpy.GetParameter(5)
poibufd= arcpy.GetParameter(6)
maxw=arcpy.GetParameter(7)
#nod_freq=arcpy.GetParameter(10)
consider_mod= arcpy.GetParameter(8)
walking=arcpy.GetParameterAsText(9)
bike=arcpy.GetParameterAsText(10)
make_smooth=arcpy.GetParameter(11)
rad=arcpy.GetParameter(12)
have_boundaries=arcpy.GetParameter(13)
already_boundary=arcpy.GetParameterAsText(14)

# inputs
#maxw=30   # maximum weight which is assigned to home
if have_boundaries==0:
    buf_dist=10 # road buffer distance
    
    # creating boundary
    print "start creating boundary"
    result = arcpy.GetCount_management(home)
    fc_count = int(result.getOutput(0))
    arcpy.SetProgressor("step", "Step1: Creating boundaries...",0, fc_count, 1)
    arcpy.AddMessage( "start creating boundary") 
    poibufd= arcpy.GetParameter(7)
    hombufd= arcpy.GetParameter(8)
    arcpy.Buffer_analysis(home, 'bufhom', hombufd, "FULL", "ROUND", "NONE", "", "PLANAR")
    arcpy.Buffer_analysis(poi, 'bufpoi', poibufd, "FULL", "ROUND", "NONE", "", "PLANAR")
    if consider_paths== 'yes':
        arcpy.Buffer_analysis(roads, 'bufroad', buf_dist, "FULL", "ROUND", "NONE", "", "PLANAR")
    arcpy.CreateFeatureclass_management ('in_memory', 'tempnb', "POLYGON", 'bufhom', "DISABLED", "DISABLED", home, '#', '#', '#', '#')
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
    arcpy.CopyFeatures_management('tempnb',output)
    print "Boundaries are created"
    arcpy.ResetProgressor()
    arcpy.AddMessage("Boundaries are created")
# Given the neighborhood boundary, this tool creates a dynamic neighborhood represented as a raster
# Author: Kamyar Hasanzadeh
# Development started on 4.5.2016
# YTK, Aalto University, SoftGIS team
# contact: kamyar.hasanzadeh@gmail.com
## ---------------------------
# code part two: creating IREM
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
arcpy.Delete_management("in_memory")
t1 = time.time()
env.workspace = r"in_memory"
env.overwriteOutput=True

# inputs
# maxw=30   # maximum weight which is assigned to home
buf_dist=25 # road buffer distance
# secure original files by making a copy
if have_boundaries==0:
    solid_nb=output
else:
    solid_nb=already_boundary
# #################
## Convert lines to points
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
arcpy.DeleteField_management(poi,"w")
arcpy.AddField_management(poi, "w", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
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
routes= roads
infc=routes
pointed_path='pointed_path'
pointmaker(infc,pointed_path,5,'POI_ID')  
#arcpy.Integrate_management (pointed_path, 22) #simplify points (make thinner)
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
    if mod==walking:
        rw=math.sqrt(w1*w2)
    elif mod== bike:
        rw=(math.sqrt(w1*w2))/3.4
    else:
        rw=(math.sqrt(w1*w2))/10.0
    if consider_mod==0:
        rw=math.sqrt(w1*w2)    
  row.setValue('w_road', rw)
  cursor4.updateRow(row)
del row, cursor4
arcpy.DeleteField_management(pointed_path,"w")  
arcpy.AddField_management(pointed_path, "w", "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
arcpy.CalculateField_management (pointed_path, 'w', '!w_road!',"PYTHON_9.3")
#arcpy.CopyFeatures_management(pointed_path, "Z:/tmp/joined_temp.shp")
# break path into points
## here we create the surface of the neighborhood model (raster)
print "raster making initiated"
result = arcpy.GetCount_management(home)
fc_count = int(result.getOutput(0))
arcpy.SetProgressor("step", "Step2: Creating AS rasters...",0, fc_count, 1)
arcpy.AddMessage( "started creating AS rasters") 
rows = arcpy.SearchCursor(home)
for row in rows:
    u=row.uid
    arcpy.SetProgressorLabel("Creating AS raster for user %u ..."%u)
    arcpy.AddMessage( "Creating IREM for user %u"%u) 
    progress=(float(u)/float(fc_count))*100.0
    arcpy.AddMessage( "%x percent completed"%progress)
    
    #print "creating raster for:"
    print u
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
    pointmaker('lined_nb',pointed_nb,30,'uid')
    arcpy.AddField_management (pointed_nb, 'w', "DOUBLE", 10, 5, "", "", "NULLABLE", "REQUIRED")
    arcpy.CalculateField_management (pointed_nb, 'w', 0.05)
    if count > 0:
      arcpy.Merge_management (['homsel','poisel',pointed_nb], 'merge1' )
      if arcpy.management.GetCount('pathsel')[0] != "0":
        arcpy.Merge_management (['pathsel',pointed_nb], 'merge2' )
      arcpy.CheckOutExtension("spatial")
      idw1=Idw ('merge1', 'w', 5, 2, "", "")
      
      #idw1.save(c_idw1)
      if arcpy.management.GetCount('pathsel')[0] != "0":
        idw2=Idw ('merge2', 'w', 5, 2, "", "")
      #c_idw2="Y:/activeAge/Kamyar/activity_space/data/model_outputs/rasters/idw2"
      #idw2.save(c_idw2)
      if arcpy.management.GetCount('pathsel')[0] != "0":
        summed = CellStatistics([idw1, idw2], "SUM", "DATA")
      else:
        summed=idw1

      arcpy.CheckInExtension("spatial")
      #summed.save("Z:/tmp/workingF/rasters/summed")
      arcpy.CheckOutExtension("spatial")
      if make_smooth==1:
        neighborhood = NbrCircle(rad, "MAP")
        summed=BlockStatistics (summed,neighborhood,'MEAN')
      new_name="nb_%u"%u
      clippedrast=directory
      arcpy.Clip_management (summed, "#",clippedrast, 'boundsel', "0", "ClippingGeometry", "MAINTAIN_EXTENT")  
      #focaled=FocalStatistics (clippedrast, neighborhood)
      #focaled.save("Y:/activeAge/Kamyar/activity_space/data/model_outputs/rasters/clipped")
      arcpy.Rename_management (clippedrast, new_name, "")
      arcpy.CheckInExtension("spatial")
      #arcpy.Delete_management (summed)
    else:
      if make_smooth==1:
        neighborhood = NbrCircle(rad, "MAP")
        summed=BlockStatistics (summed,neighborhood,'MEAN')
      arcpy.Merge_management (['homsel','poisel',pointed_nb], 'merge1' )
      arcpy.CheckOutExtension("spatial")
      idw1=Idw ('merge1', 'w', 5, 2, "", "")
      #summed.save("Z:/tmp/workingF/rasters/summed")
      new_name="nb_%u"%u
      clippedrast=directory
      arcpy.Clip_management (idw1, "#",clippedrast, 'boundsel', "0", "ClippingGeometry", "MAINTAIN_EXTENT")  
      #focaled=FocalStatistics (clippedrast, NbrCircle(50, "MAP"), "MEAN", "")
      arcpy.Rename_management (clippedrast, new_name, "")
      #arcpy.Delete_management (summed)
      arcpy.CheckInExtension("spatial") 
    arcpy.SetProgressorPosition()      
del row, rows
t2 = time.time()
s = t2 - t1
print round(s/60, 2)
x=round(s/60, 2)
arcpy.AddMessage( "process took %x minutes"%x) 
arcpy.ResetProgressor()
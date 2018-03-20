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
    
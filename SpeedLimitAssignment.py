import arcpy
import os

# Define the input feature classes
streets_fc = "CTN_AFP"
crashes_fc = "Crashes"

# Create a temporary file geodatabase
temp_gdb = "C:/Temp/TempGDB.gdb"
if not arcpy.Exists(temp_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(temp_gdb), os.path.basename(temp_gdb))
print("Temporary file geodatabase created.")

# Define intermediate and output feature classes
buffered_streets_fc = os.path.join(temp_gdb, "Buffered_Streets")
intersections_fc = os.path.join(temp_gdb, "Intersections")
temp_output_fc = os.path.join(temp_gdb, "Temp_Crashes_with_Speed_Limit")

try:
    # Create a buffer around street segments
    buffer_distance = "10 Meters"  # Adjust this value as needed
    arcpy.analysis.Buffer(streets_fc, buffered_streets_fc, buffer_distance)
    print("Buffer created successfully.")
    
    # Check if the buffered_streets_fc exists
    if arcpy.Exists(buffered_streets_fc):
        print("Buffered streets feature class exists.")
    else:
        raise Exception("Buffered streets feature class does not exist.")
    
    # Perform a spatial join to assign speed limits to crash points
    arcpy.analysis.SpatialJoin(crashes_fc, buffered_streets_fc, temp_output_fc, 
                               "JOIN_ONE_TO_ONE", "KEEP_COMMON", 
                               match_option="WITHIN")
    print("Spatial join completed successfully.")

    # Identify intersection points
    arcpy.analysis.Intersect([streets_fc], intersections_fc, 
                             join_attributes="ALL", 
                             output_type="POINT")
    print("Intersections identified successfully.")

    # Add speed limit field to the original Crashes layer if not already added
    if not arcpy.ListFields(crashes_fc, "Assigned_Speed_Limit"):
        arcpy.management.AddField(crashes_fc, "Assigned_Speed_Limit", "SHORT")
    print("Assigned_Speed_Limit field added successfully.")

    # Create a spatial index for the intersections to speed up querying
    arcpy.management.AddSpatialIndex(intersections_fc)

    # Create an update cursor to iterate over crash points
    with arcpy.da.UpdateCursor(crashes_fc, ["OBJECTID", "SHAPE@", "Assigned_Speed_Limit"]) as cursor:
        for row in cursor:
            crash_id = row[0]
            point = row[1]
            
            # Check if the speed limit is already assigned
            with arcpy.da.SearchCursor(temp_output_fc, ["OBJECTID", "SPEED_LIMIT"], f"OBJECTID = {crash_id}") as temp_cursor:
                temp_row = temp_cursor.next()
                if temp_row and temp_row[1]:
                    row[2] = temp_row[1]
                    cursor.updateRow(row)
                    continue
            
            # Query intersecting streets for the current crash point
            intersecting_streets = []
            with arcpy.da.SearchCursor(intersections_fc, ["SHAPE@", "SPEED_LIMIT"], 
                                       spatial_reference=point.spatialReference) as intersect_cursor:
                for intersect_row in intersect_cursor:
                    if point.within(intersect_row[0]):
                        intersecting_streets.append(intersect_row[1])

            # Decide on the speed limit to assign (e.g., max speed limit)
            if intersecting_streets:
                assigned_speed_limit = max(intersecting_streets)
                row[2] = assigned_speed_limit
                cursor.updateRow(row)

    # Clean up intermediate files
    arcpy.management.Delete(buffered_streets_fc)
    arcpy.management.Delete(intersections_fc)
    arcpy.management.Delete(temp_output_fc)

    print("Speed limit assignment complete.")

except arcpy.ExecuteError as e:
    print(f"Error: {e}")
    arcpy.AddError(e)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    arcpy.AddError(e)

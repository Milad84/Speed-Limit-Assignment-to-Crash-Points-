import arcpy
import os

# Define the input feature classes
streets_fc = "CTN_AFP_Subset"
crashes_fc = "Crashes_Subset"

# Create a temporary file geodatabase
temp_gdb = "C:/Temp/TempGDB.gdb"
if not arcpy.Exists(temp_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(temp_gdb), os.path.basename(temp_gdb))
print("Temporary file geodatabase created.")

# Define the output feature class for intersections
intersections_fc = os.path.join(temp_gdb, "Intersections")

try:
    # Identify intersection points and save to the geodatabase
    arcpy.analysis.Intersect([streets_fc], intersections_fc, 
                             join_attributes="ALL", 
                             output_type="POINT")
    print("Intersections identified and created successfully.")

    # Step 1: Add speed limit field to the original Crashes layer if not already added
    if not arcpy.ListFields(crashes_fc, "Assigned_Speed_Limit"):
        arcpy.management.AddField(crashes_fc, "Assigned_Speed_Limit", "SHORT")
    print("Assigned_Speed_Limit field added successfully.")

    # Phase 1: Assign speed limits from the closest street
    with arcpy.da.UpdateCursor(crashes_fc, ["OBJECTID", "SHAPE@", "Assigned_Speed_Limit"]) as cursor:
        for row in cursor:
            crash_id = row[0]
            point = row[1]
            
            # Find the nearest street segment
            nearest_street = None
            nearest_distance = float('inf')
            with arcpy.da.SearchCursor(streets_fc, ["SHAPE@", "SPEED_LIMIT"]) as street_cursor:
                for street_row in street_cursor:
                    street_line = street_row[0]
                    speed_limit = street_row[1]
                    distance = point.distanceTo(street_line)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_street = speed_limit
            
            # Assign the speed limit from the nearest street
            if nearest_street is not None:
                row[2] = nearest_street
                cursor.updateRow(row)

    # Create a spatial index for the intersections to speed up querying
    arcpy.management.AddSpatialIndex(intersections_fc)

    # Phase 2: Handle intersections
    with arcpy.da.UpdateCursor(crashes_fc, ["OBJECTID", "SHAPE@", "Assigned_Speed_Limit"]) as cursor:
        for row in cursor:
            crash_id = row[0]
            point = row[1]
            assigned_speed_limit = row[2]
            
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

    print("Phase 2: Intersections handled successfully.")
    print("Speed limit assignment complete.")

except arcpy.ExecuteError as e:
    print(f"Error: {e}")
    arcpy.AddError(e)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    arcpy.AddError(e)

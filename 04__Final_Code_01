import arcpy
import os
import psycopg2

# Define the input feature classes
streets_fc = "CTN_AFP_Subset_2" #REMEMBER TO REPLACE TO YOUR PATH
crashes_fc = "Crashes_Subset_2" #REMEMBER TO REPLACE TO YOUR PATH
intersections_fc = "Intersections" #REMEMBER TO REPLACE TO YOUR PATH

# Define the project geodatabase
project_gdb = "G:/ATD/ACTIVE TRANS/Vision Zero/GIS/Speed Limit Implemetation/Speed Limit Implemetation.gdb" #REMEMBER TO REPLACE TO YOUR PATH
buffer_fc = os.path.join(project_gdb, "Customized_Buffers")
output_copy_fc = os.path.join(project_gdb, "Crashes_Subset_2_Copy")

# Create a temporary file geodatabase
temp_gdb = "C:/Temp/TempGDB.gdb"
if not arcpy.Exists(temp_gdb):
    arcpy.management.CreateFileGDB(os.path.dirname(temp_gdb), os.path.basename(temp_gdb))
print("Temporary file geodatabase created.")

# Define buffer size mapping based on street level combinations
buffer_size_mapping = {
    frozenset([1, 2]): "15 Feet",
    frozenset([1, 3]): "17.5 Feet",
    frozenset([1, 4]): "25 Feet",
    frozenset([1, 5]): "25 Feet",
    frozenset([2, 3]): "17.5 Feet",
    frozenset([2, 4]): "25 Feet",
    frozenset([2, 5]): "25 Feet",
    frozenset([3, 4]): "25 Feet",
    frozenset([3, 5]): "25 Feet",
    frozenset([4, 5]): "25 Feet",
    frozenset([1, 2, 3]): "17.5 Feet",
    frozenset([1, 2, 4]): "25 Feet",
    frozenset([1, 2, 5]): "25 Feet",
    frozenset([1, 3, 4]): "25 Feet",
    frozenset([1, 3, 5]): "25 Feet",
    frozenset([1, 4, 5]): "25 Feet",
    frozenset([2, 3, 4]): "25 Feet",
    frozenset([2, 3, 5]): "25 Feet",
    frozenset([2, 4, 5]): "25 Feet",
    frozenset([3, 4, 5]): "25 Feet",
    frozenset([1, 2, 3, 4]): "25 Feet",
    frozenset([1, 2, 3, 5]): "25 Feet",
    frozenset([1, 2, 4, 5]): "25 Feet",
    frozenset([1, 3, 4, 5]): "25 Feet",
    frozenset([2, 3, 4, 5]): "25 Feet",
    frozenset([1, 2, 3, 4, 5]): "25 Feet",
}

default_buffer_size = "15 Feet"

try:
    # Function to get buffer size based on street levels
    def get_buffer_size(street_levels):
        street_levels_set = frozenset(street_levels)
        return buffer_size_mapping.get(street_levels_set, default_buffer_size)

    # Remove existing feature class if it exists in the project geodatabase
    if arcpy.Exists(buffer_fc):
        arcpy.management.Delete(buffer_fc)
        print(f"Deleted existing {buffer_fc}")

    # Add field to flag crashes near intersections
    if "Near_Intersection" not in [f.name for f in arcpy.ListFields(crashes_fc)]:
        arcpy.management.AddField(crashes_fc, "Near_Intersection", "SHORT")
        print("Near_Intersection field added successfully.")

    # Identify intersection points with street levels
    intersection_points = os.path.join(temp_gdb, "Intersection_Points")
    if arcpy.Exists(intersection_points):
        arcpy.management.Delete(intersection_points)
        print(f"Deleted existing {intersection_points}")

    arcpy.analysis.Intersect([streets_fc], intersection_points, output_type="POINT")

    # Add street level information to intersections
    arcpy.management.AddField(intersection_points, "Street_Levels", "TEXT")
    with arcpy.da.UpdateCursor(intersection_points, ["Street_Levels", "SHAPE@"]) as cursor:
        for row in cursor:
            intersecting_levels = set()
            with arcpy.da.SearchCursor(streets_fc, ["STREET_LEVEL", "SHAPE@"]) as street_cursor:
                for street_row in street_cursor:
                    if street_row[1].crosses(row[1]) and street_row[0] in [1, 2, 3, 4, 5]:
                        intersecting_levels.add(street_row[0])
            if intersecting_levels:
                row[0] = ",".join(map(str, intersecting_levels))
                cursor.updateRow(row)
            else:
                row[0] = "Default"
                cursor.updateRow(row)

    # Create buffers around intersection points with initial default size
    arcpy.management.CreateFeatureclass(project_gdb, "Customized_Buffers", "POLYGON", spatial_reference=intersections_fc)
    arcpy.management.AddField(buffer_fc, "Buffer_Size", "TEXT")
    arcpy.management.AddField(buffer_fc, "Street_Levels", "TEXT")

    buffer_creation_count = 0

    with arcpy.da.InsertCursor(buffer_fc, ["SHAPE@", "Buffer_Size", "Street_Levels"]) as buffer_cursor:
        with arcpy.da.SearchCursor(intersection_points, ["SHAPE@", "Street_Levels"]) as cursor:
            for row in cursor:
                street_levels_str = row[1].split(",")
                if all(level_str.isdigit() for level_str in street_levels_str) and street_levels_str != ['']:
                    street_levels = list(map(int, street_levels_str))
                    buffer_size = get_buffer_size(street_levels)
                    buffer_geometry = row[0].buffer(float(buffer_size.split()[0]))
                    buffer_cursor.insertRow([buffer_geometry, buffer_size, row[1]])
                    buffer_creation_count += 1
                else:
                    buffer_size = default_buffer_size
                    buffer_geometry = row[0].buffer(float(buffer_size.split()[0]))
                    buffer_cursor.insertRow([buffer_geometry, buffer_size, row[1]])
                    buffer_creation_count += 1

    print(f"Buffers around intersections created successfully: {buffer_creation_count} buffers created.")

    # Recalculate buffer sizes based on street levels crossing the initial buffers
    buffer_update_count = 0

    with arcpy.da.UpdateCursor(buffer_fc, ["SHAPE@", "Buffer_Size", "Street_Levels"]) as buffer_cursor:
        for row in buffer_cursor:
            intersecting_levels = set()
            with arcpy.da.SearchCursor(streets_fc, ["STREET_LEVEL", "SHAPE@"]) as street_cursor:
                for street_row in street_cursor:
                    if street_row[1].crosses(row[0]) and street_row[0] in [1, 2, 3, 4, 5]:
                        intersecting_levels.add(street_row[0])
            if intersecting_levels:
                buffer_size = get_buffer_size(list(intersecting_levels))
                buffer_geometry = row[0].buffer(float(buffer_size.split()[0]) - float(row[1].split()[0]))
                row[0] = buffer_geometry
                row[1] = buffer_size
                row[2] = ",".join(map(str, intersecting_levels))
                buffer_cursor.updateRow(row)
                buffer_update_count += 1

    print(f"Buffers around intersections updated successfully: {buffer_update_count} buffers updated.")

    # Create a copy of the crashes feature class
    if arcpy.Exists(output_copy_fc):
        arcpy.management.Delete(output_copy_fc)
        print(f"Deleted existing {output_copy_fc}")

    arcpy.management.Copy(crashes_fc, output_copy_fc)
    print(f"Copied crashes to {output_copy_fc}")

    # Add Assigned_Speed_Limit field if not exists
    if "Assigned_Speed_Limit" not in [f.name for f in arcpy.ListFields(output_copy_fc)]:
        arcpy.management.AddField(output_copy_fc, "Assigned_Speed_Limit", "SHORT")
        print("Assigned_Speed_Limit field added successfully.")
    else:
        print("Assigned_Speed_Limit field already exists.")

    # Add a field for the speed limit from the database if not exists
    if "DB_Speed_Limit" not in [f.name for f in arcpy.ListFields(output_copy_fc)]:
        arcpy.management.AddField(output_copy_fc, "DB_Speed_Limit", "SHORT")
        print("DB_Speed_Limit field added successfully.")
    else:
        print("DB_Speed_Limit field already exists.")

    # Load buffer shapes
    buffer_shapes = [row[0] for row in arcpy.da.SearchCursor(buffer_fc, ["SHAPE@"])]

    crash_count = int(arcpy.management.GetCount(output_copy_fc)[0])
    processed_count = 0

    with arcpy.da.UpdateCursor(output_copy_fc, ["OBJECTID", "SHAPE@", "Assigned_Speed_Limit", "Near_Intersection", "Crash_Id", "DB_Speed_Limit"]) as cursor:
        for row in cursor:
            crash_id = row[0]
            point = row[1]

            # Check if crash point is within any buffer
            is_within_buffer = any(buffer_shape.contains(point) for buffer_shape in buffer_shapes)
            row[3] = 1 if is_within_buffer else None

            if row[3] == 1:
                # Get the highest speed limit from intersecting street segments within the buffer
                intersecting_speeds = [
                    street_row[1]
                    for buffer_shape in buffer_shapes
                    if buffer_shape.contains(point)
                    for street_row in arcpy.da.SearchCursor(streets_fc, ["SHAPE@", "SPEED_LIMIT"])
                    if street_row[0].crosses(buffer_shape)
                ]
                intersecting_speeds = [speed for speed in intersecting_speeds if speed is not None]
                if intersecting_speeds:
                    row[2] = max(intersecting_speeds)
            else:
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

            # Log progress
            processed_count += 1
            if processed_count % 100 == 0:
                print(f"Processed {processed_count}/{crash_count} crashes.")

    print("Speed limit assignment complete.")
    print("Final assignment of crashes near intersections completed.")

    # Connect to the PostgreSQL database and retrieve speed limits
    conn = psycopg2.connect(
        dbname="YOUR_DATABASE",
        user="YOUR_USERNAME",
        password="YOUR_PASSWORD",
        host="YOUR_HOST"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT crash_id, crash_speed_limit FROM public.atd_txdot_crashes")
    db_speed_limits = cursor.fetchall()

    # Create a dictionary from the database results
    speed_limit_dict = {row[0]: row[1] for row in db_speed_limits}

    # Update the crash points with the speed limit from the database
    with arcpy.da.UpdateCursor(output_copy_fc, ["Crash_Id", "DB_Speed_Limit"]) as cursor:
        for row in cursor:
            crash_id = row[0]
            if crash_id in speed_limit_dict:
                row[1] = speed_limit_dict[crash_id]
                cursor.updateRow(row)

    print("Database speed limit assignment complete.")

except arcpy.ExecuteError as e:
    print(f"Error: {e}")
    arcpy.AddError(e)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    arcpy.AddError(e)
finally:
    # Ensure the buffer feature class exists
    if arcpy.Exists(buffer_fc):
        print("Buffers around intersections retained successfully.")
    else:
        print("Buffers around intersections do not exist.")

    if conn:
        conn.close()

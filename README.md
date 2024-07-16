![image](https://github.com/user-attachments/assets/3af249c9-fc94-458b-abe4-fb2d6b210eb3)
Sample of output showing intersection buffer and crash points categorized based on different speed limits. Crashes along the street segments get the speed limit from the street feature. Crashes at the intersection inherit the highest speed from intersecting street segments with the intersection buffer.

# Speed Limit Assignment to Crash Points

This repository contains a script that assigns speed limit data from street segments to crash points. The script uses ArcPy to perform spatial analysis within ArcGIS Pro, ensuring accurate speed limit assignments, even at intersections where multiple streets may intersect.

## Features

- **Input:** Street segment feature class (`CTN_AFP_Subset_2`) and crash points feature class (`Crashes_Subset_2`).
- **Output:** Crash points feature class with added fields for assigned speed limits.
- **Temporary Storage:** Uses a temporary file geodatabase to store intermediate results.

## Approach

### Buffer Creation

- Creates buffers around intersection points with an initial default size of 15 feet.
- Buffer sizes are adjusted based on street level combinations at intersections.

### Street Level Intersection

- Identifies intersection points and determines the street levels of intersecting streets.
- Creates and updates buffers around these intersection points based on the intersecting street levels.

### Speed Limit Assignment

- For crashes near intersections, the highest speed limit from the intersecting street segments within the buffer is assigned to the crash point.
- For crashes not near intersections, the speed limit from the nearest street segment is assigned.

### Database Speed Limit Assignment

- Connects to an AWS PostgreSQL database to retrieve additional speed limits for crash points.
- Updates the crash points with the speed limit from the database.

## Requirements

- ArcGIS Pro
- ArcPy
- psycopg2 (for PostgreSQL connection)

## Usage Instructions

1. **Update the Input Paths:**
   - Modify the `streets_fc` variable to point to your street layer (`CTN_AFP_Subset_2`).
   - Modify the `crashes_fc` variable to point to your crash points layer (`Crashes_Subset_2`).

2. **Run the Script:** Execute the script in an ArcGIS Pro environment.

3. **Check Output:** The `Assigned_Speed_Limit` and `DB_Speed_Limit` fields in the `Crashes_Subset_2_Copy` layer will be updated with the appropriate speed limits.

4. ![image](https://github.com/user-attachments/assets/9bb0f39f-9646-4b6d-8de1-d1ff2ff0a46c)
   Sample of output table in ArcPro where three new fields bring the results of the code.


## Script Details

### Buffer Creation and Street Level Intersection

The script begins by creating buffers around intersection points and determining the street levels of the intersecting streets. These buffers are adjusted based on the street levels.

```python
# Define buffer size mapping based on street level combinations
buffer_size_mapping = {
    frozenset([1, 2]): "15 Feet",
    frozenset([1, 3]): "17.5 Feet",
    frozenset([1, 4]): "25 Feet",
    # Other combinations...
    frozenset([1, 2, 3, 4, 5]): "25 Feet",
}

default_buffer_size = "15 Feet"

# Function to get buffer size based on street levels
def get_buffer_size(street_levels):
    street_levels_set = frozenset(street_levels)
    return buffer_size_mapping.get(street_levels_set, default_buffer_size)
```
## Speed Limit Assignment from Street Segments
The script assigns speed limits to crash points based on their proximity to street segments. The highest speed limit from the intersecting streets within the buffer is used for crashes near intersections. For crashes not near intersections, the nearest street segment's speed limit is assigned.

with arcpy.da.UpdateCursor(output_copy_fc, ["OBJECTID", "SHAPE@", "Assigned_Speed_Limit", "Near_Intersection", "Crash_Id", "DB_Speed_Limit"]) as cursor:
    for row in cursor:
        crash_id = row[4]
        point = row[1]
```python
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

```

## Database Speed Limit Assignment
The script connects to an AWS PostgreSQL database to retrieve additional speed limits for crash points and updates the crash points with the speed limit from the database

``` python
# Connect to the PostgreSQL database and retrieve speed limits
conn = psycopg2.connect(
    dbname="atd_vz_data",
    user="kordem",
    password="cEEFMT46vWoEiZ6kcuvX",
    host="db-rr.vision-zero.austinmobility.io"
)
cursor = conn.cursor()
cursor.execute("SELECT crash_id, crash_speed_limit FROM public.atd_txdot_crashes")
db_speed_limits = cursor.fetchall()

# Create a dictionary from the database results
speed_limit_dict = {str(row[0]): row[1] for row in db_speed_limits}

# Debug print to verify dictionary content
print(f"Speed limit dictionary: {speed_limit_dict}")

# Update the crash points with the speed limit from the database
with arcpy.da.UpdateCursor(output_copy_fc, ["Crash_Id", "DB_Speed_Limit"]) as cursor:
    for row in cursor:
        crash_id = str(row[0])  # Ensure crash_id is a string for dictionary lookup
        if crash_id in speed_limit_dict:
            row[1] = speed_limit_dict[crash_id]
            cursor.updateRow(row)

print("Database speed limit assignment complete.")
```

# Speed Limit Assignment to Crash Points

This repository contains a series of scripts that assign speed limit data from street segments to crash points. The scripts use ArcPy to perform spatial analysis within ArcGIS Pro, ensuring accurate speed limit assignments, even at intersections where multiple streets may intersect.

# Final Code
Although the Final Code is the last version of tested software, previous versions (starting with numbers) record all the steps to get to where I am now with the final code. All the earlier attempts are kept for my record. 

## Features

- **Input:** Street segment feature class (`CTN_AFP_Subset_2`) and crash points feature class (`Crashes_Subset_2`).
- **Output:** Crash points feature class with added fields for assigned speed limits (`Assigned_Speed_Limit`) and database speed limits (`DB_Speed_Limit`).
- **Intersection Handling:** Uses customized buffer sizes based on street levels at intersections to ensure accurate speed limit assignments.
- **Temporary Storage:** Uses a temporary file geodatabase to store intermediate results.
- **Database Integration:** Fetches additional speed limit data from an AWS-hosted PostgreSQL database and integrates it with the crash data.

## Approach

The process of assigning speed limits to crash points involves several steps:

1. **Buffer Creation Around Intersections:**
    - Intersection points are identified by intersecting street segments.
    - Initial buffers with a default radius of 15 feet are created around these intersection points.
    - Buffer sizes are then adjusted based on the street levels of the intersecting streets. For instance, different combinations of street levels result in different buffer sizes as defined in the `buffer_size_mapping`.

2. **Flagging Crashes Near Intersections:**
    - Crash points are checked to see if they fall within any of the customized buffers.
    - The `Near_Intersection` field is updated to `1` for crash points within the buffers and `NULL` for those outside.

3. **Speed Limit Assignment:**
    - For crash points near intersections (i.e., those within the buffers), the highest speed limit from all intersecting street segments is assigned to ensure safety considerations.
    - For crash points not near intersections, the speed limit is determined based on the closest street segment using the nearest neighbor search.

4. **Integration with Database:**
    - Connects to a PostgreSQL database hosted on AWS to fetch additional speed limit data (`crash_speed_limit`).
    - Updates the crash points with this additional speed limit data using the `Crash_Id` field for joining the local crash data with the database records.

5. **Cleanup:**
    - Intermediate files and layers are deleted to manage disk space and maintain a clean working environment.

## Usage Instructions

1. **Update the Input Paths:**
    - Modify the `streets_fc` variable to point to your street layer.
    - Modify the `crashes_fc` variable to point to your crash points layer.
    - Modify the `project_gdb` variable to point to your project geodatabase.

2. **Run the Script:** Execute the script in an ArcGIS Pro environment.

3. **Check Output:**
    - The `Assigned_Speed_Limit` and `DB_Speed_Limit` fields in the `Crashes` layer will be updated with the appropriate speed limits.
    - The buffers around intersections will be stored in the `Customized_Buffers` feature class in your project geodatabase.

##

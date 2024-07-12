# Speed Limit Assignment to Crash Points

This repository contains a script that assigns speed limit data from street segments to crash points. The script uses ArcPy to perform spatial analysis within ArcGIS Pro, ensuring accurate speed limit assignments, even at intersections where multiple streets may intersect. Additionally, the script retrieves and compares speed limit data from a PostgreSQL database hosted on AWS.

## Features

- **Input:**
  - Street segment feature class (`CTN_AFP_Subset_2`)
  - Crash points feature class (`Crashes_Subset_2`)
  - Intersection points feature class (`Intersections`)
- **Output:**
  - Crash points feature class with added fields for assigned speed limits from street segments and AWS database.
- **Temporary Storage:** Uses a temporary file geodatabase to store intermediate results.

## Approach

1. **Buffer Creation:**
   - Creates buffers around intersection points with initial default size.
   - Adjusts buffer sizes based on the street levels of intersecting streets.

2. **Field Addition:**
   - Adds a field `Near_Intersection` to flag crashes near intersections.
   - Adds fields `Assigned_Speed_Limit` and `DB_Speed_Limit` to store speed limits from street segments and AWS database.

3. **Speed Limit Assignment:**
   - Assigns speed limits from the nearest street segment to each crash point.
   - If a crash is near an intersection, assigns the highest speed limit from the intersecting streets.
   - Retrieves speed limit data from the AWS PostgreSQL database and updates the crash points with this data.

4. **Cleanup:**
   - Deletes intermediate files to free up space.
   - Ensures buffers around intersections are retained in the project geodatabase.

## Requirements

- ArcGIS Pro
- ArcPy
- psycopg2 (for PostgreSQL database connection)

## Installation

1. Ensure you have ArcGIS Pro installed.
2. Clone this repository to your local machine.
3. Install the `psycopg2` package:
   ```bash
   pip install psycopg2

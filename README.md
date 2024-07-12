# Speed Limit Assignment to Crash Points

This repository contains a script that assigns speed limit data from street segments to crash points. The script uses ArcPy to perform spatial analysis within ArcGIS Pro, ensuring accurate speed limit assignments, even at intersections where multiple streets may intersect.

## Features

- **Input:** Street segment feature class (`CTN_AFP_Subset_2`) and crash points feature class (`Crashes_Subset_2`).
- **Output:** Crash points feature class with an added field for assigned speed limits.
- **Temporary Storage:** Uses a temporary file geodatabase to store intermediate results.

## Methodology

The project follows these steps to achieve the desired speed limit assignment:

### Step 1: Create Buffers Around Intersection Points

1. **Identify intersection points** from the street segments.
2. **Determine the street levels** of the intersecting streets at each intersection point.
3. **Create buffers** around the intersection points with sizes determined by the combination of street levels.

### Step 2: Assign Near_Intersection Field

1. **Check if each crash point** falls within any buffer.
2. **Update the Near_Intersection field** to 1 if the crash is within a buffer, otherwise set it to NULL.

### Step 3: Assign Speed Limits

1. **Assign the highest speed limit** from intersecting streets if the crash is near an intersection.
2. **Assign the speed limit from the nearest street segment** if the crash is not near an intersection.

## Approach

The approach involves creating a buffer around each intersection point to determine if a crash is near an intersection. The size of the buffer is determined based on the combination of street levels at the intersection. 

- **Intersection Buffering:** Buffers are created around intersection points, with sizes based on street level combinations (e.g., a combination of street levels 1 and 2 might get a 30-foot buffer, while a combination involving street level 4 might get a 50-foot buffer).
- **Near_Intersection Field:** Each crash point is checked to see if it falls within any of the intersection buffers. If it does, the `Near_Intersection` field is set to 1; otherwise, it is set to NULL.
- **Speed Limit Assignment:** For crashes near intersections (those with `Near_Intersection` set to 1), the highest speed limit from the intersecting streets is assigned. For other crashes, the speed limit from the nearest street segment is assigned.

## Usage Instructions

1. **Update the Input Paths:**
   - Modify the `streets_fc` variable to point to your street layer.
   - Modify the `crashes_fc` variable to point to your crash points layer.

2. **Run the Script:** Execute the script in an ArcGIS Pro environment.

3. **Check Output:** The `Assigned_Speed_Limit` field in the `Crashes` layer will be updated with the appropriate speed limits.

## Requirements

- ArcGIS Pro
- ArcPy

## Installation

1. Ensure you have ArcGIS Pro installed.
2. Clone this repository to your local machine.
3. Open the script in ArcGIS Pro and update the input paths as needed.

## Contributions

Contributions are welcome! Please fork this repository and submit pull requests.

## License

This project is licensed under the MIT License.

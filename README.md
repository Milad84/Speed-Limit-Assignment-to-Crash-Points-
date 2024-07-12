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

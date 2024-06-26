# Speed Limit Assignment to Crash Points

This repository contains a script that assigns speed limit data from street segments to crash points. The script uses ArcPy to perform spatial analysis within ArcGIS Pro, ensuring accurate speed limit assignments, even at intersections where multiple streets may intersect.

## Features

- **Input:** Street segment feature class (`CTN_AFP`) and crash points feature class (`Crashes`).
- **Output:** Crash points feature class with an added field for assigned speed limits.
- **Temporary Storage:** Uses a temporary file geodatabase to store intermediate results.

## Script Details

- **Buffer Creation:** Creates a buffer around each crash point and iteratively increases the buffer size until a street segment is intersected.
- **Spatial Join:** Performs a spatial join to assign speed limits from intersecting street segments to crash points.
- **Field Addition:** Adds a new field `Assigned_Speed_Limit` to the `Crashes` layer.
- **Speed Limit Assignment:** Assigns the maximum speed limit from intersecting streets to the crash points.
- **Cleanup:** Deletes intermediate files to free up space.

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

## Contact

If you have any questions or need further assistance, feel free to open an issue or contact us.


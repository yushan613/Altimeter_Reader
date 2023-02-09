Folder: footprint_computer

In this folder, footprints of images are computed.

footprint_computer/all_pts: contains the SHAPE file of all the photo centers, from which information like photo center coordinates, ground elevation, and flight direction, looking angle can be extracted exported as csv files. 

footprint_computer/1815_shp: As an example, photos centers on flight line 1815 was exported as a SHAPE file. Then from this SHAPE file, attributes (information) like coordinates, ground elevation, flight direction can be exported as a CSV file.

1815_coord_ele.csv: Exported CSV file. Then add the reading results given by the altimeter_reader to the CSV file, by subtracting ground elevation we get the camera height above the ground.

camera_calculator.py: compute the footprints based on information in the CSV file. The computed coordinates of the footprints will be stored in footprint.geojson, which can further be visualized in QGIS.



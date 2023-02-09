# Altimeter_Reader
This repository contains the Python source code used in additional thesis "Information extraction and geolocalization of historical aerial imagery" by Yushan Liu.
This altimeter reader can automatically read the altitudes from the altimeters in historical aerial images(photographs). 


The steps to run the altimeter reader are as follows:

1. Train the altimeter detector

    1.1 Go to folder: altimeter_detector

    1.1 Create training and testing dataset with imglab

    1.2 Run train_object_detector.py to obtain the trained detector: detector.svm

2. Read the altimeters

    2.1 Put all the TIFF images of the aerial photos in folder: readHeight/tif_images (preferably, the images should be from the same flight line.)

    2.2 Exacute the program by running readHeight.py
        Before running the program, you'll need to give the path to the directory where there are TIFF images(photos) from a flightline are in.
        For example, if the TIFF images(photos) from a flightline are in directory "readHeight/tif_images", then execute the program by running: 
        "python readHeight.py .\tif_images" in commond line.
        
    2.3 The reading results will be stored in readings.txt
 
        
3. Compute footprints

    3.1 In QGIS, export the attributes of the needed photocenters as CSV files from the SHP file: TMA_pts_20100927.shp
    
    3.2 Find the flying direction(in degrees) from the exported CSV file

    3.3 Run camera_calculator.py and the computed footprints are stored in geojson file: footprints.geojson. You can then visualize the footprints in QGIS




readHeight/jpg_images contains the images converted from TIFF format to JPEG format. 

readHeight/templates contains templates of number 3, 5, and 8 that are used in template matching.

readHeight/cut_clocks contains the altimeters images cropped from the photos.

readHeight/img_twoHands contains the cropped altimeter images with lines drawn on it, which represent the two pointers(hands) on the altimeters

The readings will be written in txt file: readings.txt

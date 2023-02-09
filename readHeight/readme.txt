Folder: readHeight contains the python files that can automatically read altimeters.
Below are some information of the folders and files in readHeight

readHeight/jpg_images contains the images converted from TIFF format to JPEG format. 

readHeight/templates contains templates of number 3, 5, and 8 that are used in template matching.

readHeight/cut_clocks contains the altimeters images cropped from the photos.

readHeight/img_twoHands contains the cropped altimeter images with lines drawn on it, which represent the two pointers(hands) on the altimeters

The readings will be written in txt file: readings.txt


Required Packages:
dlib (19.24 or higher version): for dlib to work, you need to have CMake and a working C++ compiler installed.
opencv-python
spymicmac: contrast_enhance function is used for image enhancement
matplotlib: for some visualization
Pillow: for some visualization

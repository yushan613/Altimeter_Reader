import cv2
import numpy as np
import dlib
import os
import glob
import warnings
import sys
import dlib
from spymicmac.image import contrast_enhance
from PIL import Image
from matplotlib import pyplot as plt
from findCircle import *
from CircularMask_ImageInhance import *
from lineDetection import *
from selectLines import *
from mergeLines import *
from lines2readings import *


""" 
This Python file shows all the steps of the altimeter reader.

"""


#### First get the folder with tif images
if len(sys.argv) != 2:
    print(
        "Give the path to the examples/tif_images directory as the argument to this "
        "program. For example, if you are in the readHeight folder then "
        "execute this program by running:\n"
        "python readHeight.py ./tif_images")
    exit()
tif_folder = sys.argv[1]
tif_path = os.path.abspath(tif_folder)

#### Convert the tif images to jpeg
# create a new folder to store all the converted jpg files
jpg_path = os.path.dirname(tif_path) + '/jpg_images/'
if not os.path.exists(jpg_path):
    os.makedirs(jpg_path)
# converting
for infile in os.listdir(tif_path):
    print("converting from tif to jpeg : " + infile)
    read = cv2.imread(tif_folder + '/' + infile)
    outfile = infile.split('.')[0] + '.jpg'
    cv2.imwrite(jpg_path + outfile, read, [cv2.IMWRITE_JPEG_QUALITY, 200])

#### Use the detector on the images to detect the bounding box for the altimeter
detector = dlib.simple_object_detector("detector.svm")
cut_path = os.path.dirname(tif_path) + '/cut_clocks/'
if not os.path.exists(cut_path):
    os.makedirs(cut_path)
# now run the detector over the images in the jpg_path and save the results.
f_height = open('readings.txt', 'a')
for f in glob.glob(os.path.join(jpg_path, "*.jpg")):
    print("Processing file: {}".format(f))
    img = dlib.load_rgb_image(f)
    dets = detector(img)
    print("Number of clocks detected: {}".format(len(dets)))
    if len(dets) == 1:
        for k, d in enumerate(dets):
            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                k, d.left(), d.top(), d.right(), d.bottom()))
            # crop the images to get the height clock
            if d.left() < 50:
                img_cropped = img[d.top()-50:d.bottom()+50, 0:d.right()+50]
            else:
                img_cropped = img[d.top()-50:d.bottom()+50, d.left()-50:d.right()+50]
        cv2.imwrite(os.path.dirname(tif_path) + '/cut_clocks/' + os.path.basename(f), img_cropped)
    else:
        warnings.warn('not 1 altimeter detected.')
        img_cropped = None
        readings = -9991
        line = [os.path.basename(f), '      ', str(readings)]
        f_height.writelines(line)
        f_height.write('\n')

#### Iterate through the cutted image folder
template3 = cv2.imread('./templates/3.jpg', 0)
template5 = cv2.imread('./templates/5.jpg', 0)
template8 = cv2.imread('./templates/8.jpg', 0)

for infile in os.listdir(cut_path):
    print("template matching : " + infile)
    cut_img = cv2.imread(cut_path + '/' + infile, 0)
    rows, cols = cut_img.shape
    ### Locate the circle by template matching ###
    img_enh = IMGEnhance(cut_img)
    img_bw = IMGBinary(img_enh)
    # cv2.imshow('binary', img_bw)
    # cv2.waitKey(0)
    circle1 = getCircle(cut_img, img_bw, template3, template5, template8)
    if circle1 is None:
        print('cannot locate altimeter in image:' + infile)
        img_reading = -9990
    else:
        ### Image enhancement again on the central area only ###
        img_enh_central = CentralEnhance(cut_img, circle1)
        ### Thresholding ###
        th = 230
        max_val = 255
        ret, o1 = cv2.threshold(img_enh_central, th, max_val, cv2.THRESH_BINARY)
        ### Line Detection (HoughLinesP) ###
        linesP = lineDetection(o1, cut_img)
        ### Select the lines that are likely to be edges of short/long hands ###
        selected_lines = np.array(SelectLines(circle1, linesP, cut_img, o1))
        selected_lines = selected_lines.reshape((len(selected_lines), 1, 4))
        ### Merge the lines that are very close
        merged_lines, img_merged = mergeLines(selected_lines, cut_img, circle1)
        ### Get the reading from the image and show the two hands
        img_reading, height = lines2readings(merged_lines, cut_img, circle1, o1)

        print('height reading is:', height)
        cv2.imwrite('./img_twoHands/' + infile, img_reading)
    line = [infile, '      ', str(height)]
    f_height.writelines(line)
    f_height.write('\n')
f_height.close()



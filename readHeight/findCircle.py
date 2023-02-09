import cv2
import numpy as np
from spymicmac.image import contrast_enhance
from PIL import Image
from matplotlib import pyplot as plt
import os
import warnings

def IMGEnhance(img):
    # some image enhancement techniques
    # 1. Histogram equalization
    eqHist = cv2.equalizeHist(img)
    # 2. Unmasked sharpening
    img_GaussianBlur = cv2.GaussianBlur(eqHist, (0, 0), 3)
    usm = cv2.addWeighted(eqHist, 2.0, img_GaussianBlur, -1.0, 0)
    # 3. Denoising & Contrast enhancement
    # since this function only takes file path as input
    # we need to save usm to a path and then remove it
    cv2.imwrite('temp_IMGEnhance.jpg', usm)
    img_enh = contrast_enhance('temp_IMGEnhance.jpg')
    # cv2.imwrite('./findC/img_enhanced.jpg', img_enh)
    os.remove('temp_IMGEnhance.jpg')
    return img_enh

def IMGBinary(img):
    # ruturning binary image with the numbers black
    # thresholding
    th = 210
    max_val = 255
    ret, o1 = cv2.threshold(img, th, max_val, cv2.THRESH_BINARY)
    # Erosion & Dilation
    kernel1 = np.ones((3, 3), np.uint8)
    img_erosion = cv2.erode(o1, kernel1, iterations=2)
    img_dilation = cv2.dilate(img_erosion, kernel1, iterations=2)
    # white black color exchange()
    img_wbexchange = 255 - img_dilation
    return img_wbexchange

def getCircle(img_gray, img_binary, img_template_3, img_template_5, img_template_8):
    # img_gray: the original gray scale image
    # img_binary: binary image of the clock with numbers and hands in black
    # img_template_3~8: template images to match for

    # width and height of the 3 templates
    w3, h3 = img_template_3.shape[::-1]
    w5, h5 = img_template_5.shape[::-1]
    w8, h8 = img_template_8.shape[::-1]

    img_copy = img_gray.copy()
    # matching for 3
    res3 = cv2.matchTemplate(img_binary, img_template_3, cv2.TM_CCOEFF)
    min_val3, max_val3, min_loc3, max_loc3 = cv2.minMaxLoc(res3)
    # matching for 5
    res5 = cv2.matchTemplate(img_binary, img_template_5, cv2.TM_CCOEFF)
    min_val5, max_val5, min_loc5, max_loc5 = cv2.minMaxLoc(res5)
    # matching for 8
    res8 = cv2.matchTemplate(img_binary, img_template_8, cv2.TM_CCOEFF)
    min_val8, max_val8, min_loc8, max_loc8 = cv2.minMaxLoc(res8)

    r = 168 + 25 + 74
    # print('3,5,8:', max_val3, max_val5, max_val8)
    if max_val3 > 30000000 and max_val3 > max_val5 and max_val3 > max_val8:
        # print('max_val3:',max_val3)
        top_left3 = max_loc3
        bottom_right3 = (top_left3[0] + w3, top_left3[1] + h3)
        mid_p = ( int((top_left3[0]+bottom_right3[0])/2), int((top_left3[1]+bottom_right3[1])/2) )
        circle = (int(mid_p[0]-np.cos(18*np.pi/180)*205), int(mid_p[1]-np.sin(18*np.pi/180)*205), r)
    elif max_val5 > 30000000 and max_val5 > max_val3 and max_val5 > max_val8:
        # print('max_val5:', max_val5)
        top_left5 = max_loc5
        bottom_right5 = (top_left5[0] + w5, top_left5[1] + h5)
        circle = (int((top_left5[0] + bottom_right5[0])/2)-7,  top_left5[1]-169, r)
    elif max_val8 > 30000000 and max_val8 > max_val3 and max_val8 > max_val5:
        # print('max_val8:',max_val8)
        top_left8 = max_loc8
        bottom_right8 = (top_left8[0] + w8, top_left8[1] + h8)
        mid_p = ( int((top_left8[0]+bottom_right8[0])/2), int((top_left8[1]+bottom_right8[1])/2) )
        circle = ( int(mid_p[0]+np.cos(18*np.pi/180)*205), int(mid_p[1]+np.sin(18*np.pi/180)*205), r)
    else:
        warnings.warn('no match found for number 3, 5, or 8.')
        return None

    return circle



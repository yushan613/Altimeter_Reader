import cv2
import numpy as np


def lineDetection(binary, img_gray):
    # get the edge of the binary image using Canny
    edges = cv2.Canny(image=binary, threshold1=100, threshold2=200, apertureSize=5)
    # HoughLinesP
    lines_list = []
    linesP = cv2.HoughLinesP(
        edges,  # Input edge image
        1,  # Distance resolution in pixels
        np.pi / 180,  # Angle resolution in radians
        threshold=28,  # Min number of votes for valid line
        minLineLength=16,  # Min allowed length of line
        maxLineGap=5  # Max allowed gap between line for joining them
    )
    # Iterate over points
    img_gray1 = img_gray.copy()
    for points in linesP:
        # Extracted points nested in the list
        x1, y1, x2, y2 = points[0]
        # Draw the lines joing the points on the original image
        cv2.line(img_gray1, (x1, y1), (x2, y2), (0, 255, 0), 1)
        # Maintain a simples lookup list for points
        lines_list.append([(x1, y1), (x2, y2)])

    # cv2.namedWindow('linesP', 0)
    # cv2.imshow('linesP', img_gray1)
    # cv2.waitKey(0)
    return linesP




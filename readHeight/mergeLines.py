import cv2
import numpy as np
from shapely.geometry import LineString
from scipy import spatial
import math
from selectLines import getAngle_new

### merge the lines that are very close together
def mergeLines(lines, img, circle):
    # lines: ndarray type, lines detected by HoughLinesP earlier
    # img: the grayscale image on which the new lines will be drawn on
    center_x = circle[0]
    center_y = circle[1]
    img_copy = img.copy()
    merged_lines = [] # lines that has been merged to another line

    for i in range(len(lines)):
        if i not in merged_lines:
            # print(lines[i][0])
            x1, y1, x2, y2 =lines[i][0]  #line_1

            for j in range(len(lines)-i-1):
                if i+j+1 not in merged_lines:
                    x3, y3, x4, y4 = lines[i+j+1][0]# line_2
                    # compute the minimum distance & difference between the two slopes
                    # minimum distance
                    l1 = LineString([(x1,y1),(x2,y2)])
                    l2 = LineString([(x3,y3),(x4,y4)])
                    mindist = l1.distance(l2)
                    # angle difference
                    angle_diff = np.abs(getAngle_new(lines[i]) - getAngle_new(lines[i+j+1]))

                    if mindist < 4 and angle_diff < 0.1:
                        # if the lines are really close
                        # we combine them to be a new line
                        # by finding the two end points that are furthest apart
                        # and form new line with these two points
                        pts = ([[x1,y1],[x2,y2],[x3,y3],[x4,y4]])
                        # get distances between each pair of candidate points
                        dist_mat = spatial.distance_matrix(pts, pts)
                        # get indices of candidates that are furthest apart
                        p1, p2 = np.unravel_index(dist_mat.argmax(), dist_mat.shape)
                        # end points of the new line segment
                        x1_new, y1_new = pts[p1]
                        x2_new, y2_new = pts[p2]

                        # remember which lines have been merged so we dont iterate it later
                        merged_lines.append(j+i+1)

                        # update line1 to be the new line
                        lines[i] = [[x1_new, y1_new, x2_new, y2_new]]
                        x1, y1, x2, y2 = lines[i][0]

    # update the lines array
    lines = np.delete(lines, merged_lines, axis=0)

    # delete the lines that are too short (<25)
    tooshort_lines = []
    for n in range(len(lines)):
        # Extracted points nested in the list
        x1, y1, x2, y2 = lines[n][0]
        if np.sqrt((x1-x2)**2 + (y1-y2)**2) < 15:
            tooshort_lines.append(n)
    lines = np.delete(lines, tooshort_lines, axis=0)

    # and draw on the image
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Draw the lines joing the points on the original image
        cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 1)
    # cv2.namedWindow('merged lines', 0)
    # cv2.imshow('merged lines', img_copy)
    # cv2.waitKey(0)
    return lines, img_copy

# center_x = circle1[0]
# center_y = circle1[1]
# new_lines, img_new = mergeLines(selected_lines, img, center_x, center_y)

# print(new_lines)
# print(new_lines[0])
# print(new_lines[0][0])
# print(len(new_lines))
# print(new_lines[0][0][0])

# cv2.imshow('merged lines', img_new)
# cv2.waitKey(0)
# cv2.imwrite('./imgs/merged_lines.jpg',img_new)
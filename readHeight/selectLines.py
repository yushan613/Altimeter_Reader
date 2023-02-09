import cv2
import numpy as np
from shapely.geometry import LineString
import math
from skimage.draw import line

def whiteBetween(pt1, pt2, img_bi):
    rr, cc = line(pt1[0], pt1[1], pt2[0], pt2[1])
    # if pt1[0] == 366 and pt1[1] == 399 and pt2[0] == 392:
    #     print(pt1)
    #     print(pt2)
    #     print(img_bi[cc, rr])
    count = sum(i > 245 for i in img_bi[cc, rr])
    if count >= len(img_bi[cc, rr]) * 0.4:
        return True
    else:
        return False

def rearrangeLines(line, center_x, center_y):
    # rearrange a line
    # so that the first point in the line is always closer to center point
    x1,y1,x2,y2 = line[0]
    dist1 = math.dist([x1, y1], [center_x,center_y])
    dist2 = math.dist([x2, y2], [center_x, center_y])

    if dist1 > dist2:
        line_new = [[x2, y2, x1, y1]]
    else:
        line_new = [[x1, y1, x2, y2]]
    return line_new

def getAngle_new(line):
    # each line has been rearranged in a way that the first point is
    # the one close to center, therefore we can use this property
    x1, y1, x2, y2 = line[0]
    if x1 == x2:
        if y2 > y1:
            angle = np.pi
        else:
            angle = 0
    elif x2 > x1:
        angle = math.atan((y1 - y2) / (x2 - x1))
        angle = np.pi/2 - angle
    elif x2 < x1:
        angle = math.atan((y1 - y2) / (x2 - x1))
        angle = np.pi * 3 / 2 - angle
    return angle

def intersection(line1, line2):
    # get the intersection point of two line segments
    # if the lines are not intersecting, extend them
    x1,y1,x2,y2 = line1[0]
    x3,y3,x4,y4 = line2[0]
    if x1 == x2 and x3 != x4:
        k2 = (y4-y3)/(x4-x3)
        b2 = y3-k2*x3
        inter_x = x1
        inter_y = k2 * inter_x + b2
    elif x1 != x2 and x3 == x4:
        k1 = (y2-y1)/(x2-x1)
        b1 = y1-k1*x1
        inter_x = x3
        inter_y = k1 * inter_x + b1
    elif x1 != x2 and x3 != x4:
        k1, k2 = (y2-y1)/(x2-x1), (y4-y3)/(x4-x3)
        b1, b2 = y1 - k1 * x1, y3-k2*x3
        if k1 != k2:
            inter_x = (b2-b1)/(k1-k2)
            inter_y = k1 * inter_x + b1
        else:
            inter_x = -9999
            inter_y = -9999
    else:
        inter_x = -9999
        inter_y = -9999
    return inter_x, inter_y

def middleLine(lines_2, center_x, center_y):
    # lines_2 is a list contains two lines that has been paired
    # mid_angle_theta is the angle to compute reading
    # while mid_angle_delta is the angle to compute line slope etc.
    x1,y1,x2,y2 = lines_2[0][0]
    x3,y3,x4,y4 = lines_2[1][0]
    # get the angles of line1 and line2
    angle1, angle2 = getAngle_new(lines_2[0]), getAngle_new(lines_2[1]) # [0, 2*pi) from y-axis
    delta1, delta2 = angleTrans(angle1), angleTrans(angle2)
    if np.abs(angle1 - angle2) > np.pi*3/2:
        mid_angle_theta = (angle1 + angle2)/2 - np.pi
        if mid_angle_theta < 0:
            mid_angle_theta = mid_angle_theta + 2*np.pi
    else:
        mid_angle_theta = (angle1 + angle2)/2

    if np.abs(angle1-angle2) < 0.05:
        # parallel lines, which means the long hand
        mid_p1 = [(x1 + x3)/2, (y1 + y3)/2]
        mid_p2 = [(x2 + x4)/2, (y2 + y4)/2]
        mid_line = [mid_p1, mid_p2]
    else:
        # not parallel, which means the short hand
        mid_angle_delta = (delta1 + delta2)/2
        interP_x, interP_y = intersection(lines_2[0], lines_2[1])
        if mid_angle_delta == np.pi/2 or mid_angle_delta == 3*np.pi/2:
            p1_x = interP_x
            p2_x = interP_x
            p1_y = lines_2[np.array([np.abs(y1-center_y), np.abs(y3-center_y)]).argmin()][0][1]
            p2_y = lines_2[np.array([np.abs(y2-center_y), np.abs(y4-center_y)]).argmax()][0][3]
        else:
            p1_x = lines_2[np.array([np.abs(x1 - center_x), np.abs(x3 - center_x)]).argmin()][0][0]
            p2_x = lines_2[np.array([np.abs(x2 - center_x), np.abs(x4 - center_x)]).argmax()][0][2]
            k = math.tan(mid_angle_delta)
            b = interP_y - k * interP_x
            p1_y = k * p1_x + b
            p2_y = k * p2_x + b
        mid_line = [[p1_x, p1_y], [p2_x, p2_y]]
    return mid_line, mid_angle_theta

def angleTrans(theta):
    # theta is the angle between a line and y-axis up
    # delta is the angle between a line and x-axis right
    # this function transform theta to delta
    delta = theta - np.pi/2
    if delta < 0:
        delta = delta + np.pi * 2
    # elif delta >
    return delta

def midLineTroughCenter(line1, line2, circle):
    # check whether the middle line of the two lines goes through the central area
    center_x, center_y = circle[0], circle[1]
    # get the middle line
    midLine, midAngel = middleLine((line1, line2), center_x, center_y)
    # get coefficients of the line
    a = midLine[0][1] - midLine[1][1]
    b = midLine[1][0] - midLine[0][0]
    c = midLine[0][0] * midLine[1][1] - midLine[1][0] * midLine[0][1]

    if a == 0 and b == 0:
        return False
    d = np.abs(a * center_x + b * center_y + c) / np.sqrt(a ** 2 + b ** 2)
    if d < 10:
        return True
    else:
        return False

def isShortTip(line1, line2, circle, img_bi):
    # check whether the two lines are the tip of shorthand
    center_x = circle[0]
    center_y = circle[1]
    r = circle[2]
    # rearrange
    line1 = rearrangeLines(line1, center_x, center_y)
    line2 = rearrangeLines(line2, center_x, center_y)
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    ls1 = LineString([(x1, y1), (x2, y2)])
    ls2 = LineString([(x3, y3), (x4, y4)])

    inter_x, inter_y = intersection(line1, line2)
    r_inner = int(r / 1.7)
    r_outter = int(r / 1.4)

    if inter_x == -9999 and inter_y == -9999:
        return False
    else:
        # compute angle_diff & dist & middleLine
        angle_diff = np.abs(getAngle_new(line1) - getAngle_new(line2))
        if angle_diff > np.pi*3/2:
            angle_diff = np.pi * 2 - angle_diff
        dist = ls1.distance(ls2)
        xy = (inter_x - center_x) ** 2 + (inter_y - center_y) ** 2
        throughCenter = midLineTroughCenter(line1, line2, circle)
        # WhiteInBetween = whiteBetween([x1, y1], [x3, y3], img_bi)
        # if line1[0][0] == 311 and line2[0][0] == 331:
        #     print(line1)
        #     print(line2)
        #     print('angleLine1:', getAngle_new(line1), 'angleLine2:', getAngle_new(line2))
        #     print('angle_dif:', angle_diff, 'dist:', dist, 'throughCenter:', throughCenter, 'WhiteBetween:', WhiteInBetween)
        if angle_diff < 0.9 and angle_diff > 0.60 and dist < 60 and r_inner ** 2 < xy and xy < r_outter ** 2 and throughCenter is True:#and WhiteInBetween is True
            return True
        else:
            return False


def SelectLines(circle, lines, img, img_bi):
    # make sure there are at least 2 lines
    if len(lines) < 2:
        print("Less than 2 lines.")
        exit()

    # get the center and radius of the circle
    x_circle = circle[0]
    y_circle = circle[1]
    r = circle[2]

    # define the radius of a circular area in the center
    # x,y of the area is the same as the circle
    r_new = 25

    # iterate all the lines
    lines_list = []
    img_new = img.copy()
    for line in lines:
        # get coefficients of the line and
        a = line[0, 1] - line[0, 3]
        b = line[0, 2] - line[0, 0]
        c = line[0, 0] * line[0, 3] - line[0, 2] * line[0, 1]

        # check if the line intersect with the circle
        d = np.abs(a * x_circle + b * y_circle + c) / np.sqrt(a ** 2 + b ** 2)

        if d <= r_new:
            # draw the selected lines on the original image
            cv2.line(img_new, (line[0, 0], line[0, 1]), (line[0, 2], line[0, 3]), (0, 255, 0), 1)
            lines_list.append([(line[0, 0], line[0, 1]), (line[0, 2], line[0, 3])])

    # now look for the two lines representing the tip of shorthand
    for i in range(len(lines)):
        for j in range(len(lines) - i - 1):
            isTip = isShortTip(lines[i], lines[j + i + 1], circle, img_bi)
            if isTip is True:
                cv2.line(img_new, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 255, 0), 1)
                cv2.line(img_new, (lines[j+i+1][0][0], lines[j+i+1][0][1]), (lines[j+i+1][0][2], lines[j+i+1][0][3]), (0, 255, 0), 1)
                lines_list.append([(lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3])])
                lines_list.append([(lines[j+i+1][0][0], lines[j+i+1][0][1]), (lines[j+i+1][0][2], lines[j+i+1][0][3])])

    # also draw the central circle on the image
    cv2.circle(img_new, (x_circle, y_circle), r_new, (0, 255, 0), 1)
    cv2.circle(img_new, (x_circle, y_circle), int(r / 1.7), (0, 255, 0), 1)
    cv2.circle(img_new, (x_circle, y_circle), int(r / 1.4), (0, 255, 0), 1)

    # cv2.imshow('selected lines', img_new)
    # cv2.waitKey(0)

    return lines_list





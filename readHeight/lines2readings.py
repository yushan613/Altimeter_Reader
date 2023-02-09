import cv2
import numpy as np
from shapely.geometry import LineString
import math
import warnings
from selectLines import *


"""
this file is to get the readings for the clocks from the lines
first make sure there are 4 lines left (this script is not able to deal with other situations)
then pair the 4 lines into 2 pairs, and find the middle line for each pair, also indentify which is short/long hand
finally get the readings for the clock by computing the angles
"""

def shortest(reading, angle_short, angle_long, circle, img_bi, img_gray):
    center_x = circle[0]
    center_y = circle[1]
    r = circle[2]
    # print('r:', r)

    angle_shortest_0 = np.pi/2 - (np.pi * 2 / 100000) * reading
    angle_shortest_1 = np.pi/2 - ((np.pi * 2 / 100000) * (reading + 10000))
    angle_shortest_2 = np.pi/2 - ((np.pi * 2 / 100000) * (reading + 20000))

    # print('angle_shortest_0:', angle_shortest_0)
    k_0 = -(math.tan(angle_shortest_0))
    # print('k_0:', k_0)
    k_1 = -(math.tan(angle_shortest_1))
    k_2 = -(math.tan(angle_shortest_2))
    b_0 = center_y - k_0 * center_x
    b_1 = center_y - k_1 * center_x
    b_2 = center_y - k_2 * center_x

    x1_0 = int( center_x + abs(r / 4 * math.cos(angle_shortest_0)))
    y1_0 = int(k_0 * x1_0 + b_0)
    x2_0 = int(center_x + abs(r * 5 / 12 * math.cos(angle_shortest_0)))
    y2_0 = int(k_0 * x2_0 + b_0)

    x1_1 = int(center_x + abs(r / 4 * math.cos(angle_shortest_1)))
    y1_1 = int(k_1 * x1_1 + b_1)
    x2_1 = int(center_x + abs(r * 5 / 12 * math.cos(angle_shortest_1)))
    y2_1 = int(k_1 * x2_1 + b_1)

    x1_2 = int(center_x + abs(r / 4 * math.cos(angle_shortest_2)))
    y1_2 = int(k_2 * x1_2 + b_2)
    x2_2 = int(center_x + abs(r * 5 / 12 * math.cos(angle_shortest_2)))
    y2_2 = int(k_2 * x2_2 + b_2)


    # print('x1:', x1_0, 'y1:', y1_0, 'x2:', x2_0, 'y2:', y2_0)
    img_gray1 = img_gray.copy()
    cv2.line(img_gray1, (x1_0, y1_0), (x2_0, y2_0), (0, 255, 0), 1)
    cv2.line(img_gray1, (x1_1, y1_1), (x2_1, y2_1), (0, 255, 0), 1)
    cv2.line(img_gray1, (x1_2, y1_2), (x2_2, y2_2), (0, 255, 0), 1)
    cv2.circle(img_gray1, (center_x, center_y), r, (0, 255, 0), 2)


    rr0, cc0 = line(x1_0, y1_0, x2_0, y2_0)
    rr1, cc1 = line(x1_1, y1_1, x2_1, y2_1)
    rr2, cc2 = line(x1_2, y1_2, x2_2, y2_2)
    count0 = sum(i > 245 for i in img_bi[cc0, rr0])
    count1 = sum(i > 245 for i in img_bi[cc1, rr1])
    count2 = sum(i > 245 for i in img_bi[cc2, rr2])
    th0 = len(img_bi[cc0, rr0]) * 0.5
    th1 = len(img_bi[cc1, rr1]) * 0.5
    th2 = len(img_bi[cc2, rr2]) * 0.5

    # take into account the tail of the long hand
    angle_tail = -1
    if np.pi <= angle_long <= 3 * np.pi/ 2:
        angle_tail = angle_long - np.pi

    #
    if count0 >= th0 and count1 < th1 and count2 < th2:
        if (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and abs(angle_tail - angle_shortest_1) < 0.15:
            return 1
        elif (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and abs(angle_tail - angle_shortest_2) < 0.15:
            return 2
        else:
            return 0
    elif count1 >= th1 and count0 < th0 and count2 < th2:
        if (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and abs(angle_tail - angle_shortest_0) < 0.15:
            return 0
        elif (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and abs(angle_tail - angle_shortest_2) < 0.15:
            return 2
        else:
            return 1
    elif count2 >= th2 and count0 < th0 and count1 < th1:
        if (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and abs(
                angle_tail - angle_shortest_0) < 0.15:
            return 0
        elif (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and abs(
                angle_tail - angle_shortest_1) < 0.15:
            return 1
        else:
            return 2


    elif count0 >= th0 and count1 >= th1 and count2 < th2:
        if (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and (abs(angle_shortest_1 - angle_short) >= 0.3 or abs(angle_shortest_1 - angle_long) >= 0.2):
            return 1
        elif (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and (abs(angle_shortest_0 - angle_short) >= 0.3 or abs(angle_shortest_0 - angle_long) >= 0.2):
            return 0
        else:
            if abs(angle_tail - angle_shortest_2) < 0.15:
                return 2
            else:
                if reading < 4000:
                    return 2
                else:
                    return 1
    elif count0 >= th0 and count1 < th1 and count2 >= th2:
        if (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and (abs(angle_shortest_2 - angle_short) >= 0.3 or abs(angle_shortest_2 - angle_long) >= 0.2):
            return 2
        elif (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and (abs(angle_shortest_0 - angle_short) >= 0.3 or abs(angle_shortest_0 - angle_long) >= 0.2):
            return 0
        else:
            if abs(angle_tail - angle_shortest_1) < 0.15:
                return 1
            else:
                if reading < 4000:
                    return 2
                else:
                    return 1
    elif count0 < th0 and count1 >= th1 and count2 >= th2:
        if (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and (abs(angle_shortest_2 - angle_short) >= 0.3 or abs(angle_shortest_2 - angle_long) >= 0.2):
            return 2
        elif (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and (abs(angle_shortest_1 - angle_short) >= 0.3 or abs(angle_shortest_1 - angle_long) >= 0.2):
            return 1
        else:
            if abs(angle_tail - angle_shortest_0) < 0.15:
                return 0
            else:
                if reading < 4000:
                    return 2
                else:
                    return 1
    elif count0 >= th0 and count1 >= th1 and count2 >= th2:
        if (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and (abs(angle_shortest_2 - angle_short) >= 0.3 or abs(angle_shortest_2 - angle_long) >= 0.2):
            return 2
        elif (abs(angle_shortest_0 - angle_short) < 0.3 or abs(angle_shortest_0 - angle_long) < 0.2) and (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and (abs(angle_shortest_1 - angle_short) >= 0.3 or abs(angle_shortest_1 - angle_long) >= 0.2):
            return 1
        elif (abs(angle_shortest_1 - angle_short) < 0.3 or abs(angle_shortest_1 - angle_long) < 0.2) and (abs(angle_shortest_2 - angle_short) < 0.3 or abs(angle_shortest_2 - angle_long) < 0.2) and (abs(angle_shortest_0 - angle_short) >= 0.3 or abs(angle_shortest_0 - angle_long) >= 0.2):
            return 0
        else:
            if reading < 4000:
                return 2
            else:
                return 1
    elif count0 < th0 and count1 < th1 and count2 < th2:
        if angle_tail != -1:
            if angle_tail < 0.62832:
                return 0
            elif 0.62832 <= angle_tail < 1.25664:
                return 1
            elif 1.25664 <= angle_tail < 1.88849:
                return 2
        else:
            if reading < 4000:
                return 2
            else:
                return 1


def isShortBetween01(img_gray, img_bi, circle):
    # see if there is enough 255 pixels between 0 and 1
    center_x = circle[0]
    center_y = circle[1]
    r = circle[2]
    x0 = center_x
    y0 = center_y - 90
    x1 = x0 + 60
    y1 = y0
    # img_gray1 = img_gray.copy()
    # cv2.line(img_gray1, (x0, y0), (x1, y1), (0, 255, 0), 2)
    # cv2.imshow('line on img gray', img_gray1)
    # cv2.waitKey(0)

    rr, cc = line(x0, y0, x1, y1)
    count = sum(i > 245 for i in img_bi[cc, rr])
    if count >= len(img_bi[cc, rr]) * 0.4:
        return True
    else:
        return False

def extendDist(line1, line2, center_x, center_y):
    # extend the lines to the center (to make sure the lines are not too far away)
    # and return the minimum distance between them
    # this is only for the parallel lines
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    # extend line1 to the longest possible
    if x1 == x2:
        y1 = center_y
        y2 = y4
    else:
        k1 = (y2 - y1) / (x2 - x1)
        b1 = y1 - k1 * x1
        if np.abs(x2 - center_x) > np.abs(x4 - center_x):
            x1 = center_x
            y1 = k1 * x1 + b1
        else:
            x2 = x4
            y2 = k1 * x2 + b1
    ls1 = LineString([(x1, y1), (x2, y2)])
    ls2 = LineString([(x3, y3), (x4, y4)])
    dist = ls1.distance(ls2)
    return dist

def isShortHand(line1, line2, circle, img_bi):
    # check whether two lines are short hand body
    center_x = circle[0]
    center_y = circle[1]
    r = circle[2]
    x1, y1, x2, y2 = line1[0]
    x3, y3, x4, y4 = line2[0]
    ls1 = LineString([(x1, y1), (x2, y2)])
    ls2 = LineString([(x3, y3), (x4, y4)])
    # the two lines should be within a certain r_within
    r_within = int(r / 2.6)
    xy1 = (x1-center_x)**2 + (y1-center_y)**2
    xy3 = (x3-center_x)**2 + (y3-center_y)**2
    angle_diff = np.abs(getAngle_new(line1) - getAngle_new(line2))
    if angle_diff > np.pi*3/2:
        angle_diff = np.pi * 2 - angle_diff
    dist = ls1.distance(ls2)
    throughCenter = midLineTroughCenter(line1, line2, circle)
    WhiteInBetween = whiteBetween([x1, y1], [x3, y3], img_bi)
    # if line1[0][0] == 176 and line2[0][0] == 217:
    #     print(line1)
    #     print(line2)
    #     print('angle line1:', getAngle_new(line1))
    #     print('angle line2:', getAngle_new(line2))
    #     print('angledif:', angle_diff, 'dist:', dist, 'throughcenter:', throughCenter)
    if xy1 < r_within ** 2 and xy3 < r_within ** 2 and angle_diff < 0.3 and angle_diff > 0.1 and dist < 46 and dist > 25 and throughCenter is True and WhiteInBetween is True:
        return True
    else:
        return False

def isLongHand(line1, line2, circle, img_bi):
    # check whether two lines are longhand
    center_x = circle[0]
    center_y = circle[1]
    angle_diff = np.abs(getAngle_new(line1) - getAngle_new(line2))
    if angle_diff > np.pi*3/2:
        angle_diff = np.pi * 2 - angle_diff
    dist = extendDist(line1, line2, center_x, center_y)
    throughCenter = midLineTroughCenter(line1, line2, circle)
    WhiteInBetween = whiteBetween([line1[0][0], line1[0][1]], [line2[0][0], line2[0][1]], img_bi)
    if angle_diff < 0.1 and dist < 45 and dist > 23 and throughCenter is True and WhiteInBetween is True:
        return True
    else:
        return False


def lines2readings(lines, img, circle, img_bi):
    # lines is a list with more than 1 lines representing long/short hands
    # img is the original full-sized image

    # first check the number of lines
    if len(lines) <= 1:
        warnings.warn('There is less than 2 lines detected, unable to read.')

    # re-arrange the points in the lines
    center_x, center_y = circle[0], circle[1]
    for n in range(len(lines)):
        lines[n] = rearrangeLines(lines[n], center_x, center_y)

    # pair the lines
    # the 2 lines of the longhand:  perfectly parallel, extended lines having certain distance
    # the 2 lines of the shorthand: within certain distance, certain slope difference
    flag_long = 0  # a flag to indicate whether the lines have been paired
    flag_short = 0
    flag_tip = 0
    for i in range(len(lines)):
        for j in range(len(lines)-i-1):
            isLong = isLongHand(lines[i], lines[j+i+1], circle, img_bi)
            isShort = isShortHand(lines[i], lines[j+i+1], circle, img_bi)
            isTip = isShortTip(lines[i], lines[j+i+1], circle, img_bi)


            if isLong is True and isShort is False and isTip is False:
                longHand = (lines[i], lines[i+j+1])
                flag_long = 1
            if isShort is True and isLong is False and isTip is False:
                shortHand = (lines[i], lines[i+j+1])
                flag_short = 1
            elif isTip is True and isLong is False and isShort is False:
                shortTip = (lines[i], lines[i+j+1])
                flag_tip = 1

    img_new = img.copy()
    if flag_long == 1:
        # compute and draw the middle line for longhand
        mid_line_long, angle_long = middleLine(longHand, center_x, center_y)
        cv2.line(img_new, (int(mid_line_long[0][0]), int(mid_line_long[0][1])),
                 (int(mid_line_long[1][0]), int(mid_line_long[1][1])), (0, 255, 0), 1)
        if flag_short == 1:
            # get the middle lines for the shorthand
            mid_line_short, angle_short = middleLine(shortHand, center_x, center_y)
            if flag_tip == 1:
                # get the middle line for the short tip
                mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
                if np.abs(angle_tip-angle_short) < 0.3:
                    print('Found: longhand + shorthand + shorthand tip')
                    cv2.line(img_new, (int(mid_line_short[0][0]), int(mid_line_short[0][1])),
                             (int(mid_line_short[1][0]), int(mid_line_short[1][1])), (0, 255, 0), 1)
                    cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                             (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
                    # get the readings for short&tip/long hand from the angle
                    # long hand: 2*pi = 1000 ft
                    reading_long = (1000 / (2 * np.pi)) * angle_long
                    # short hand: 2*pi = 1000*10 ft
                    reading_short = (10000 / (2 * np.pi)) * ((angle_short + angle_tip) / 2)
                    reading_short_th = int( ((10000 / (2 * np.pi)) * (angle_short + angle_tip) / 2) / 1000) * 1000
                    shortLongDif = abs(reading_short - reading_long - reading_short_th)
                    # Check if short and long hands consist on how many hundreds
                    # if consistent, use short + long, if not, trust short hand
                    if shortLongDif < 500:
                        # print('reading_short_th', reading_short_th, 'reading_long', reading_long)
                        readings = reading_short_th + reading_long
                    else:
                        readings = reading_short

                    # # only need to know how many thousands
                    # readings = reading_short + reading_long
                else:
                    cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                             (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
                    print('Found: longhand + shorthand + shorthand tip (but shorthand and short tip not on same line, will trust short tip)')
                    angle_short = angle_tip
                    # get the readings for short&tip/long hand from the angle
                    # long hand: 2*pi = 1000 m
                    reading_long = (1000 / (2 * np.pi)) * angle_long
                    # short hand: 2*pi = 1000*10 ft
                    reading_short = (10000 / (2 * np.pi)) * angle_short
                    reading_short_th = int(((10000 / (2 * np.pi)) * angle_short) / 1000) * 1000
                    shortLongDif = abs(reading_short - reading_long - reading_short_th)
                    # Check if short and long hands consist on how many hundreds
                    # if consistent, use short + long, if not, trust short hand
                    if shortLongDif < 500:
                        readings = reading_short_th + reading_long
                    else:
                        readings = reading_short
                    readings = reading_short + reading_long
            else:
                print('Found: longhand + shorthand')
                # get the readings for short/long hand from the angle
                # long hand: 2*pi = 1000 ft
                reading_long = (1000 / (2 * np.pi)) * angle_long
                # short hand: 2*pi = 1000*10 ft
                reading_short = (10000 / (2 * np.pi)) * angle_short
                reading_short_th = int(
                    ((10000 / (2 * np.pi)) * angle_short) / 1000) * 1000  # only need to know how many thousands
                shortLongDif = abs(reading_short - reading_long - reading_short_th)
                # Check if short and long hands consist on how many hundreds
                # if consistent, use short + long, if not, trust short hand
                if shortLongDif < 500:
                    readings = reading_short_th + reading_long
                else:
                    readings = reading_short
                readings = reading_short + reading_long

        elif flag_tip == 1:
            print('Found: longhand + shorthand tip')
            mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
            # draw on the image
            cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                     (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
            # get the readings for short/long hand from the angle
            # long hand: 2*pi = 1000 m
            reading_long = (1000 / (2 * np.pi)) * angle_long
            # short hand: 2*pi = 1000*10 ft
            reading_short = (10000 / (2 * np.pi)) * angle_tip
            reading_short_th = int(
                ((10000 / (2 * np.pi)) * angle_tip) / 1000) * 1000  # only need to know how many thousands
            shortLongDif = abs(reading_short - reading_long - reading_short_th)
            # Check if short and long hands consist on how many hundreds
            # if consistent, use short + long, if not, trust short hand
            angle_short = angle_tip
            if shortLongDif < 500:
                readings = reading_short_th + reading_long
            else:
                readings = reading_short
            readings = reading_short + reading_long
        else:
            # warnings.warn('Found only longhand, unable to read')
            # readings = -9999
            short01 = isShortBetween01(img, img_bi, circle)
            if short01 is True:
                print('Found: longhand + shorthand might between 0~1')
                # mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
                # draw on the image
                cv2.line(img_new, (center_x, center_y), (center_x, center_y - 80), (0, 255, 0), 1)
                # get the readings for short/long hand from the angle
                # long hand: 2*pi = 1000 ft
                reading_long = (1000 / (2 * np.pi)) * angle_long
                # short hand: 2*pi = 1000*10 ft
                reading_short = 0  # only need to know how many thousands
                readings = reading_short + reading_long
            else:
                print('Found: longhand + shorthand might overlay longhand')
                # get the readings for short/long hand from the angle
                # long hand: 2*pi = 1000 m
                reading_long = (1000 / (2 * np.pi)) * angle_long
                # short hand: 2*pi = 1000*10 ft
                reading_short = int(
                    ((10000 / (2 * np.pi)) * angle_long) / 1000) * 1000  # only need to know how many thousands
                readings = reading_short + reading_long
            angle_short = ((2 * np.pi) / 10000) * readings

    elif flag_short == 1:
        mid_line_short, angle_short = middleLine(shortHand, center_x, center_y)
        if flag_tip == 1:
            cv2.line(img_new, (int(mid_line_short[0][0]), int(mid_line_short[0][1])),
                     (int(mid_line_short[1][0]), int(mid_line_short[1][1])), (0, 255, 0), 1)
            mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
            cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                     (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
            if np.abs(angle_tip-angle_short) < 0.3:
                print('Found: shorthand + shorthand tip')
                # get the 2 readings for short hand from the angle
                # short hand: 2*pi = 1000*10 ft
                reading_short = (10000 / (2 * np.pi)) * angle_short
                reading_tip = (10000 / (2 * np.pi)) * angle_tip
                readings = (reading_short + reading_tip) / 2
                angle_long = (np.pi*2 / 1000) * (readings - int((readings / 1000) * 1000))
            else:
                print('Shorthand and short tip not on same line, will trust short tip')
                mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
                cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                         (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
                reading_tip = (10000 / (2 * np.pi)) * angle_tip
                readings = reading_tip
                angle_short = angle_tip
                angle_long = (np.pi * 2 / 1000) * (readings - int((readings / 1000) * 1000))
        else:
            print('Found: shorthand')
            # short hand: 2*pi = 1000*10 ft
            reading_short = (10000 / (2 * np.pi)) * angle_short  # approximate reading only from the short hand
            readings = reading_short  # accuracy ~ 50ft
            angle_long = (np.pi * 2 / 1000) * (readings - int((readings / 1000) * 1000))
    elif flag_tip == 1:
        print('Found: shorthand tip')
        mid_line_tip, angle_tip = middleLine(shortTip, center_x, center_y)
        cv2.line(img_new, (int(mid_line_tip[0][0]), int(mid_line_tip[0][1])),
                 (int(mid_line_tip[1][0]), int(mid_line_tip[1][1])), (0, 255, 0), 1)
        # get the readings for short hand tip from the angle
        # short hand: 2*pi = 1000*10 ft
        reading_tip = (10000 / (2 * np.pi)) * angle_tip
        readings = reading_tip
        angle_short = angle_tip
        angle_long = (np.pi * 2 / 1000) * (readings - int((readings / 1000) * 1000))
    else:
        warnings.warn('No hand found')
        readings = -9999

    # new method to decide the shortest hand
    if readings == -9999:
        return img_new, readings
    elif readings > 5000:
        shortesthand = shortest(readings, angle_short, angle_long,  circle, img_bi, img)
        readings = readings + shortesthand * 10000
    else:
        readings = readings + 10000


    return img_new, readings

import os

import cv2
import numpy as np

CONST_RED_LOWER = np.array([200, 0, 0])
CONST_RED_UPPER = np.array([255, 20, 20])
CONST_A4_LENGTH = 1123
CONST_A4_WIDTH = 794


def print_codes_with_new_pages(filename):
    sized_dots = find_xy_in_large_sized(filename)
    count = 1
    #
    # Modify offset here
    #
    offset = -7
    for dot in sorted(sized_dots):
        print("LODOP.ADD_PRINT_TEXT({0}, {1}, 100, 20, \"{2}\");".format(dot[0] + offset, dot[1], count))
        count += 1
    print("LODOP.NEWPAGE();")


def print_codes(filename, page_index):
    sized_dots = find_xy_in_large_sized(filename)

    blank_count = 1
    # vertical_offset is configured -1 because
    # the dot position is on the bottom of one line of text
    vertical_offset = -7
    for dot in sorted(sized_dots):
        print("LODOP.ADD_PRINT_TEXT({0}, {1}, 100, 20, \"{2}\");".format(
            dot[0] + vertical_offset + page_index * CONST_A4_LENGTH, dot[1], blank_count))
        blank_count += 1


def print_codes_with_blank_data(filename, page_index, blank_data):
    sized_dots = find_xy_in_large_sized(filename)

    blank_count = 1
    # vertical_offset is configured -7 because
    # the dot position is on the bottom of one line of text
    vertical_offset = -7
    for dot in sorted(sized_dots):
        print("LODOP.ADD_PRINT_TEXT({0}, {1}, 100, 20, {2});".format(
            dot[0] + vertical_offset + page_index * CONST_A4_LENGTH, dot[1], blank_data[blank_count - 1]))
        blank_count += 1


def find_xy_in_large_sized(filename):
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mask = cv2.inRange(img, CONST_RED_LOWER, CONST_RED_UPPER)
    dot_coordinates = np.where(mask != 0)
    dot_coordinates = set(zip(dot_coordinates[0], dot_coordinates[1]))
    dot_coordinates = sorted(dot_coordinates)
    sized_dots = set()
    for coors in dot_coordinates:
        sized_dots.add((int(coors[0] * 794 / 4961), int(coors[1] * 794 / 4961)))
    adjust_dots_in_one_line(sized_dots)
    remove_duplicate_dots(sized_dots)
    return sized_dots


def remove_duplicate_dots(sized_dots):
    sorted_sized_dots = sorted(sized_dots)
    pre = (0, 0)
    for dot in sorted_sized_dots:
        # debug:
        # print(dot, abs(dot[0] - pre[0]), abs(dot[1] - pre[1]))
        if abs(dot[0] - pre[0]) <= 15 and abs(dot[1] - pre[1]) <= 15:
            # debug:
            # print("{0} is removed because of {1}".format(dot, pre))
            # here sizedDots will be manipulated
            sized_dots.remove(dot)
            continue
        pre = dot
    # debug:
    # print(sorted(sizedDots))
    sorted_sized_dots = sorted(sized_dots, key=lambda k: [k[1], k[0]])

    pre = (0, 0)
    for dot in sorted_sized_dots:
        # debug:
        # print(dot, abs(dot[0] - pre[0]), abs(dot[1] - pre[1]))
        if abs(dot[0] - pre[0]) <= 15 and abs(dot[1] - pre[1]) <= 15:
            # debug:
            # print("{0} is removed because of {1}".format(dot, pre))
            # here sizedDots will be manipulated
            sized_dots.remove(dot)
            continue
        pre = dot


def adjust_dots_in_one_line(sized_dots):
    sorted_sized_dots = sorted(sized_dots)
    pre = (0, 0)
    for dot in sorted_sized_dots:
        if dot[0] - pre[0] <= 2:
            # debug:
            # print("{0} is adjusted because of {1}".format(dot, pre))
            # here sizedDots will be manipulated
            sized_dots.remove(dot)
            new_dot = (pre[0], dot[1])
            sized_dots.add(new_dot)
            pre = new_dot
            continue
        pre = dot

# Edit Code Here
picsDirectory = "resource/pics/"
filenames = os.walk(picsDirectory).__next__()[2]

# page_count default: 1
page_count = 1
for filename in filenames:
    # print(filename)
    print("// Page: ", page_count)
    # print_codes(picsDirectory + filename, page_count - 1)
    print_codes(picsDirectory + filename, page_count - 1)
    page_count += 1

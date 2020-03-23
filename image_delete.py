# Resources
# https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
# https://stackoverflow.com/questions/52505906/find-if-image-is-bright-or-dark
# https://towardsdatascience.com/automatic-image-quality-assessment-in-python-391a6be52c11
# https://towardsdatascience.com/deep-image-quality-assessment-with-tensorflow-2-0-69ed8c32f195

"""
When executed from the command line this script takes
in a pathname of a folder with pictures in it and a threshold
for when an image is considered too blurry (defaults to 100)

It then recursively searches images in subfolders of root_path
then loops through the images, calculates sharpness and
brightness and uses these to determine wether to move the image
or ignore it.

TODO:
MVP:
[] Make this work with other models than iPhone 4 by detecting camera model from metadata
[] If metadata cannot be read get thresholds from commad line:
    [] take lower bound threshold for sharpness and
    [] upper and lower bounds for brightness from command line args
NICE TO HAVE:
- look at more advanced factors other than sharpness and brightness
- build interface with input for root path, porgress bar and options for threshold
- make installable on windows, mac and linux
"""

import argparse
import sys
from os import path
from shutil import copy

import numpy as np
from cv2 import COLOR_BGR2GRAY, CV_64F, Laplacian, cvtColor, imread
from imutils import paths


class ImageDelete():
    def __init__(self):
        self.trash_path = "./trash/"
        self.root_path = None
        self.threshold = None
        self.upper_brightness = None
        self.lower_brightness = None
        self.path_as_string = None

        print("\n")
        print("============== IMAGE-DELETE CLI ==============")
        print("\n")
        print("Welcome to the IMAGE-DELETE CLI. Based on your input blurry and under / overexposed images will be deleted and free up some disk space by deleting them.")
        print("\n")
        print("Lets get started...")

    def get_args(self):
        while True:

            try:
                print("\n")
                print("============== 1/4 SELECT FOLDER")
                print("\n")
                self.root_path = input(
                    "Please provide the root path of the folder that contains the pictures you want to check: ")

                if not path.isdir(self.root_path):
                    raise ValueError

            except ValueError:
                print("\n")
                print("ERROR! This is not a number. Starting over...")
                print("\n")
                continue

            try:
                print("\n")
                print("============== 2/4 ENTER SHARPNESS THRESHOLD")
                print("\n")
                print("Please enter the sharpness threshold. Note: The lower the number, the more tolerant the selection, i.e. blurier pictures will make it through the filter.")
                self.threshold = int(input("Sharpness threshold: "))

            except ValueError:
                print("\n")
                print("ERROR! This is not a number. Starting over...")
                print("\n")
                continue

            try:
                print("\n")
                print("============== 3/4 ENTER BRIGHTNESS - LOWER BOUND")
                print("\n")
                print("Please enter the upper bound of the brighntess that is still acceptable for you. Note: Lowest value here is 0. The lower the number, the darker the pictures will be that make it through the filter")
                self.lower_brightness = int(input("Brightness - lower bound: "))

            except ValueError:
                print("\n")
                print("ERROR! This is not a number. Starting over...")
                print("\n")
                continue

            try:
                print("\n")
                print("============== 4/4 ENTER BRIGHTNESS: UPPER BOUND")
                print("\n")
                print("Please enter the upper bound of the brighntess\nthat is still acceptable for you.\nNote: Max value here is 255. The higher the number,\nthe brighter the pictures will be that make it\nthrough the filter.\n")
                self.upper_brightness = int(input("Brightness - upper bound: "))

            except ValueError:
                print("\n")
                print("ERROR! This is not a number. Starting over...")
                print("\n")
                continue

            else:
                print("\n")
                print("============== ALL SET!")
                print("\n")
                print(f"Folder:{self.root_path}")
                print(f"Sharpness Threshold:\t{self.threshold}")
                print(f"Brightness Upper:\t{self.upper_brightness}")
                print(f"Brightness Lower:\t{self.lower_brightness}")
                print("\n")
                print("Searching for images...")
                break

    def variance_of_laplacian(self, image):
        """
        The function calculates the Laplacian of the source image. It highlights regions of rapid intensity change and is therefore often used for edge detection.
        """
        # CV_64F bc we need a floating point data type for negative values. An unsigned 8-bit integer cannot handle negative values.
        return Laplacian(image, CV_64F).var()

    def is_unsharp(self, gray):
        score = self.variance_of_laplacian(gray)
        return score < self.threshold

    def is_brightness_bad(self, gray):
        return np.mean(gray) > 240 or np.mean(gray) < 50

    def deleteImages(self):
        # 'list_images' recursively looks through root folder and finds images of all types and returns their paths
        for image_path in paths.list_images(self.root_path):
            file_name = path.basename(image_path)
            destination = self.trash_path + file_name

            img = imread(image_path)
            gray = cvtColor(img, COLOR_BGR2GRAY)

            if self.is_unsharp(gray) and self.is_brightness_bad(gray):
                try:
                    # TODO: replace copy with move and destination should be trash-bin
                    copy(image_path, destination)
                    print("Image deleted")
                except FileNotFoundError as error:
                    print(error)
                    sys.exit(1)


imageDelete = ImageDelete()
imageDelete.get_args()
imageDelete.deleteImages()

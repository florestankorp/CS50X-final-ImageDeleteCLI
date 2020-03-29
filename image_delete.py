# Resources
# https://www.pyimagesearch.com/2015/09/07/blur-detection-with-opencv/
# https://stackoverflow.com/questions/52505906/find-if-image-is-bright-or-dark
# https://towardsdatascience.com/automatic-image-quality-assessment-in-python-391a6be52c11
# https://towardsdatascience.com/deep-image-quality-assessment-with-tensorflow-2-0-69ed8c32f195

"""
This CLI takes in a path, brightness and sharpness thresholds and then recursively searches images in the provided folder, evaluates the file and either keeps the ones of acceptable quality or moves them to the trashbin if they're not good enough.

TODO:
NICE TO HAVE:
[] Try getting metadata and based on camera model determine parameters
[] look at more advanced factors other than sharpness and brightness
[] build interface with input for root path, porgress bar and options for threshold as GUI
[] make installable on windows, mac and linux

TEST FOLDER:
/media/florestan/BACKUP/FileHistory/Florestan/FLO_MACHINE/Data/E/Pictures/IPHONE/2013
"""

import argparse
import sys
import textwrap
from os import path, remove
from shutil import copy

import numpy as np
from cv2 import COLOR_BGR2GRAY, CV_64F, Laplacian, cvtColor, imread
from imutils import paths
from send2trash import send2trash


class ImageDeleteCLI():
    def __init__(self):
        # instatiating class attributes
        self.root_path = None
        self.threshold = None
        self.upper_brightness = None
        self.lower_brightness = None
        self.path_as_string = None
        self.confirmation = None

        self.texts = {
            "WELCOME": "Welcome to the IMAGE-DELETE CLI. This CLI takes in a path, brightness and sharpness thresholds, recursively looks for images in the provided folder and deletes the ones that aren't good enough.",
            "PROVIDE_PATH": "Please provide the root path of the folder that contains the pictures you want to check: ",
            "UPPER_BOUND": "Please enter the upper bound of the brighntess that is still acceptable for you. Note: Max value here is 255. The higher the number, the brighter the pictures will be that make it through the filter.",
            "LOWER_BOUND": "Please enter the lower bound of the brighntess that is still acceptable for you. Note: Lowest value here is 0. The lower the number, the darker the pictures will be that make it through the filter.",
            "SHARPNESS_THRESHOLD": "Please enter the sharpness threshold. Note: The lower the number, the more tolerant the selection, i.e. blurier pictures will make it through the filter.",
            "CONFIRMATION": "You have entered all the required information. Please confirm that you want to proceed. Note: Rejected images will be moved to the trashbin. You can review them and if necessary restore them from there."
        }
        self.titles = {
            "WELCOME": """
============================================================

╦╔╦╗╔═╗╔═╗╔═╗  ╔╦╗╔═╗╦  ╔═╗╔╦╗╔═╗  ╔═╗╦  ╦
║║║║╠═╣║ ╦║╣    ║║║╣ ║  ║╣  ║ ║╣   ║  ║  ║
╩╩ ╩╩ ╩╚═╝╚═╝  ═╩╝╚═╝╩═╝╚═╝ ╩ ╚═╝  ╚═╝╩═╝╩

============================================================

Florestan Korp (2020)
florestankorp@gmail.com

============================================================
            """,
            "SELECT_FOLDER": "1/4 SELECT FOLDER",
            "SHARPNESS_THRESHOLD": "2/4 ENTER SHARPNESS THRESHOLD",
            "LOWER_BOUND": "3/4 ENTER BRIGHTNESS - LOWER BOUND",
            "UPPER_BOUND": "4/4 ENTER BRIGHTNESS - UPPER BOUND",
            "CONFIRMATION": "CONFIRMATION",
        }

        self.print_formatted(self.titles["WELCOME"],
                             self.texts["WELCOME"])

        print("Lets get started...")

    def get_input(self):
        self.get_path()
        self.get_sharpness()
        self.get_lower()
        self.get_upper()
        self.get_confirmation()

    def get_path(self):
        while True:
            try:
                self.print_formatted(self.titles["SELECT_FOLDER"],
                                     self.texts["PROVIDE_PATH"])
                self.root_path = input()

                if not path.isdir(self.root_path):
                    raise ValueError

            except ValueError:
                self.print_error("path")
                continue

            else:
                break

    def get_sharpness(self):
        while True:
            try:
                self.print_formatted(self.titles["SHARPNESS_THRESHOLD"],
                                     self.texts["SHARPNESS_THRESHOLD"])
                self.threshold = int(input("Sharpness threshold: "))

            except ValueError:
                self.print_error("number")
                continue

            else:
                break

    def get_lower(self):
        while True:
            try:
                self.print_formatted(self.titles["LOWER_BOUND"],
                                     self.texts["LOWER_BOUND"])
                self.lower_brightness = int(input("Brightness - lower bound: "))
                if (self.lower_brightness < 0) or (self.lower_brightness > 255):
                    raise ValueError

            except ValueError:
                self.print_error("number")
                continue

            else:
                break

    def get_upper(self):

        while True:
            try:
                self.print_formatted(self.titles["UPPER_BOUND"],
                                     self.texts["UPPER_BOUND"])
                self.upper_brightness = int(input("Brightness - upper bound: "))
                if (self.upper_brightness < 0) or (self.upper_brightness > 255):
                    raise ValueError

            except ValueError:
                self.print_error("number")
                continue

            else:
                break

    def get_confirmation(self):
        while True:
            try:
                self.print_formatted(self.titles["CONFIRMATION"],
                                     self.texts["CONFIRMATION"])
                self.print_summary()
                self.confirmation = input("Are you sure you want to proceed (y/n): ")

                if (
                        not self.confirmation.isalpha() and
                        not self.confirmation == 'y' and
                        not self.confirmation == 'n'
                ):
                    raise ValueError

                if self.confirmation == 'n':
                    print("Goodbye!")
                    sys.exit(1)

            except ValueError:
                self.print_error("input")
                continue

            else:
                print("\n")
                print(" DELETING IMAGES ".center(60, '='))
                break

    def print_summary(self):
        print(f"Folder:\t\t\t{self.root_path}")
        print(f"Sharpness Threshold:\t{self.threshold}")
        print(f"Brightness Upper:\t{self.upper_brightness}")
        print(f"Brightness Lower:\t{self.lower_brightness}")
        print("\n")

    def print_formatted(self, title, text=""):
        spaced_title = " " + title + " "
        print("\n")
        print('\033[95m' + spaced_title.center(60, '='))
        print("\n")

        lines = textwrap.wrap(text, width=60)

        for line in lines:
            print(line)
        print("\n")

    def print_error(self, type):
        print("\n")
        print("\033[91m" + "ERROR! Invalid {}. Please try again...".format(type))
        print("\n")

    def calculate_variance_of_laplacian(self, image):
        """
        The function calculates the Laplacian of the source image. It highlights regions of rapid intensity change and is therefore often used for edge detection.
        """
        # CV_64F bc we need a floating point data type for negative values. An unsigned 8-bit integer cannot handle negative values.
        return Laplacian(image, CV_64F).var()

    def is_unsharp(self, gray):
        score = self.calculate_variance_of_laplacian(gray)
        return score < self.threshold

    def is_brightness_bad(self, gray):
        return np.mean(gray) > 240 or np.mean(gray) < 50

    def deleteImages(self):
        # 'list_images' recursively looks through root folder and finds images of all types and returns their paths
        for image_path in paths.list_images(self.root_path):
            file_name = path.basename(image_path)
            img = imread(image_path)
            gray = cvtColor(img, COLOR_BGR2GRAY)

            if self.is_unsharp(gray) and self.is_brightness_bad(gray):
                try:
                    send2trash(image_path)
                    print("Image deleted")
                except FileNotFoundError as error:
                    print(error)
                    sys.exit(1)

        print("Done!")


imageDeleteCLI = ImageDeleteCLI()
imageDeleteCLI.get_input()
imageDeleteCLI.deleteImages()

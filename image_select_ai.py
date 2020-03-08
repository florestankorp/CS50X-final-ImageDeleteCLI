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
- look at more advanced factors other than sharpness and brightness
- build interface with input for root path, porgress bar and options for threshold
- make installable on windows, mac and linux
"""

import os
import sys
from shutil import copy

import numpy as np
from cv2 import COLOR_BGR2GRAY, CV_64F, Laplacian, cvtColor, imread
from imutils import paths


def main():
    """main"""

    root_path = "/media/florestan/BACKUP/FileHistory/Florestan/FLO_MACHINE/Data/E/Pictures/IPHONE"
    trash_path = "./trash/"
    threshold = 25

    def variance_of_laplacian(image):
        """
        The function calculates the Laplacian of the source image. It highlights regions of rapid intensity change and is therefore often used for edge detection.
        """
        # CV_64F bc we need a floating point data type for negative values. An unsigned 8-bit integer cannot handle negative values.
        return Laplacian(image, CV_64F).var()

    def is_unsharp(gray):
        score = variance_of_laplacian(gray)
        return score < threshold

    def is_brightness_bad(gray):
        return np.mean(gray) > 240 or np.mean(gray) < 50
        # loop over the input images

    # list_images recursively looks through root folder and finds images of all types and returns their paths
    for image_path in paths.list_images(root_path):
        file_name = os.path.basename(image_path)
        destination = trash_path + file_name

        img = imread(image_path)
        gray = cvtColor(img, COLOR_BGR2GRAY)

        if is_unsharp(gray) and is_brightness_bad(gray):
            try:
                # TODO: replace copy with move and destination should be trash-bin
                copy(image_path, destination)
                print("Image deleted")
            except FileNotFoundError as error:
                print(error)
                sys.exit(1)


if __name__ == "__main__":
    main()

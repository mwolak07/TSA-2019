import cv2
import numpy as np
import matplotlib.pyplot as plt
from keras.applications.mobilenet_v2 import preprocess_input
import time
import random


def is_white(pixel):
    return pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240


def fill_background(image):
    slice_number = random.randint(0, 2)
    slice_image = cv2.imread("D:/TSA-2019-Dataset/slices/" + str(slice_number) + ".jpg")
    height = image.shape[0]
    width = image.shape[1]
    slice_image_resized = np.array(cv2.resize(slice_image, (width, height)))
    for row in range(len(image)):
        for col in range(len(image[row])):
            if is_white(image[row][col]):
                image[row][col] = slice_image_resized[row][col]
    return image


directory = "D:/TSA-2019-Dataset/"

weapon_type = "handgun"

for i in range(4369):
    image = cv2.imread(directory + weapon_type + "/" + str(i) + ".jpg")
    if image is None:
        continue
    cv2.imwrite("D:/TSA-2019-Dataset-Final/Training/gun/" + weapon_type + str(i) + ".jpg",
                np.array(fill_background(np.array(image))))
    print("saved im")

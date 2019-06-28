import time
import cv2
import numpy as np


# Precondition: target and source are 2D arrays
# Fills target with data from source starting at source indexes in the top left
# Returns filled array
def fill_from_source(target, source, source_row, source_col):
    # Gets size of target window
    target_size = target.shape[0]

    # Creates empty array the same shape as the target
    output = np.empty((target_size, target_size, 3))

    # Iterates over rows and columns of empty array, filling from source
    for window_row in range(target_size):
        for window_col in range(target_size):
            output[window_row][window_col] = source[source_row + window_row][source_col + window_col]

    return output


def slice_up_image(image_path, output_array):
    # Reading in image as np array
    image = np.array(cv2.imread(image_path))

    # Defining max width and height of image
    max_rows = image.shape[0]
    max_cols = image.shape[1]

    # Creates new empty sliding window
    window_size = 200
    step_size = 100
    window = np.empty((window_size, window_size, 3))

    # Iterates through image, tracking top-left of window,
    # and assigns values in window to sliding_output 2D array of images
    # Iterates through rows and columns, ensuring it steps by the defined step size
    # but does not overstep the edges of the image
    # Builds temporary array of window snapshots (rows) and appends these to empty output 2D array
    for row in range(0, max_rows - (window_size - 1), step_size):
        for col in range(0, max_cols - (window_size - 1), step_size):
            output_array.append(np.array(fill_from_source(window, image, row, col)))


directory = "D:/TSA-2019-Dataset/store/"
slices_array = []

print("slicing store images")

low = 0
for i in range(94):
    # skips number if that image is missing
    if cv2.imread(directory + str(i) + ".jpg") is None:
        continue
    slice_up_image(directory + str(i) + ".jpg", slices_array)
    slices_array = slices_array[low:len(slices_array)]
    for n in range(low, len(slices_array)):
        cv2.imwrite("D:/TSA-2019-Dataset/slices/" + str(n) + ".jpg", np.array(slices_array[n]))
    print("finished and image")

directory = "D:/TSA-2019-Dataset/highschool/"

print("slicing high school images")

for i in range(94):
    # skips number if that image is missing
    if cv2.imread(directory + str(i) + ".jpg") is None:
        continue
    slice_up_image(directory + str(i) + ".jpg", slices_array)
    slices_array = slices_array[low:len(slices_array)]
    for n in range(low, len(slices_array)):
        cv2.imwrite("D:/TSA-2019-Dataset/slices/" + str(n) + ".jpg", np.array(slices_array[n]))
    print("finished and image")

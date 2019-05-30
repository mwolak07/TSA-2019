import numpy as np
import cv2
import time


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


def five_to_three_d(five_d_source):
    outer_row_max = five_d_source.shape[0]
    outer_col_max = five_d_source.shape[1]
    inner_row_max = five_d_source.shape[2]
    inner_col_max = five_d_source.shape[3]
    output = np.empty((outer_row_max * inner_row_max, outer_col_max * inner_col_max, 3))
    output_row = 0
    output_col = 0
    for outer_row in range(outer_row_max):
        for inner_row in range(inner_row_max):
            for outer_col in range(outer_col_max):
                for inner_col in range(inner_col_max):
                    output[output_row][output_col][0] = five_d_source[outer_row][outer_col][inner_row][inner_col][0]/255
                    output[output_row][output_col][1] = five_d_source[outer_row][outer_col][inner_row][inner_col][1]/255
                    output[output_row][output_col][2] = five_d_source[outer_row][outer_col][inner_row][inner_col][2]/255
                    output_col += 1
            output_row += 1
            output_col = 0
    return output


# Reading in image as np array
image = np.array(cv2.imread("Images/Test.jpeg"))

# Defining max width and height of image
max_rows = image.shape[0]
max_cols = image.shape[1]

# Creates new empty sliding window
window_size = int(input("Input sliding window size: "))
step_size = int(input("Input sliding window step size: "))
window = np.empty((window_size, window_size, 3))

# Iterates through image, tracking top-left of window, and assigns values in window to sliding_output 2D array of images
start = time.process_time()  # Process timing
temp_array = []
temp_output = []
# Iterates through rows and columns, ensuring it steps by the defined step size
# but does not overstep the edges of the image
# Builds temporary array of window snapshots (rows) and appends these to empty output 2D array
for row in range(0, max_rows - (window_size-1), step_size):
    for col in range(0, max_cols - (window_size-1), step_size):
        temp_array.append(fill_from_source(window, image, row, col))
    temp_output.append(temp_array)
    temp_array = []
sliding_output = np.array(temp_output)
end = time.process_time()  # Process timing

# Stitches snapsots from 5D storage array into a 3D color image array
converted_output = five_to_three_d(sliding_output)

# Shows shape of stitched image
print("Stitched shape: (%s, %s, %s)" % (converted_output.shape[0],
                                        converted_output.shape[1],
                                        converted_output.shape[2]))

# Shows how long sliding window took
print("Time: %s" % (end-start))

# Shows the finished stitched image
cv2.imshow("Image", converted_output)
cv2.waitKey()

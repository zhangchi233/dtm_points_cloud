# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import laspy

import os

path = r"F:\dem1015\assignment4"
os.chdir(path)
file = "C_58EZ1.laz"
las=laspy.read(file)
# it may cost some times
midx,midy = 0.5*(las.header.x_min + las.header.x_max),0.5*las.header.y_min+0.5*las.header.y_max
bound_box =[midx+250,midy+250,midx-250,midy-250]

# crop the file chunck by chunck
header = las.header

with laspy.open(file) as f:
    with laspy.open("somepath.las", mode="w", header=header) as writer:
        for points in f.chunk_iterator(1_000_000):
            x = points.x.copy()
            y = points.y.copy()
            mask = (x <= bound_box[0]) & (x >= bound_box[2]) & (y >= bound_box[3] ) & (y <= bound_box[1])
            if True in mask:
                sub_points=points[mask]
                writer.write_points(sub_points)
                print(mask)


path = r"F:\dem1015\assignment4"
os.chdir(path)
print("start to read")
file = "somepath.las"
las=laspy.read(file)
# it may cost some times
points = list(zip(list(las.x),list(las.y),list(las.z)))

# use pickle to fast read the points information
import pickle
with open("database.txt",'wb') as f:
    pickle.dump(points, f, fix_imports=True, buffer_callback=None)

#use pickle is much faster then directly read laz files
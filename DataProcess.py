import math
import os
import laspy
import numpy as np
def write_to_file(filename,header,data):
    with laspy.open(filename, mode="w", header=header) as writer:
        if type(data) == type([]):
            data= np.array(data)
        print
        point_record = laspy.ScaleAwarePointRecord.zeros(data.shape[0], header=header)
        point_record.x = data[:, 0]
        point_record.y = data[:, 1]
        point_record.z = data[:, 2]
        writer.write_points(point_record)

def thinning(file,data=None,mode="grid",n_random = 10,percentage=0.9,cellsize=1,cell_manipulation='average'):

    if data == None:
        data_thinning = []
        with laspy.open(file) as f:
            for points in f.chunk_iterator(1_000_000):

                x = points.x.copy()
                y = points.y.copy()
                z = points.y.copy()
                data_thinning+=list(zip(x,y,z))
    else:
        import copy
        data_thinning = data.deepcopy()
    if mode == 'random':
        random_size = int(round(len(data_thinning)*percentage,0))
        data_thinning = np.array(data_thinning)
        np.random.seed(101)
        np.random.shuffle(data_thinning)
        data_thinning=data_thinning[:random_size]
    elif mode == 'n_points_random':
        data_n = [data_thinning[n] for n in range(0,len(data_thinning),n_random)]
        data_thinning =np.array(data_n)


    elif mode == 'n_points':
        data_z = []
        start = 0
        for pts in range(0,len(data_thinning),n_random):
            seg = np.array(data_thinning[start:pts])
            np.random.shuffle(seg)
            index = (len(seg)*percentage)//1
            data_z+=list(seg[:index])
        data_thinning = np.array(data_z)

    elif mode == 'grid':

        data_thinning = np.array(data_thinning)
        bounds_x = max(data_thinning[:,0]),min(data_thinning[:,0])
        bounds_y = max(data_thinning[:, 1]), min(data_thinning[:, 1])
        cell_rows = int((bounds_y[0]-bounds_y[1])//cellsize+1)
        cell_cols = int((bounds_x[0] - bounds_x[1]) // cellsize + 1)
        #print(cell_cols,cell_rows)
        data_grid = [[[]]*cell_cols for i in range(cell_rows)]

        for pt in data_thinning:
            x,y,z = pt
            rows = (y-bounds_y[1])//cellsize
            cols = (x-bounds_x[1])//cellsize

            data_grid[int(rows)][int(cols)].append([x,y,z])
        data_new = []
        for row in data_grid:
            for col in row:
                if len(col) == 0:
                    continue
                if cell_manipulation=='average':
                    grid_data = np.array(col)
                    x_average = np.average(grid_data[:,0])
                    y_average = np.average(grid_data[:, 1])
                    z_average = np.average(grid_data[:, 2])
                    data_new.append([x_average,y_average,z_average])

                elif cell_manipulation == 'middle':

                    grid_data = np.array(col)
                    x_mid = np.median(grid_data[:, 0])
                    y_mid = np.median(grid_data[:, 1])
                    z_mid = np.median(grid_data[:, 2])
                    data_new.append([x_mid, y_mid, z_mid])

                elif cell_manipulation == 'min':
                    grid_data = np.array(col)
                    x_min = np.min(grid_data[:, 0])
                    y_min = np.min(grid_data[:, 1])
                    z_min = np.min(grid_data[:, 2])
                    data_new.append([x_min, y_min, z_min])
                elif cell_manipulation == 'max':
                    grid_data = np.array(col)
                    x_max = np.max(grid_data[:, 0])
                    y_max = np.max(grid_data[:, 1])
                    z_max = np.max(grid_data[:, 2])
                    data_new.append([x_max, y_max, z_max])
                elif cell_manipulation == 'random':
                    grid_data = np.array(col)
                    np.random.shuffle(grid_data)
                    grid_data[:n_random]
                    data_new+=list(grid_data)
        data_thinning= data_new






    return data_thinning
if __name__=='__main__':
    d = thinning("somepath.las",mode='grid')




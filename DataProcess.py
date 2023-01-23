import math
import os
import laspy
import numpy as np
def write_to_file(filename,header,data):
    with laspy.open(filename, mode="w", header=header) as writer:
        if type(data) == type([]):
            data= np.array(data)
        point_record = laspy.ScaleAwarePointRecord.zeros(data.shape[0], header=header)
        point_record.x = data[:, 0]
        point_record.y = data[:, 1]
        point_record.z = data[:, 2]
        writer.write_points(point_record)
# write back the particles back to las files
def thinning(file=None,data=None,mode="random",n_random = 10,percentage=0.9,cellsize=1,cell_manipulation='average'):

    if data == None:
        data_thinning = []
        with laspy.open(file) as f:
            for points in f.chunk_iterator(1_000_000):

                x = points.x.copy()
                y = points.y.copy()
                z = points.z.copy()
                data_thinning+=list(zip(x,y,z))


    else:
        import copy
        data_thinning = data.deepcopy()
    if mode == 'random':
        random_size = int(round(len(data_thinning)*percentage,0))
        data_thinning = np.array(data_thinning)
        if random_size == len(data_thinning):
            return data_thinning
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
#do thinning use different method

def interpolation(dt,coordinatex, coordinatey,mode="TIN"): # according to the points use differenct interpolation method to write a dtm
    if mode == "TIN":
        if dt.is_inside_convex_hull(coordinatex, coordinatey) == False:
            return -999999
        else:
            value = dt.interpolate_tin_linear(coordinatex,coordinatey)
            return value
    elif mode == "Nearest":
        if dt.is_inside_convex_hull(coordinatex, coordinatey) == False:
            return -999999
        else:
            value = dt.interpolate_nn(coordinatex,coordinatey)
            return value
    elif mode == "laplace":
        if dt.is_inside_convex_hull(coordinatex, coordinatey) == False:

            return -999999
        else:
            value = dt.interpolate_laplace(coordinatex,coordinatey)
            return value
    elif mode =="NNI":
        if dt.is_inside_convex_hull(coordinatex, coordinatey) == False:
            print('coo')
            return -999999
        else:
            #print("the value is ",dt.is_inside_convex_hull(coordinatex,coordinatey))
            try:
                value = dt.interpolate_nni(coordinatex,coordinatey)
            except:
                return -999999
            return value



# writhe the data as raster file
def write_to_raster(data,driver="GTiff",filename='new.tif',CRS='+proj=sterea +lat_0=52.1561605555556 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.4171,50.3319,465.5524,1.9342,-1.6677,9.1019,4.0725 +units=m +no_defs +type=crs',
                  resolution=0.5,mode="NNI"):
    if type(data) == type([]):
        data = np.array(data)

    xmax = data[:,0].max()
    xmin = data[:,0].min()
    ymax = data[:, 1].max()
    ymin = data[:, 1].min()
    width = int((xmax-xmin)//resolution)+1
    height = int((ymax - ymin) // resolution) + 1
    import rasterio
    from rasterio.transform import Affine
    crs = CRS

    transform =  Affine.translation(xmin - resolution / 2, ymin - resolution / 2) * Affine.scale(resolution, resolution)
    new_dataset = rasterio.open(
        filename,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
        nodata = -999999
    )
    import startinpy
    dt = startinpy.DT()
    dt.snap_tolerance = 0.00001
    dt.insert(data)
    values = np.empty((height,width))
    for row in range(height):
        for col in range(width):
            pixel_x,pixel_y= transform*(col,row)
           # print(dt.is_inside_convex_hull(pixel_x,pixel_y))

           # print(row,col,width)
            value = interpolation(dt,pixel_x,pixel_y,mode=mode)

            values[row][col] = value
    new_dataset.write(values, 1)
    new_dataset.close()














if __name__=='__main__':

    d = thinning("somepath.las",mode='random',percentage=1)

    write_to_raster(d,filename='originl.tif',mode='laplace')
    d = thinning("cfs.laz", mode='random', percentage=0.1)
    #print(d)

    write_to_raster(d, filename="thinning.tif",mode="laplace")
    d = thinning("cfs.laz", mode='random', percentage=1)

    write_to_raster(d, filename='csf_withoutthinning.tif', mode='laplace')



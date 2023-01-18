import os
path = r"F:\dem1015\assignment4"
os.chdir(path)
print("start to read")


# instruction to run the files
# how to get crop the file get the pickle file dumped by xyz points and cropped las file, just see cropping file
# all the following operation just use the pickle file stored the xyz points from original las file

# use pickle to fast read the points information
import pickle
#with open("database.txt",'wb') as f:
    #pickle.dump(points, f, fix_imports=True, buffer_callback=None)

with open("database.txt",'rb') as f:
    particles = pickle.load(f)
print("has read read points")
import points_grid
from points_grid import cloth

#points_grid.draw_3d_points(particles, '^') # u can use this to draw points in 3d scatter using matplotlib
#print("particles is",particles)
# how to run cfs ground filtering
clothes = cloth(particles,cellsize=5,mass=0.1,displacement=10)
without_cfs_points = [[pt.x,pt.y,-pt.originalZ] for row in clothes.Particles for pt in row]
print(without_cfs_points)
print("has start to do cfs")
particle_xyz = clothes.implementation_CSF(0.03)

# check the final resutl
#clothes.draw_particles(show_difference=True) # check the points' shift distance
clothes.draw_particles(show_OriginalZ=True,zmin = -clothes.MinZ,zmax = -clothes.MaxZ) # check original points before ground filtering
points_grid.draw_3d_points(particle_xyz, '^',-clothes.MinZ,-clothes.MaxZ) # see points after ground filtering

# write back the data to laspy
# how to write back the cfs points into a new las file
import DataProcess
import laspy
#DataProcess.write_to_raster(without_cfs_points,filename="before.tif")
file = "somepath.las"
las=laspy.read(file)
header = las.header
DataProcess.write_to_file("cfs.laz",header,particle_xyz)





# how to do thinning to cfs points and and show the raster file of it using different interpolation methods, check Dataprocess
# default method is nni
#default value without thinning

d = DataProcess.thinning("cfs.laz",mode='random',percentage=0.1)
DataProcess.write_to_raster(particle_xyz,filename='cfs_withoutthinning.tif')
DataProcess.write_to_raster(d,filename="thinning.tif")
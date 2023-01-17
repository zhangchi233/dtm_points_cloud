import os
path = r"F:\dem1015\assignment4"
os.chdir(path)
print("start to read")


# use pickle to fast read the points information
import pickle
#with open("database.txt",'wb') as f:
    #pickle.dump(points, f, fix_imports=True, buffer_callback=None)

with open("database.txt",'rb') as f:
    particles = pickle.load(f)
print("has read read points")
import points_grid
from points_grid import cloth

#points_grid.draw_3d_points(particles, '^')
clothes = cloth(particles,cellsize=5,mass= 2,displacement=3)
print("has start to do cfs")
particle_xyz = clothes.implementation_CSF(0.03)
#clothes.draw_particles(show_difference=True,zmin = -clothes.MinZ,zmax = -clothes.MaxZ)
clothes.draw_particles(show_OriginalZ=True,zmin = -clothes.MinZ,zmax = -clothes.MaxZ)
points_grid.draw_3d_points(particle_xyz, '^',-clothes.MinZ,-clothes.MaxZ)

# write back the data to laspy
import DataProcess
import laspy
file = "somepath.las"
las=laspy.read(file)
header = las.header
DataProcess.write_to_file("cfs.laz",header,particle_xyz)
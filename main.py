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

points_grid.draw_3d_points(particles, '^')
clothes = cloth(particles)

particle_xyz = clothes.implementation_CSF(0.03)
points_grid.draw_3d_points(particle_xyz, '^')
# remeber to generate database.txt
import numpy as np
from scipy.spatial import KDTree


class Point: # a base class to define the points
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def __mul__(self, other): # if u want to convert point to upside down u will need it
        #new_x = self.x * other
        #new_y = self.y * other
        new_z =  self.z * other
        return Point(self.x,self.y,new_z)



class Particle(Point): # particle used for cloth simulation filtering algorithm,
    def __init__(self,x,y,z,displacement,mass,originalZ,outer=False):
        super().__init__(x,y,z)
        self.displacement = displacement # how internal forces
        self.moveable = True # define whether move or not
        self.gravity = -1*mass # define the gravity of each particle
        self.movedirection = self.gravity # initial moving vector for each particle
        self.delta_z = self.movedirection # how long has the particle move now
        self.originalZ = originalZ # the starting points of particles
        self.Outer = outer # whether the point is out or boundary of delaunay triangular of the interpolated points
    def update(self,others):
        # it is very risky to pull downwards, since if we adjust the displacement to tight, it is possible that the points pulled below originZ
        # as a result, making it failed to cover the buildings
        # the way to solve it is to limit the maximum downward vector, what about this, at most averge difference of 4 neighbor points?
        # at most 4 times of gravity?

        if self.moveable:
            vector = 0
            average_height = 0
            length = 0
            for particle in others:
                if self.Outer:
                    continue
                average_height+=particle.z
                length+=1
            average_height/=length
            difference= (average_height-self.z)
            vector = difference*self.displacement
            if vector<0 and vector <difference:
                vector = difference
            elif vector >0 and vector>difference:
                vector = difference



            self.movedirection = self.gravity+vector
        else:
            self.movedirection=0
    def shift(self):
        # make particles change its position
        self.z+=self.movedirection
        self.delta_z = abs(self.movedirection)
        if self.z<=self.originalZ:

            self.delta_z -= abs(self.originalZ-self.z)
            self.z = self.originalZ
            self.moveable =False
            self.movedirection = 0





class cloth:
    def __init__(self,Points,interpolation="TIN",cellsize = 5,displacement=1,mass=1):

        if type(Points) == type([]):
            Points = np.array(Points)

        Points *= [1,1,-1]
        #self.Points = (Points)
        self.MinZ = max(Points[:,2])
        self.MaxZ = min(Points[:, 2])
        self.bounds = [min(Points[:,0]),max(Points[:,0]),min(Points[:,1]),max(Points[:,1])] # define bounding box
        self.xv = np.arange(self.bounds[0],self.bounds[1]+cellsize,cellsize)
        self.yv = np.arange(self.bounds[2], self.bounds[3]+cellsize, cellsize)
        self.Xvertex, self.Yvertex = np.meshgrid(self.xv,self.yv)
        self.displacement = displacement
        self.mass = mass
        # form the cloth
        if interpolation =="TIN":
            import startinpy
            dt = startinpy.DT()
            dt.snap_tolerance = 0.01
            for pt in Points:
                x,y,z = pt
                dt.insert_one_pt(x,y,z)

            self.interpolation=dt

        Particles = []
        Yshape,Xshape= self.Xvertex.shape
        for i in range(Yshape):
            OneRow =[]
            for t in range(Xshape):
                x,y = self.Xvertex[i][t],self.Yvertex[i][t]

                outer = False
                if interpolation=='TIN':
                    if not self.interpolation.is_inside_convex_hull(x, y):
                        originalZ = self.MinZ # dont interact into calculation
                        outer = True



                    else:

                        originalZ = self.interpolation.interpolate_tin_linear(x,y)

                particle = Particle(x,y,self.MinZ,displacement,mass,originalZ,outer)
                OneRow.append(particle)
            Particles.append(OneRow)
        self.Particles = Particles

    def draw_particles(self,show_OriginalZ = False,zmin=None,zmax=None,show_difference=False):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        if show_OriginalZ== False and show_difference==False: # show the z value of points after csf
            xs, ys, zs = zip(*[[pt.x,pt.y,pt.z] for row in self.Particles for pt in row])
            ax.scatter(xs, ys, zs, marker='o')
        elif show_OriginalZ: # show the original z value of points before csf
            xs, ys, zs = zip(*[[pt.x,pt.y,-pt.originalZ] for row in self.Particles for pt in row])
            ax.scatter(xs, ys, zs, marker='^')
        elif show_difference: # show change of z value

            xs, ys, zs = zip(*[[pt.x, pt.y, -pt.z+pt.originalZ] for row in self.Particles for pt in row])
            ax.scatter(xs, ys, zs, marker='^')
        ax.set_zlim(zmin,zmax)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        plt.show()

    def getNeighbors(self):
        '''
        self.KDtree = QueryTree(self.Particles)
        neighborpoints = []
        for row in self.Particles:
            row_neightbors = []
            for particle in row:

                x, y = particle.x, particle.y
                neighborindex = self.KDtree.QueryNeightbors(x, y)
                row_neightbors.append(neighborindex)
            neighborpoints.append(row_neightbors)

        self.neighborpoints = neighborpoints
        '''
        # find the near points for points on the cloth
        neighborpoints = []
        for i in range(len(self.Particles)):
            row_neightbors = []
            for t in range(len(self.Particles[i])):
                pt = self.Particles[i][t]
                neighborindex=[]
                if i+1<len(self.Particles) and self.Particles[i+1][t].Outer==False :
                    neighborindex.append((i+1)*len(self.Particles[i])+t)

                if  i - 1 >=0 and self.Particles[i -1][t].Outer == False:
                    neighborindex.append((i - 1) * len(self.Particles[i]) + t)
                if t+1<len(self.Particles[i]) and self.Particles[i][t+1].Outer==False:
                    neighborindex.append((i)*len(self.Particles[i])+t+1)
                if t-1>=0 and self.Particles[i][t-1].Outer==False:
                    neighborindex.append((i)*len(self.Particles[i])+t-1)
                row_neightbors.append(neighborindex)
            neighborpoints.append(row_neightbors)

        self.neighborpoints = neighborpoints
    # all points move once
    def do_one_movement(self):  # they must be the same order
        max_deltaZ = 0
        # shift once
        for pt in range(len(self.Particles)):
            for particle in self.Particles[pt]:

                particle.shift()
        

        # update the move vector combining internal and external forces
        row_len = len(self.Particles[0])
        for pt in range(len(self.Particles)):
            for part in range(len(self.Particles[pt])):
                particle = self.Particles[pt][part]
                NearestPointsindex = self.neighborpoints[pt][part]


                neighbors = [self.Particles[index//row_len][index%row_len] for index in NearestPointsindex]
                particle.update(neighbors)

                if particle.delta_z>=max_deltaZ:
                    max_deltaZ = particle.delta_z
        #self.draw_particles()

        return max_deltaZ

    def implementation_CSF(self, threhold):  # a list of points


        self.getNeighbors()
        # generate the relation between each particles and its neightbors

        delta_z = self.Particles[0][0].delta_z
        threhold =  threhold
        i= 0
        while True:
            # all points move once until all points' change within tolerance
            delta_z = self.do_one_movement()

            i += 1
            print(delta_z, i)


            if delta_z <= threhold:


                break
        # return new x,y,z position of cloth
        particle_xyz = [[particle.x,particle.y,-particle.z] for row in self.Particles for particle in row]
        return particle_xyz

        




class QueryTree(KDTree): # useless, will cause error, it aims to find the near points that exert internal force to each other
    def __init__(self,points):
        Points = []
        if type(points[0][0]) == type(Particle(1,1,1,1,1,1,1)):
            for row in points:

                for particle in row:
                    if particle.Outer != False:
                        Points.append([particle.x,particle.y])
        else:
            Points = points[:,:2]



        super().__init__(Points)
    def QueryNeightbors(self,x,y):
        point = np.array([x,y])
        _,i = self.query(point,k = [2,3,4,5])
        return i.ravel()
    def QueryZ(self,x,y,pts):
        point = np.array([x, y])
        _, i = self.query(point, k=1)

        if type(pts[0]) == type(Point(1,1,1)):
            Z = pts[i].z


        else:

            Z = pts[i][2]



        return Z
def draw_3d_points(Points,marker,zmin,zmax): # to visualize the points' position
    import matplotlib.pyplot as plt
    xs =[]
    ys = []
    zs = []
    for pt in Points:
        if type(pt) == type(Point(1,1,1)) or type(pt) == type(Particle(1,1,1,1,1,1,1)):
            xs.append(pt.x)
            ys.append(pt.y)
            zs.append(pt.z)
        else:
            xs.append(pt[0])
            ys.append(pt[1])
            zs.append(pt[2])
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    #xs, ys, zs = zip(*particles)
    ax.scatter(xs, ys, zs, marker=marker)
    ax.set_zlim(zmin,zmax)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()
   


# implementation of cloth simulation filter algorithm





if __name__ == "__main__":
    
    from generate_random import particles

    draw_3d_points(particles, '^')
    clothes = cloth(particles)
    print("start to do cfs")
    particle_xyz = clothes.implementation_CSF(0.03)
    clothes.draw_particles(show_difference=True)
    draw_3d_points(particle_xyz, '^')
    #test particle

    #test_particle = Particle(1,1,1,0.4,1,-1)
    #neighbors = [Particle(0,1,-2,0.4,1,-5),Particle(1,2,-2,0.4,1,-5),Particle(1,0,-2,0.4,1,-5),Particle(2,1,-2,0.4,1,-5)]
    #test_particle.shift()
    #test_particle.update(neighbors)
    #print(test_particle.z)
    #print(test_particle.movedirection)
    # noproblem
    # test and store the cropping laz file's csf into a new laz file
    with open("database.txt",'rb') as f:
        particles = pickle.load(f)
        print("has read read points")


    #points_grid.draw_3d_points(particles, '^') # u can use this to draw points in 3d scatter using matplotlib
    #print("particles is",particles)
    # how to run cfs ground filtering
    clothes = cloth(particles,cellsize=5,mass=0.1,displacement=10)
    without_cfs_points = [[pt.x,pt.y,-pt.originalZ] for row in clothes.Particles for pt in row]
    print(without_cfs_points)
    print("has start to do cfs")
    particle_xyz = clothes.implementation_CSF(0.03)

    # check the final resutl
    clothes.draw_particles(show_difference=True) # check the points' shift distance
    clothes.draw_particles(show_OriginalZ=True,zmin = -clothes.MinZ,zmax = -clothes.MaxZ) # check original points before ground filtering
    draw_3d_points(particle_xyz, '^',-clothes.MinZ,-clothes.MaxZ) # see points after ground filtering

    # write back the data to laspy
    # how to write back the cfs points into a new las file
    import DataProcess
    import laspy
    #DataProcess.write_to_raster(without_cfs_points,filename="before.tif")
    file = "somepath.las"
    las=laspy.read(file)
    header = las.header
    # write the result after csf into laz file
    DataProcess.write_to_file("cfs.laz",header,particle_xyz)


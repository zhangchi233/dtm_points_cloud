import numpy as np
from scipy.spatial import KDTree

class Point:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def __mul__(self, other):
        #new_x = self.x * other
        #new_y = self.y * other
        new_z =  self.z * other
        return Point(self.x,self.y,new_z)



class Particle(Point):
    def __init__(self,x,y,z,displacement,mass,originalZ,outer=False):
        super().__init__(x,y,z)
        self.displacement = displacement
        self.moveable = True
        self.gravity = -1*mass
        self.movedirection = self.gravity
        self.delta_z = self.movedirection
        self.originalZ = originalZ
        self.Outer = outer
    def update(self,others):
        if self.moveable:
            vector = 0
            for particle in others:
                if self.Outer:
                    continue

                vector += (particle.z-self.z)*self.displacement
            self.movedirection = self.gravity+vector
        else:
            self.movedirection=0
    def shift(self):

        self.z+=self.movedirection
        self.delta_z = abs(self.movedirection)
        if self.z<=self.originalZ:

            self.delta_z -= abs(self.originalZ-self.z)
            self.z = self.originalZ
            self.moveable =False
            self.movedirection = 0





class cloth:
    def __init__(self,Points,interpolation="TIN",cellsize = 5,displacement=0.4,mass=1):
        if type(Points) == type([]):
            Points = np.array(Points)
        Points *= [1,1,-1]
        #self.Points = (Points)
        self.MinZ = max(Points[:,2])
        self.bounds = [min(Points[:,0]),max(Points[:,0]),min(Points[:,1]),max(Points[:,1])] # define bounding box
        self.xv = np.arange(self.bounds[0],self.bounds[1]+cellsize,cellsize)
        self.yv = np.arange(self.bounds[2], self.bounds[3]+cellsize, cellsize)
        self.Xvertex, self.Yvertex = np.meshgrid(self.xv,self.yv)
        self.displacement = displacement
        self.mass = mass

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

    def draw_particles(self,show_OriginalZ = False):
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        xs, ys, zs = zip(*[[pt.x,pt.y,pt.z] for row in self.Particles for pt in row])
        ax.scatter(xs, ys, zs, marker='o')
        if show_OriginalZ:
            zo = [[pt.originalZ] for row in self.Particles for pt in row]
            ax.scatter(xs, ys, zo, marker='^')

        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        plt.show()

    def getNeighbors(self):
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

        return max_deltaZ

    def implementation_CSF(self, threhold):  # a list of points


        self.getNeighbors()
        # generate the relation between each particles and its neightbors

        delta_z = self.Particles[0][0].delta_z
        threhold = self.mass * threhold
        while True:

            delta_z = self.do_one_movement()

            if delta_z <= threhold:

                break
        particle_xyz = [[particle.x,particle.y,-particle.z] for row in self.Particles for particle in row]
        return particle_xyz

        




class QueryTree(KDTree):
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
def draw_3d_points(Points,marker):
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
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()
   


# implementation of cloth simulation filter algorithm





if __name__ == "__main__":
    from generate_random import particles

    draw_3d_points(particles, '^')
    clothes = cloth(particles)

    particle_xyz = clothes.implementation_CSF(0.03)
    draw_3d_points(particle_xyz, '^')
    #test particle

    #test_particle = Particle(1,1,1,0.4,1,-1)
    #neighbors = [Particle(0,1,-2,0.4,1,-5),Particle(1,2,-2,0.4,1,-5),Particle(1,0,-2,0.4,1,-5),Particle(2,1,-2,0.4,1,-5)]
    #test_particle.shift()
    #test_particle.update(neighbors)
    #print(test_particle.z)
    #print(test_particle.movedirection)
    # noproblem



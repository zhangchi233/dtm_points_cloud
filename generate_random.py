# i use it to generate random points for testing

import numpy as np
np.random.seed(101)
y = np.random.randint([1,1,1],[100,100,2],(15,3))
y = np.vstack((y,np.array([101,101,2000])))
indices = np.unique(y[:,:2],return_index=True,axis=0)[1]

Y = y[indices]




random_Z = np.random.permutation(y)
Z = random_Z[:5]
buildings = [    ]
for pt in Z:
    x,y,z = pt
    for i in range(3):
        for t in range(3):
            for l in range(10):
                buildings.append([x+i,y+t,l*100+z])
buildings = np.array(buildings)

particles = np.vstack((random_Z[5:],buildings))

if __name__=='__main__':
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    xs,ys,zs = zip(*particles)
    ax.scatter(xs, ys, zs, marker='o')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()

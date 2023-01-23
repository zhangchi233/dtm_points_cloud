import numpy as np
import matplotlib.pyplot as plt
import rasterio
class Segment:
    def __init__(self,endx,endy,startx,starty,cellindex,neighborcells,shape):
        self.endx = endx
        self.endy = endy
        self.startx = startx
        self.starty = starty
        self.cellindex = cellindex
        self.neighborcells = neighborcells
        self.connected = len(self.neighborcells)
        for i in neighborcells:
            k,z = i
            if k <0 or z<0 or k>=shape[0]-1 or z>= shape[1]-1:
                self.connected-=1
    def findnext(self,x,y,snap=0.0001):
        if self.startx!= None and abs(self.startx - x)<snap and abs(self.starty -y) < snap:
            X = self.startx
            Y = self.starty
            self.startx = None
            self.starty = None
            return True, [X,Y]

        elif  self.endx!= None and abs(self.endx - x) <snap and abs(self.endy - y) < snap:
            X = self.endx
            Y = self.endy
            self.endx = None
            self.endy = None
            return True, [X,Y]
        else:
            return False, None

def startcontour(segments,snap=0.0001):
    contour_line = []
    seg = segments[0]
    previous_length = len(segments)
    # given the segments of a level, make sure segments are connected to each other
    while segments:

        ring = []
        if seg.startx == None:
            # in case some self intersection scenario as a result of infinite loop
            #print(len(segments))
            segments.remove(seg)
            seg = segments[0]
            continue
        ring.append([seg.startx,seg.starty])
        nextx = seg.endx
        nexty = seg.endy
        #ring = recursive_seg(segments,nextx,nexty,ring,seg)

        ring = another_seg(segments,nextx,nexty,ring,seg,snap=snap)
        #ring = brutal_seg(segments,nextx,nexty,ring,seg,snap = snap)
        contour_line.append(ring)

        if len(segments) == 0:
            break

        seg = segments[0]
    return contour_line

def another_seg(segments,nextx,nexty,ring,seg,snap):
    segment = ring
    if nextx == None and nexty == None:
        return segment
    else:
        while True:
            segment.append((nextx,nexty))
            neighbors = seg.neighborcells
            newx = None
            newy = None
            newseg = None
            segments.remove(seg)
            for index in neighbors:
                for line in segments:

                    if line.connected <= 0:
                        continue

                    if line.cellindex == index:
                        whether, pt = line.findnext(nextx, nexty,snap)
                        if whether:
                            seg.connected -= 1
                            line.connected -= 1
                            if line.startx != None:
                                newx = line.startx
                                newy = line.starty
                                # segment.append((newx,newy))
                                newseg = line
                                break
                            elif line.endx != None:
                                newx = line.endx
                                newy = line.endy
                                # segment.append((newx, newy))
                                newseg = line
                                break
            if newx == None and newy==None:
                break
            seg = newseg
            if seg == None:
                return segment
            nextx = newx
            nexty = newy
        return segment

def brutal_seg(segments,nextx,nexty,ring,seg,snap =0.0001):
    segment = ring
    if nextx == None and nexty == None:
        return segment
    else:
        while True:
            if nextx == None and nexty == None:

                continue

            segment.append((nextx,nexty))
            neighbors = seg.neighborcells
            newx = None
            newy = None
            newseg = seg
            segments.remove(seg)

            for line in segments:

                if line.connected <= 0:
                    continue

                whether, pt = line.findnext(nextx, nexty,snap)
                if whether:
                    seg.connected -= 1
                    line.connected -= 1
                    if line.startx != None:
                        newx = line.startx
                        newy = line.starty
                        #segment.append((newx,newy))
                        newseg = line
                        break
                    elif line.endx != None:
                        newx = line.endx
                        newy = line.endy
                        #segment.append((newx, newy))
                        newseg = line
                        break
            if newx == None and newy == None:
                break
            seg = newseg
            nextx = newx
            nexty = newy
        return segment


def recursive_seg(segments,nextx,nexty,ring,seg):
    segment = ring
    if nextx == None and nexty == None:
        return segment
    else:
        segment.append((nextx,nexty))
        neighbors = seg.neighborcells
        newx = None
        newy = None
        newseg = seg
        segments.remove(seg)
        for index in neighbors:
            for line in segments:

                if line.connected <= 0:
                    continue

                if line.cellindex == index:
                    whether,pt = line.findnext(nextx,nexty)
                    if whether:
                        seg.connected -= 1
                        line.connected -= 1
                        if line.startx != None:
                            newx = line.startx
                            newy = line.starty
                            #segment.append((newx,newy))
                            newseg = line
                            break
                        elif line.endx != None:
                            newx = line.endx
                            newy = line.endy
                            #segment.append((newx, newy))
                            newseg = line
                            break
        segment = recursive_seg(segments,newx,newy,segment,newseg)
        return segment

def extract_contour(data,levels,snap = 0.0001):
    # Create the 2D grid
    x = np.linspace(0,data.shape[1],data.shape[1])
    y = np.linspace(0, data.shape[0], data.shape[0])
    X, Y = np.meshgrid(x, y)
    # Initialize the contour lines list
    contours = []

    # Iterate over the contour levels
    for level in levels:
        # Initialize the contour line
        contour_segments = []

        # Iterate over the grid cells
        for i in range(data.shape[0]-1):
            for j in range(data.shape[1]-1):
                # Get the cell vertices values
                vals = data[i:i + 2, j:j + 2]

                # Check the cell type
                cell_type = (vals >= level).sum()


                if cell_type == 0:
                    continue
                else:

                    points = []
                    for k in range(4):
                        if k == 0:
                            if (vals[0,0]-level)*(vals[0,1]-level)>0:
                                continue
                            elif (vals[0, 1] - level) == 0:

                                if vals[0, 0] - level == 0:
                                    points.append((X[i, j], Y[i, j]))
                                continue

                            x1 = X[i,j]
                            x2 = X[i,j+1]
                            y1 = Y[i,j]
                            y2 = Y[i,j+1]
                            point_y = y2
                            point_x = x1+((level-vals[0,0])/(vals[0,1]-vals[0,0]))*(x2-x1)
                            points.append((point_x,point_y))
                        elif k == 1:
                            if (vals[0,1]-level)*(vals[1,1]-level)>0:
                                continue
                            elif (vals[1,1]-level) == 0:

                                if vals[0,1]-level == 0:
                                    points.append((X[i,j+1],Y[i,j+1]))
                                continue
                            x1 = X[i, j+1]
                            x2 = X[i+1, j + 1]
                            y1 = Y[i, j+1]
                            y2 = Y[i+1, j + 1]
                            point_x = x2
                            point_y = y1 + ((level - vals[0, 1]) / (vals[1, 1] - vals[0, 1])) * (y2 - y1)
                            if (point_x,point_y) not in points:
                                points.append((point_x, point_y))
                        elif k == 2:
                            if (vals[1,1]-level)*(vals[1,0]-level)>0:
                                continue
                            elif (vals[1,0]-level) == 0:
                                if (vals[1,1]-level) == 0:
                                    points.append((X[i+1,j+1],Y[i+1,j+1]))
                                continue
                            x1 = X[i, j]
                            x2 = X[i + 1, j + 1]
                            y1 = Y[i, j + 1]
                            y2 = Y[i + 1, j + 1]
                            point_y = y2
                            point_x = x1+((level-vals[1,0])/(vals[1,1]-vals[1,0]))*(x2-x1)
                            if (point_x,point_y) not in points:
                                points.append((point_x, point_y))

                        elif k == 3:
                            if(vals[1,0]-level)*(vals[0,0]-level)>0:
                                continue
                            elif (vals[0,0]-level) == 0:
                                if (vals[1,0]-level) == 0:
                                    points.append((X[i+1,j],Y[i+1,j]))
                                continue
                            x1 = X[i, j ]
                            x2 = X[i + 1, j + 1]
                            y1 = Y[i, j + 1]
                            y2 = Y[i + 1, j + 1]
                            point_x = x1
                            point_y = y1+((level-vals[0,0])/(vals[1,0]-vals[0,0]))*(y2-y1)
                            if (point_x, point_y) not in points:
                                points.append((point_x, point_y))

                    if len(points)==1:
                        point_x,point_y = points[0]
                        x1, x2 = X[i, j], X[i, j + 1]
                        y1, y2 = Y[i, j], Y[i + 1, j + 1]
                        neighbors = []
                        if point_y == y1:
                            neighbors.append((i-1,j))
                        elif point_y == y2:
                            neighbors.append((i+1,j))
                        if point_x == x1:
                            neighbors.append((i,j-1))
                        elif point_x == x2:
                            neighbors.append((i,j+1))
                        contour_segments.append(Segment(endx=point_x,endy=point_y,startx=point_x,starty=point_y,cellindex=(i,j),
                                                        neighborcells=neighbors,shape = data.shape))
                    elif len(points) ==2:
                        x1,x2 = X[i,j],X[i,j+1]
                        y1,y2 = Y[i, j], Y[i+1, j + 1]
                        neighbors = []
                        point_x1,point_y1 = points[0]
                        if point_y1 == y1:
                            neighbors.append((i-1,j))
                        elif point_y1 == y2:
                            neighbors.append((i+1,j))
                        if point_x1 == x1:
                            neighbors.append((i,j-1))
                        elif point_x1 == x2:
                            neighbors.append((i,j+1))
                        point_x2, point_y2 = points[1]
                        if point_y2 == y1:
                            neighbors.append((i-1,j))
                        elif point_y2 == y2:
                            neighbors.append((i+1,j))
                        if point_x2 == x1:
                            neighbors.append((i,j-1))
                        elif point_x2 == x2:
                            neighbors.append((i,j+1))
                        contour_segments.append(
                            Segment(endx=point_x1, endy=point_y1, startx=point_x2, starty=point_y2, cellindex=(i, j),
                                    neighborcells=neighbors,shape = data.shape))

                    elif len(points) ==3:
                        x1, x2 = X[i, j], X[i, j + 1]
                        y1, y2 = Y[i, j], Y[i + 1, j + 1]
                        point_x1, point_y1 = points[0]
                        point_x2, point_y2 = points[1]
                        point_x3, point_y3 = points[2]
                        neighbors1=[]
                        if point_y1 == y1:
                            neighbors1.append((i-1,j))
                        elif point_y1 == y2:
                            neighbors1.append((i+1,j))
                        if point_x1 == x1:
                            neighbors1.append((i,j-1))
                        elif point_x1 == x2:
                            neighbors1.append((i,j+1))
                        contour_segments.append(
                            Segment(endx=point_x1, endy=point_y1, startx=point_x2, starty=point_y2, cellindex=(i, j),
                                    neighborcells=neighbors1,shape = data.shape))
                        neighbors2 = []
                        if point_y3 == y1:
                            neighbors2.append((i - 1, j))
                        elif point_y3 == y2:
                            neighbors2.append((i + 1, j))
                        if point_x3 == x1:
                            neighbors2.append((i, j - 1))
                        elif point_x3 == x2:
                            neighbors2.append((i, j + 1))
                        contour_segments.append(
                    Segment(endx=point_x2, endy=point_y2, startx=point_x3, starty=point_y3, cellindex=(i, j),
                            neighborcells=neighbors2,shape = data.shape))
                    elif len(points) == 4:
                        continue
                        x1, x2 = X[i, j], X[i, j + 1]
                        y1, y2 = Y[i, j], Y[i + 1, j + 1]
                        point_x1, point_y1 = points[0]

                        point_x2, point_y2 = points[1]
                        point_x3, point_y3 = points[2]
                        point_x4, point_y4 = points[3]
                        neighbors1 = []
                        if point_y4 == y1:
                            neighbors1.append((i - 1, j))
                        elif point_y4 == y2:
                            neighbors1.append((i + 1, j))
                        if point_x4 == x1:
                            neighbors1.append((i, j - 1))
                        elif point_x4 == x2:
                            neighbors1.append((i, j + 1))
                        if point_y1 == y1:
                            neighbors1.append((i - 1, j))
                        elif point_y1 == y2:
                            neighbors1.append((i + 1, j))
                        if point_x1 == x1:
                            neighbors1.append((i, j - 1))
                        elif point_x1 == x2:
                            neighbors1.append((i, j + 1))


                        contour_segments.append(
                    Segment(endx=point_x1, endy=point_y1, startx=point_x4, starty=point_y4, cellindex=(i, j),\
                            neighborcells=neighbors1,shape = data.shape))
                        neighbors2 = []
                        if point_y2 == y1:
                            neighbors2.append((i - 1, j))
                        elif point_y2 == y2:
                            neighbors2.append((i + 1, j))
                        if point_x2 == x1:
                            neighbors2.append((i, j - 1))
                        elif point_x2 == x2:
                            neighbors2.append((i, j + 1))
                        if point_y3 == y1:
                            neighbors2.append((i - 1, j))
                        elif point_y3== y2:
                            neighbors2.append((i + 1, j))
                        if point_x3 == x1:
                            neighbors1.append((i, j - 1))
                        elif point_x3 == x2:
                            neighbors2.append((i, j + 1))
                        contour_segments.append(
                            Segment(endx=point_x2, endy=point_y2, startx=point_x3, starty=point_y3, cellindex=(i, j),
                                    neighborcells=neighbors2,shape = data.shape))
        # Append the contour line to the list
        contour_line= startcontour(contour_segments,snap)

        contours.append(contour_line)
    return contours

    # Plot the contour lines
def write_to_wkt(filename,band,levels,output,snap=0.001):
    dataset = rasterio.open(filename)
    band1 = dataset.read(band)
    data = band1
    contour_lines=extract_contour(data,levels,snap)


    f = open(output, "w")
    for contour, level in zip(contour_lines, levels):
        label = str(level)
        for ring in contour:

            # x, y = zip(*ring)

            f.write("LINESTRING(")
            for point in ring:
                x1,y1 = dataset.transform*(point[0],point[1])
                f.write(str(x1) + " " + str(y1) + ",")
                # f.seek(-1, 2)
                # f.truncate()

            f.write(")")
            f.write(";{}\n".format(label))
    f.close()
''' elif cell_type == 1:
                    for k, val in enumerate(vals.flatten()):
                        if val >= level:
                            if k == 0:
                                x1, y1 = X[i, j], Y[i, j]
                                x2, y2 = X[i + 1, j], Y[i, j + 1]
                                if val == level:
                                    one_line = Segment(x1, y1, x1,y1, cellindex=(i, j),
                                                       neighborcells=[(i - 1, j), (i, j - 1)])
                                else:
                                    startx,starty = x1 + (level - val) / (vals[k, 1] - val) * (x2 - x1),y1
                                    endx,endy =x1, y1 + (level - val) / (vals[k+1, k] - val) * (y2 - y1)
                                    one_line = Segment(endx,endy,startx,starty,cellindex=(i,j),neighborcells=[(i-1,j),(i,j-1)])
                                    contour_segments.append(one_line)
                            if k == 1:
                                x1, y1 = X[i, j+1], Y[i, j+1]
                                x2, y2 = X[i, j], Y[i+1, j+1]
                                if val == level:
                                    one_line = Segment(x1, y1, x1,y1, cellindex=(i, j),
                                                       neighborcells=[(i - 1, j), (i, j - 1)])
                                else:
                                    startx,starty = x1 + (level - val) / (vals[k, 1] - val) * (x2 - x1),y1
                                    endx,endy =x1, y1 + (level - val) / (vals[k+1, k] - val) * (y2 - y1)
                                    one_line = Segment(endx,endy,startx,starty,cellindex=(i,j),neighborcells=[(i-1,j),(i,j-1)])
                                    contour_segments.append(one_line)
                            if k == 2:
                                x1, y1 = X[i+1, j ], Y[i+1, j]
                                x2, y2 = X[i+1, j+1], Y[i, j]
                                if val == level:
                                    one_line = Segment(x1, y1, x1,y1, cellindex=(i, j),
                                                       neighborcells=[(i - 1, j), (i, j - 1)])
                                else:
                                    startx,starty = x1 + (level - val) / (vals[k, 1] - val) * (x2 - x1),y1
                                    endx,endy =x1, y1 + (level - val) / (vals[k+1, k] - val) * (y2 - y1)
                                    one_line = Segment(endx,endy,startx,starty,cellindex=(i,j),neighborcells=[(i-1,j),(i,j-1)])
                                    contour_segments.append(one_line)
                            if k == 3:
                                x1, y1 = X[i + 1, j+1], Y[i + 1, j+1]
                                x2, y2 = X[i +1, j], Y[i, j+1]
                                if val == level:
                                    one_line = Segment(x1, y1, x1,y1, cellindex=(i, j),
                                                       neighborcells=[(i - 1, j), (i, j - 1)])
                                else:
                                    startx,starty = x1 + (level - val) / (vals[k, 1] - val) * (x2 - x1),y1
                                    endx,endy =x1, y1 + (level - val) / (vals[k+1, k] - val) * (y2 - y1)
                                    one_line = Segment(endx,endy,startx,starty,cellindex=(i,j),neighborcells=[(i-1,j),(i,j-1)])
                                    contour_segments.append(one_line)
                elif cell_type == 2:
                    k1 = None
                    k2 = None
                    for k, val in enumerate(vals.flatten()):
                        if val >= level:
                            if k1 == None:
                                k1 = k
                            else:
                                k2 = k
                    if abs(k1-k2) == 2:
                        if k1 == 0:
                            x1 = X[i,j]
                            x2 = X[i,j+1]
                            y1 = X[i,j]
                            y2 = X[i+1,j]
                            startx, starty = x1 + (level - vals[0,0]) / (vals[0, 1] - vals[0,0]) * (x2 - x1), y1
                            endx, endy = x1+ (level - vals[1,0]) / (vals[1, 1] - vals[1,0]) * (x2 - x1), y2
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i - 1, j), (i+1, j)])
                            contour_segments.append(one_line)
                        elif k1 == 1:
                            x1 = X[i, j+1]
                            x2 = X[i, j]
                            y1 = X[i, j]
                            y2 = X[i + 1, j]
                            startx, starty = x1 + (level - vals[0,1]) / (vals[0, 0] - vals[0,1]) * (x2 - x1), y1
                            endx, endy = x1 + (level - vals[1,1]) / (vals[1, 0] - vals[1,1]) * (x2 - x1), y2
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i - 1, j), (i+1, j)])
                            contour_segments.append(one_line)
                    elif abs(k1-k2) == 1:
                        if k1 == 0:
                            x1 = X[i,j]
                            x2 = X[i,j+1]
                            y1 = X[i, j]
                            y2 = X[i + 1, j]
                            startx, starty = x1, y1+ (level - vals[0, 0]) / (vals[1, 0] - vals[0, 0]) * (y2 - y1)
                            endx, endy = x2, y1+ (level - vals[0, 1]) / (vals[1, 1] - vals[0, 1]) * (y2 - y1)
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i - 1, j), (i + 1, j)])
                            contour_segments.append(one_line)

                        elif k1 == 1:
                            x1 = X[i, j]
                            x2 = X[i, j + 1]
                            y1 = X[i, j]
                            y2 = X[i + 1, j]
                            startx, starty = x1+ (level - vals[0, 1]) / (vals[0, 0] - vals[0, 1]) * (x2 - x1), y1
                            endx, endy = x2, y1 + (level - vals[1, 0]) / (vals[0, 0] - vals[1, 0]) * (y2 - y1)
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i - 1, j), (i, j-1)])
                            contour_segments.append(one_line)
                            startx, starty = x1, y1 + (level - vals[0, 1]) / (vals[1, 1] - vals[0, 1]) * (y2 - y1)
                            endx, endy = x2+ (level - vals[1, 0]) / (vals[1, 1] - vals[1, 0]) * (x2 - x1), y2
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i, j+1), (i +1, j)])
                            contour_segments.append(one_line)

                        elif k1 == 2:
                            x1 = X[i, j]
                            x2 = X[i, j + 1]
                            y2 = X[i, j]
                            y1 = X[i + 1, j]
                            startx, starty = x1, y1 + (level - vals[1, 0]) / (vals[0, 0] - vals[1, 0]) * (y2 - y1)
                            endx, endy = x2, y1 + (level - vals[1, 1]) / (vals[0, 1] - vals[1, 1]) * (y2 - y1)
                            one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                               neighborcells=[(i - 1, j), (i + 1, j)])
                            contour_segments.append(one_line)

                    else:
                        x1 = X[i, j]
                        x2 = X[i, j + 1]
                        y2 = X[i, j]
                        y1 = X[i + 1, j]
                        startx, starty = x1+ (level - vals[0, 0]) / (vals[0, 1] - vals[0, 0]) * (X2 - X1), y1
                        endx, endy = x2, y1 + (level - vals[1, 1]) / (vals[0, 1] - vals[1, 1]) * (y2 - y1)
                        one_line = Segment(endx, endy, startx, starty, cellindex=(i, j),
                                           neighborcells=[(i - 1, j), (i, j+1)])
                        contour_segments.append(one_line)

                elif cell_type == 3:
                    if vals[0, 0] >= level:
                        if vals[0, 1] >= level:
                            contour_line.append([X[i, j] + (level - vals[0, 0])/(vals[0, 1] - vals[0, 0]) * (X[i, j+1] - X[i, j]), Y[i, j]])
                        elif vals[1, 0] >= level:
                            contour_line.append([X[i, j], Y[i, j] + (level - vals[0, 0])/(vals[1, 0] - vals[0, 0]) * (Y[i+1, j] - Y[i, j])])
                    elif vals[0, 1] >= level:
                        if vals[1, 1] >= level:
                            contour_line.append([X[i, j+1], Y[i, j+1] + (level - vals[0, 1])/(vals[1, 1] - vals[0, 1]) * (Y[i+1, j+1] - Y[i, j+1])])
                        elif vals[1, 0] >= level:
                            contour_line.append([X[i, j] + (level - vals[0, 1])/(vals[1, 0] - vals[0, 1]) * (X[i, j+1] - X[i, j]), Y[i+1, j]])
                    elif vals[1, 0] >= level:
                        contour_line.append([X[i+1, j], Y[i+1, j] + (level - vals[1, 0])/(vals[1, 1] - vals[1, 0]) * (Y[i+1, j+1] - Y[i+1, j])])'''
def draw_contour(contours):
    for contour in contours:
        for ring in contour:
            x,y = zip(*ring)
            plt.plot(x,y)
    plt.show()
if __name__ == '__main__':

    write_to_wkt("cfs_withoutthinning.tif",1,[24,26,28],"isolines_csf.wkt",snap = 0.001)
    write_to_wkt("thinning.tif", 1, [24, 26, 28], "isolines_thinning.wkt", snap=0.001)
    #write_to_wkt("originl.tif", 1, [24, 26, 28], "isolines_originl_csf.wkt", snap=0.0001)




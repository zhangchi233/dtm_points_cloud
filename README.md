# dtm_points_cloud
# how to cropping the file
open the cropping.py file, change the filename and output into the file u want, u can run file cropping algorithm, default bound is middle, u can add u own bound in [xmin,xmax,ymin,ymax]

# how to do thinning and convert file to raster file
Open the DataProcess.py and run it change the filename in the thinning and output filename in write_to_raster
the function thinning is to thinning the las file and return a set of points contain x,y,z value in the list
arguments
the mode u can choose thinning method such as random or n-points 
the n_random argument is used for choose the bins if doing n points or n-points random, and teh cellsize is used for grid,cell_manipulation used for method in the cell
and percentage is the points we want to remain after thinning
in the file, we choose random and percentage is 0.1 
(if u choose grid, it may cost i some times)
write_to_raster, input a array of points in shape of(-1,3)
and write a raster file
arguments:
the driver is to choose the driver of raster
filename is the output filenames
crs the proj string of coordinate system, default is epsg:28992

# extract isolines
u can run file extract_isolines, 
write_to_wkt can store the isolines in wkt form
the argument filename is the raster u want to extract isoliens
band is the band u want to extract
levels is the levels of isolines u want to extract
output is the output filename
snap is the tolerence of snap when stick segments together

# how to do csf
points_grid.py
intput a list or array of points containing x,y,z value
and create a object from cloth class, taking that list of points as argument
run the dynamic method implementation_CSF and input the threhold u want the csf process to stop in the function
u can get a list of new particles after ground filtering

to visualize it u can run the draw_3d_plot function to see the particles

# a sample script containning the whole process from from doing csf, convert it to raster, store the result of csf and doing thinning , visualize the final result
using 3d plot function in matplotlib before and after csf and extract_isolins
open main.py file, and read the comment
(notice these file is just use for testing, i strongly recommend u to test it seperately, since we update our code and can't make sure the code in main.py still working or noe
furthermore since python is single thread, and it will takes u loads of time)
# some other functions
## how to visulize the csf process in 3d plot
to check the result of csf, we add a dynamic method in cloth class, which is used to implement csf
and input true or false in the argument showing originalz or show difference u can visulize the particles' 3d plot
if both argument is false, then it show the result after csf
## isoline extraction algorithm:
first define the points' position on cells boundary:
we iterate 2*2 block on dtm layer and store the coordinates of points the same as the isoline level
according to the points' number, we form segments in each block
store the segments two ends coordinate and its block index, and the neight block of two ends' index
get all segments:
in a list, find a segments neighbor segments according to segments' index and its neightbor index
add next end into ring
remove a segment if its two end has connected from list,
pop a new segment and start another ring of that level
## the main.py?
it is like a test file to test each sections function and methods, however, since we keep update our code, some method may out of date,
my dear teammates, strongly recommend u to test each parts method in targeted file
## why pickle?
it is annoying that the laspy official document so ambiguous and i dont like its way to store x,y,z value, for ur convenience, i dump it into a pickle file in the cropping.py,since each time we only use points'x,y,z values, why not just directly read from pickle file
## about thinning
we use random thinning(simple and easy to implement) 
## about file
4 isolines,wkt form
isolines_csf, is the isolines of csf result without thinning
isolines_thinning is the isolines of csf raster layer after thinning
isolines_original is the isolines of original raster layer without csf after thinning in the same range of result after csf
isoliens_exceed_part is the isolines of original points above the range of csf isoliens
thinning.tif is raster layer of csf result using laplace interpoaltion use random thinning only preserve 0.1 points
original.tif is raster layer of original points after thinning using random thinning only preserve 0.1 points and interpolation method is still laplace
csf_withoutthinnign.tif is raster layer of csf without thinning using laplace interpolation

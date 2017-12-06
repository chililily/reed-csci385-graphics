# Homework 3: we contour

*Due: 11/13/2017*

This assignment has you working with a surface, specified as a "winged
half-edge" data structure, to trace iso-elevation contours along the
facets of its surface. There are two main classes whose methods you
will complete: a class 'surface' and a class 'contour'. These are
each specified partially in their respective Python source files.

If you recall from class, the winged half-edge data structure gives us
a topological representation of the facets that form a surface,
specified as a triangular mesh. It consists of three geometric
components: the 0-dimensional vertices located at points in the 3D
space, the 1-dimensional edges that connect two vertices along a mesh
line, and the 2-dimensional triangular faces that serve as the facets
of the surface. These are formed by three consecutive vertices, and
thus bordered by three consecutive edges. It is a linked data
structure that ties these three geometric components together, in an
oriented way, so that code can "walk" over the surface and explore the
connectivity and neighborhood around a face, edge, or vertex.

The structure is built around an oriented "half edge". This runs from
a 'source' vertex to a 'target' vertex, and it borders a 'face' that
sits to its left. Around that face, a half edge has a 'next' edge and
'prev'(ious) edge, and these three form the border of the face they
each share. These are a circular list ordered around the face
according to the right-hand rule. If it is not at the boundary of a
surface, rather within the surface, a half edge has a 'twin' that is
the same edge, but oriented in the opposite direction. That twin's
face, forms the second of a "winged" pair of faces where those two
twinned edges form the hinge.

This assignment has you traverse this data structure by drawing
contours along the surface, ones that are made up of line segments
formed by where faces intercept with a certain y value. The user
interface for the assignment is specified in 'we_contour.py'. You
can enter a Unix command like

	python3 we_contour.py objs/bunny.obj

to read in Alias/Wavefront .OBJ files. The initial output of this
program gives you instructions for working with the surface stored
in this file so that you can test your code. You can also enter a
Unix command like

	python3 we_contour.py pgms/rainier.pgm

and this will instead read in a surface specified from a grid of
elevations in a .PGM (or Portable GreyMap file), once you've
completed that portion of the assignment.

There is a second test program 'test_contour.py' that can be run
with the command

	python3 test_contour.py

that you can use to test the curves you compute from contours in
PART 3 of the assignment.

This assignment comes in three parts:

* PART 1. Read a .PGM file into a 'surface', mimicking my code that
reads a .OBJ file into the half-edge structure.

* PART 2. Trace contours from a face at a certain y value.

* PART 3. "Compile" contours into smooth curves.

I describe each of these parts below.

## PART 1.

Here, I want you to write code that reads in the elevation data of
a portion of the earth, specified as a rectangulat grid of elevations, 
and represents it as a half-edge surface object. The elevation data 
is given as a grayscale image, taken from DEM (Digital Elevation Maps)
athat were converted into the GEOtiff format. I've converted these into
PGM text files (see below) since they are easy to read. You will write
the `read_pgm` method of `class surface`.

The first thing you want to do is start taking a look at the code in
`surface.py`, particularly the way I handle the construction of a 
surface's `vertex`, `edge`, and `face` objects, and tie them all 
together. To do this, you can start by checking out the code for
`read_obj` which constructs the half-edge surface representation
of a triangular mesh specified in a `.obj` file. It relies heavily
on `make_vertex`, `make_edge`, and `make_face` to construct each
of these components and then tie them all together.

You'll notice that the code uses vertex identifiers to indicate how
everything is tied together. This seemed necessary because of the way
meshes work---it seems wrong to identify vertices with their locations
in three-space. Instead we name each vertex, we build an object for
each vertex, and then we build faces (which builds three edges) by
identifying its corners with these vertex identifiers rather than the
vertex objects themselves. Because of the `.obj` file format, vertices 
are named with integers from 1 up to the number of vertices, and then
faces are specified with these integers.

Complete the code for `read_pgm`. This method takes a filename of a
PGM file, opens it, and reads the data to build up the surface in a
manner similar to the `read_obj` code.

Take a look at the Portable GrayMap format by inspecting the contents
of `pgms/test.pgm`. In that file you'll see four header lines:

* a line that says `P2`
* a comment line starting with a `#` that is generated by the file creator
* a line with two integers: the number of columns and the number of rows
that make up the PGM image
* a line with a single integer giving the maximum intensity value of all the 
data values (the pixels) of the (grayscale) image. This is usually 255,
but it could be anything.

What follows on the last line, or last series of lines, is a sequence of 
integers, each in the range from 0 to that maximum intensity, that describe
the intensity values of the pixels of the image. The sequence is in *row
major* order, meaning that the first set is from the first row of the image,
the next is from the second row, and so on. There should then be `rows` x
`columns` values in the last line or lines.

Your code should treat these as *y* values (heights) specified over a
regular grid of *x-z* locations. You could have the grid range from
-1.0 to 1.0 in each of the *x*/*z* dimensions and interpret the
intensity as a *y* value from 0.0 to 1.0. Or you can instead locate
them at integer coordinates---column, intensity, row. Whatever you
choose, they will be normalized to fit onto the screen by the `rebox`
method called near the end.

You'll need build a vertex for each data point, which means you'll need to
a choose name to identify each vertex for when you build the triangular faces
connecting them together. In my solution I chose to identify vertices by 
a string that contained their row and column position in the file.

You'll also need to build facets that form the surface. You can do
this by building two triangles for each grid cell. The corners of
those faces will correspond to the four places on the earth that form
a rectangular patch of that elevation survey. That quadralateral can
be split along a diagonal to form two oriented triangles. Make sure
you order those two triangular faces' vertices according to a
right-handed order, so that the normal points in the positive *y*
direction.

To test your code and make sure you've done things correctly, you can
run the `we_contour.py` program and have it load the files I've included
in the `pgms` and `low_pgms` folders. You can then "walk" on the surface
by placing the program in walk mode. Hit the `w` key and then click on
some face to highlight it. By pressing the `r`, `t`, and `y` keys you
ought to be able to move from facet to neighboring facet. If your code
is broken, then this will not work correctly. You can see a correct
walk if you instead load in `bunny.obj` or any of the other models
in the `objs` folder.

You might get into the USGS data by finding your own elevation maps
and conversting them into PGM format. I obtained several of these by
surfing the U.S. Geological Survey's [Earth Exlporer web
site.](https://earthexplorer.usgs.gov). I then used the free GIMP
program to "Export..." the images as PGM files with a `.pgm` 
extension.

## PART 2.

Having constructed surfaces, the real test is to do directed walking
on them. In this part of the assignment you'll trace contours around
objects or on terrains, according to a starting face and a particular
elevation level (a *y* coordinate value) that coincides with that 
face.

Write the code for the surface method `contour_at` that takes a face
`f` and a value `y`. You'll create a new `contour` object starting at
some point on an edge of `f`, then walk from face to face, forward and
backwards, to find all the line segments of a contour that runs along
the surface at that *y* value. 

When you are walking forward, you'll move from edge to edge, finding
which of the other two edges of that face are incident with that
contour. You can write code for the edge method `has_level` to
indicate whether or not an edge cuts the contour, contains that `y`
value in its height range. If an edge does get cut by the contour, you
can find the next point on the contour and add it with the contour
`append` method. You can write code for the edge method `at_level`
to return the point on the edge where its cut.

That walk could hit a dead end if the contour runs to the border of
the terrain's grid. If the forward walk hits the border, you'll want to
then start a backwards walk from the beginning point of the forward
walk. During the backward walk, you'll be instead calling the contour
`prepend` method to lay out the points you walk. This leads to an
"open" contour.

Alternatively, your forward walk will loop around the surface and
return to where it started. This leads to a "closed" contour.

Having traversed a contour along the surface from that starting face and at
that elevation level, you'll want to call the contour `complete` method.
This compiles the contour into a form that can be displayed by the 
program. That call should indicate whether the contour was closed or
was open. Have `contour_at` return that new, completed, contour object.

You can test this code by clicking on the surface when `we_contour.py`
is not in walk mode. Each click ought to trace out a curve along the
surface and it will be displayed in pink. Hitting `o` will change how
the object/terrain is displayed with these contours, including a
"TRoN" mode.

## Part 3.

Finally, I'd like these contours to be depicted as smooth continuous
curves.  Since the surfaces are faceted, the points you find when you
trace out the surface specify a closed polygon or an open polyline. As
a result, the contours can be quite jagged. To make the topological
maps that these trace out prettier, I'd like you to write a `compile`
method in `class contour` that uses one of the curve schemes we
described in class to compute a list of points `self.curve` that run
along a continuous curve approximated (or interpolated, for some
schemes) by the control polygon given by `self.points`. You can
use piecewise Bezier curves, or Chaikin's scheme, or B-splines, or
any of the subdivision methods we've surveyed.  

For closed contours, you'll thing of them as being described over a 
looped interval (topologically equivalent to a circle). For open curves
they are described over a closed line interval.

The contour-drawing surface display program can be made to use these
compiled curves. To do so you would edit the program's source to set
`SMOOTH_CONTOURS` to `True`. This, I think, makes the `compile` method
tricky to test and to debug. You might just try this once you
think your curve generation is working.

Instead, I've included a second display program `test_contour.py` that
you can use to test your curve generation. This program lets you edit
a (closed) control polygon. It will then build a contour object from
this control polygon, call your `compile` method, and then draw the
curve specified by that contour's `curve` list of points. Moving
the control polygon around will allow you to change the curve. It
recompiles with each change you make to the control polygon.

## Submitting your work

Just as in past homework, you'll want to commit and push the changes
you've made to the starting repository for this assignment. You should
update this README, or include a separate `submitted.md` file, so that
it briefly describes the work that you've completed and reports any
issues or implementation features of your code.

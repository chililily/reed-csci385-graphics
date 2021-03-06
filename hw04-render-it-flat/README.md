# Homework 4: render it flat
*Due: 10/11/2017*

For this assignment, you will write code that takes a snapshot of a
3D object, specified as a Wavefront `.obj` text file, and then outputs
it as a line drawing in the form of a Postcript `.ps` text file.
The initial code, as provided here, contains several Python files
that consitute a program that allows you to load in an object,
orient it for a "snapshot", then call your code to take the snapshot
and save it into the Postcript file. There are other supporting
files, namely a collection of sample object files in a folder
`objs` along with GLSL hardware shader code in a folder `shaders`.
You won't need to change any of these, although you are welcome to 
create (or find on-line) your own `.obj` files to try out your
code or to debug your code.

Most of your work will be to complete the code of several methods of
object classes defined in `object.py` and `geom2d.py`. These methods
will perform tasks like projecting the geometric components of an
object onto a plane, according to some focal point of that projection,
performing ray casting to see if which of these components are
obscured by others due to that projection, and checking to find which
components intersect when they are projected. These various methods,
used in concert with each other, will be used to figure out the line
drawing that depicts the object.
 
Below I take you through several parts of the project, orient you to
how everything is meant to work together, and then take you through
the steps of completing the project.

## Running the program.

Like the other two homeworks, you are building a PyOpenGL executable that
uses GLUT to open up a window that depicts a 3-D scene, rendered with the
OpenGL API. The scene it depicts is a single object, defined in a 
Wavefront `.obj` file, serveral of which can be found in `objs`. This
code works as stands, even without your additions. You can for example
type the command:

	 python3 obj2ps.py objs/soccer.obj

and that will load a 3-D polyhedron description and display it on the
screen using Phong illumination. You can change the lighting of the
object with the four arrow keys, and reorient the object by clicking
and dragging the mouse across the window. Hitting the space bar will
show you the underlying geometry---the mesh of triangles that form
that soccer ball object.

What does not work properly yet (of course) is the snapshot
mechanism. When you hit the period key `.` the system will invoke
the `toPS` class method for the class `object`. For now, that just 
does very little. It creates a new file with the name `soccerXYZ.ps`
(one where `XYZ` is chosen uniquely to not conflict with any other
similar-named files) with no drawing in it. Instead, that Postcript
file describes a blank page instead.

## The final product

You might find it useful to see what your code should ultimately
produce once it is working. I have run my solution to this project
on a different object, the file `objs/squares.obj`, one that I found
useful for debugging my code and getting everything correct.
I'll use it throughout this project description to give you a sense
of the intermediate steps for a solution. Here is a screen capture of the 
viewer's window when the program is run on this object file, with
a useful reorientation and lighting of its two squares, and with the
mesh shown:

![**Figure 1.** The `squares.obj` file when loaded with `obj2ps`.](images/viewer.jpg)

Below is a screen capture of a Postscript previewer window of `squares1.ps` 
produced by my program. You'll see a simple line drawing, one that matches
exactly the perspective view that was shown by `obj2ps` at the time of
its snapshot.  It shows the edges of all four triangular facets, but because
the front square's triangles obscure parts of the two in the back, some
portions of those back edges are removed in the drawing (well, they are
just not included in the drawing).

![**Figure 2.** Part of the `squares1.ps` preview.](images/final.jpg)

I'll describe Postscript in fuller detail below. Firstly here I'd at least
like you to get a sense of the big picture (pardon the pun) of the project.
The short of it is that the `.ps` file is a printable document---it contains
the instructions for drawing that figure onto a piece of paper with a
Postscript-capable printer---and is similar to the PDF documents
that we commonly share or print today. In fact, many different kinds of 
software read such files, and some can convert them into PDF. Linked below
is a PDF created by the Mac's **Preview** application, since it can read
the `.ps` format and save it as a `.pdf`.

* [The PDF version of `squares1.ps` produced on the Mac.](squares1.pdf)

Those of you without a Mac computer will want to find a way to view or
convert Postscript files. Adobe software often freely provides tools
for reading them (**Acrobat** or **Distiller**). Vector graphics
applications used by graphic designers---Adobe's **Illustrator** or
**Inkscape** for example---also read Postscript files. (Reed has a
site license for the former; the latter is free and open source.)
You'll want to obtain one of these previewers, readers, or converters
if you have a Windows or Linux system.  

Below I have two links to the Postscript file produced by my solution.
The first is instead called `squares1.txt` so that you can look at the
actual text contents of a Postscript file. The other is the actual
`squares1.ps` that you can use to try out any Postscript-reading
program you've found.

* [Sample output file as a `.txt` file.](squares1.txt)
* [Sample output file as the original `.ps` file.](squares1.ps)

## Reading object files using `object.py`

If you look through the source code for `obj2ps.py` you will see this
line in the `init` function:
     
	object.read(filename)

This invokes a class method of the object class `object` that builds
the geometric representation of a surface by reading in all the
geometric information stored in an `.obj` file named by the variable
`filename`. It builds a collection of `vertex` objects, the ones
described by lines that start with `v` in the `.obj` file. It will
also build a collection of new `face` objects, the ones described by
lines that start with `f` in the `.obj` file.  These faces are simply
described by three `vertex` objects. In addition, for each consecutive
pair of vertices on a face (and/or consecutive vertices of a hinge of
two faces) there will be an `edge` object built.

You can get access to these three sets of geometric components with
three class attributes: `vertex.all_instances`, `face.all_instances`,
and `edge.all_instances`.  It is these three kinds of surface
objects---vertices, edges, and faces---that you'll be working with to
do your coding. In fact, you'll be adding/fixing methods for these
three Python classes to complete the project. You'll be applying your
projection calculations to all of these.

You might want to take a look quickly through `object.py` to see everything
that is there, to see what you are extending. There you'll see that a
`face` consists of three `vertex` objects and that an `edge` consists of two 
`vertex` objects.  An `edge` also knows about one or two `face` objects. If
it forms the boundary of a non-closed surface, then it knows about one
`face`.  If it forms a hinge in the middle of a faceted surface (or is on
a closed surface), then it knows about a `face` object along with that
face's "twin" `face` object.

One thing to be aware of is that faces and edges share `vertex`
objects, and that adds a little bit of awkward complexity to the
`read` method of the `object` class. If you view the wirefram mesh of
the soccer ball, for example, you will notice that several edges exit
from any vertex (sometimes as many as 7, depending on the vertex).
And several triangular faces form "fans" or "cones" from any vertex
(again, sometimes as many as 7). This explains why, for example, 
in the `.obj` file, faces are described with vertex *indices*
(integers) rather than with triples of coordinates---the goal is
to, in essence, describe the topology of (i.e. the connectivity amongst)
the geometric components that make up the surface(s) of the object
being described.

This sharing of vertices and edges also adds a little bit of awkward
complexity to your coding task. You'll also notice that every `vertex`
and `edge` instance has attributes that describe where those
components fall "on film", that is, where they sit when projected
(via perspective projection from a focal point) onto a plane by our
virtual snapshot. Those are initially set to `None` but you will set
them to 2D `point` and 2D `segment` objects with your snapshot-making
code. (These objects are described, incidentally, in `geom2d.py`.)

## Postscript file support

Postcript is an interesting technology. It turns out it is a
programming language, one that has support for procedures, functions,
loops, objects (well, instead *dictionaries*) as well as a bunch of
drawing and frame transformation instructions , many of them having
analogues to what we've learned in OpenGL. The language was invented
to communicate documents to computer printers. A typical Postscript
file consists of curve, stroke, and fill instructions to depict the
letters, as font elements, of a typeset document, with those letters
laid out on several pages as the text of that document. It is an
extremely rich language with a very robust interpretation, and
it was a workhorse (and portable) format for exchanging documents
electronically before the more compressed PDF format was introduced.

There are several good resources in Postscript "programming" on the
web. One of my favorites is a textbook by the UBC mathematician
Bill Casselman. His 
[Mathematical Illustrations](http://www.math.ubc.ca/~cass/graphics/manual/)
attempts to teach a full CG course (like this CSCI 385) in Postscript
rather than a graphics API for computer hardware. You might take a look
at that book's contents to get a fuller sense of the history and details
of the language.

Instead, here I will show you a sample document's text:

	%!PS-Adobe-2.0
	gsave
	72 8.5 2 div mul dup translate
	0 72 11 8.5 sub mul translate
	1 720 div setlinewidth
	1000.0 1000.0 scale
	0.0 setgray
	newpath
	0.08521694132597768 -0.055059442087604396 moveto
	0.09651947521766979 -0.03739982206273046 lineto
	closepath
	stroke
	grestore
	showpage

This is a fairly simple one, but not much less complex than what
you'll generate. It depicts a single black-inked line segment, drawn
as a result of the commands from `newpath` to `stroke`. The stuff
preceding those commands set up the local frame for drawing that
segment, and the two lines that follow restore the global frame and
then show the page.

The source file `ps.py` contains functions that allow you to generate
this kind of Postscript output. In that file, there is a function `def
begin(fname)` that opens a file named `fname` and outputs that
"header" text into the file. From then on, subsequent calls to the
function `def draw_stroke(gray,segment)` will produce a series of line
segments. The value of `gray` is expected to be a floating point value
between 0.0 (for white) and 1.0 (for black). The value of `segment` is
expected to be a `segment2d` object that spans to (projected) points
(each instances of `point2d`; these are defined in `geom2d.py`). The
Postscript commands that draw those lines will be sent to that most
recently opened file. Finally, once all the lines of your figure have
been drawn, you can call `end()` to emit "footer" Postscript commands
and to close that file.

For debugging purposes, I've also provided a `set_gray` function which
sets the ink brightness, a `pick_color` function (which picks a random 
ink color, not just gray), and a `draw_dot` function which places a
small dot on the page. I found these useful for checking my own
solution's progress ("Am I computing the right intersections?", "Did
that point project to the correct place?", etc.)

You can see some of these commands in action in the current code for the
`object` class method `toPS`. There, I call `ps.begin` and `ps.end` to
output a blank drawing.

## Perform the camera projection

Let's start fixing `toPS`.

The first thing you will probably want to get correct is the
projection of the vertex points, which live in 3-d, (every vertex `v`
has a `v.position` attribute of type `point`) to 2-D (every vertex
should get a `v.on_film` attribute of type `point2d`). The way 
you can do this is by looping through all the vertices of the
object, and calling their `project` method, a method that takes
information about the perspective project to make.

This projection information is provided from the graphical interface
by a `camera` object instance. A camera object `c` has several
attributes: 

* `c.focus` is a point in 3-space where the projection
frustum's cone emanates
* `c.film_plane` is a point in 3-space sitting on the plane 
where the projected image is placed. It is a point on the 
"virtual film" of the projection. It can serve as the origin
point of the coordinate system for the 2-D image.
* `c.film_x`, `c.film_y`, `c.film_z` are three unit vectors
that correspond to the right, up, and "away" directions on the 
film plane. The last is pointed towards the focus point and
away from the object, and all three constitute a right-handed 
collection of orthonormal vectors.  

When you project onto the plane, you can use `film_x` and
`film_y` to calculate the coordinates of the projected points.
You can use `film_z` to compute relative distances of vertices
away the film plane, that is, you can compute depth information 
to determine whether edges are hidden on the line drawing or not.

To compute the perspective projection of all the vertices, you want
to fix the code for the `camera` class method `project`. This method
takes a `point` object `Q`, and should return a pair `(Qp,depth)`.
The first component should be `point2d` locating the point on the
film plane. The second should be a depth/distance that you can use
later to determine the back-to-front ordering of the faces on
the object.

This calculation is (or is like) what you were asked to determine
for Homework 3. I've published a link to my solution to that
exercise on the course web site.

When you have completed this step correctly, you can draw a Postscript
figure like this one:

![**Figure 3.** The projection of `squares.obj`.](images/projected.jpg)

## Find projected edge intersections.

The next part of `toPS` projects all the edges of the object onto
the film plane. This, it turns out, performs no calculations. Instead
we are simply creating a `segment2d` object out of 2-D points of
the vertex pair that defines that edge.

Here next you will probably want to compute all the intersections of
the object's projected edges. You'll do this because these intersection
points serve as the potential "breakpoints" for depicting the edges.
If, for example, an edge is obscured by an occluding face somewhere
in its middle, then the start and end points of that occlusion will
occur at the place where that face's edges cross this edge in the
projection. For example, examine this picture, where I've added dots
to Figure 2 or all the computed segment intersections:

![**Figure 4.** The 2-D segment intersections of `squares.obj`.](images/intersected.jpg)

You'll want to write the code for the method `intersect` within class
`segment2d` of `geom2d.py`. It should expect another `segment2d` to
check its intersection with.  There are several ways to write this
code though, regardless, you will probably want to give back different
results for when the segments intersect versus when they don't. 

Because of how we are using this code, I think it's fine to say that
two segments *do not intersect* when they share an endpoint. (Recall
that edges regularly share endpoints with other edges.) Instead,
what you truly want to know is whether the two segments cross in the
middle.

It seems reasonable to, when they *do* intersect, give back their 
intersection point as a `point2d` object. You can also return any
other information that you might find useful, anything useful that
was computed when the intersection was found. For example, one
version of my code returned that convex combination weights for
(fractional values between 0.0 and 1.0) where the intersection
point sat within the queried segment.

## Determine the included/excluded subsegments

Now that we've marked out all the intersections, we'll now actually
want to draw the lines of the figure. Below I have an image I
built showing the method I used for this: 

![**Figure 5.** Annotations showing the calculations for `squares.obj`.](images/hidden.jpg)

Here you see clearly that edges can have a series of included (black) and
excluded (light gray) subsegments. The excluded ones are those obscured by 
some face sitting closer to the film plane (and this are closer to the focus point
of the camera). 

To do this, I computed the sequence of subsegments that form the full
edge line.  I then cast a ray from the focus point, through the film,
to each subsegment, to see whether or not it should be drawn or
note. If some triangle sat closer to the film, then I did not draw
that subsegment. If they all sat further away, or no other faces
were hit by that ray, then I drew that subsegment.

My method for this was to compute the midpoints of each subsegment.
These are each depicted as a colored dot in the above figure. Below
is a figure showing just those midpoints:

![**Figure 6.** Locations of the targets of each cast ray for checking occlusions.](images/shot.jpg)

This is not quite correct. What I really did was determine the ray 
that passed from the focus point, through the film, to the midpoint of
the portion of the edge in 3-space that projects to that subsegment.
I checked to see if any other faces were pierced by that ray at 
a distance that placed them in front of that midpoint. This
was how I determined whether that subsegment should be drawn or not.

All this functionality sits in three places in the code, as it is presently
organized:

* I've made a template for a `edge` method called `render` that can do
the work of issuing a series of `ps.draw_stroke` calls to draw all
the non-hidden subsegments of an edge. (This could be no calls if the
edge is completely obscured.) Right now that code simply draws the whole
edge.
* I've made a template for an `object` method called `hides` which can be
used to return whether or not a point in 3-space is hidden by some face
in the object (one of the object's `self.faces`). It takes the camera
and the point in 3-space being checked. It also takes a collection of
faces that should not be considered (namely, these can be the faces
that use the edge being checked).
* I've made a template for a `face` method called `intersects_ray` that
returns whether or not a face is pierced by a ray.  This can compute
and return any useful information you would like for `hides` to use,
and should certainly return whether or not that face is hit by the
ray.

You don't necessarily have to structure your code exactly this way,
but I found this organization made some real sense (they each seemed like
a natural method to write for their respective class) and they fit
my strategy for generating the Postscript output.

## What else?

At this point, if you've completed these steps, your code should be
working and your coding work is complete. Go back and comment the code
(if you haven't been doing it all along) and also create a
`submitted.txt` or `submitted.md` report.

If you were quickly successful in completing the work, then you might 
take the assignment a bit further. Here are a few ideas for "bells and
whistles" that you could add to your submission:

* **more objects.** You might consider generating more `.obj` files,
especially ones that better showcase the rendering method we've
performed. You might find more files on the web. You might also try
using a modeling system (like the free and rich **blender**
application) to build these files. Just be careful: the method
outlined above has a running time quadratic in the number of edges and
the number of edge intersections computed. The `bunny.obj` is 
included, but my solution is unable to render it because of the
thousands of facets that make up that model.

* **shade the faces.** The assignment asks you to draw outlines to
depict faces. You could instead have the `render` function be told
where the light source sits, and this info could be used to draw
filled faces instead, shaded with a level of gray that corresponds to
the light that would be reflected back from its surface. To do this,
you'll want to use the `fill` Postscript command rather than the
`stroke` command.  You'll also want to issue a series of `lineto`
commands that form the outline of that filled polygon.

* **hide edges on a flat polygonal face.** There are `.obj` files
on-line that specify a surface with non-triangular facets. The `f`
lines in the file specify, instead, a polygonal "fan"---a series of
vertices that serve as that face's boundary.  With this models, it
would be cool to depict them as their projected polygon rather than as
a fan of triangles.  Similarly, `soccer.obj` and `squares.obj` have
hinged faces that are flat. For these kind of surfaces, you could
choose to exclude any edges that form a flat hinge. Then, for example,
the soccer ball would look like a soccer ball, and the squares would
look like two squares.

* **a floor with shadows.** You could have the model sit on a plane
in the image, send the light information to the renderer, and compute
a picture of a shadow sitting below the object. To do this, you'll want
to use the `fill` Postscript command rather than the `stroke` 
command.  You'll also want to issue a series of `lineto` commands
that form an outline of a polygon, one that makes up a portion of
the shadow's image. Should you want the graphical interface depict
the shadow, too, talk with me. I've written GLSL shader code that
works in this way and I'd be willing to share it.

* **cast shadows on the object.** Taking the above idea further, you
could have faces cast shadows onto other faces. This too would have you
casting rays from the light source onto the faces of the object. And then
any faces hit by a light ray behind that face could have their face been
drawn in shadow.

Should you choose to do any of these, or make other enhancements, make
sure you describe them in your `submitted` document.

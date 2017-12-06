# Homework 6: loop subdivision

*Due: 11/27/2017*

This assignment continues with the framework of the last assignment,
again using the winged half-edge data structure as defined in a file
`surface.py`. Here, rather than walking over the surface, you will 
instead create a new, smoother, surface via Loop supdivision. Here, 
the initial surface is made up of a mesh of triangles. To make
the smoother surface, subdivision occurs in two stages: (1) a splitting
step where each edge is split in half allowing us to split each triangular
face into four "subtriangles," and (2) a smoothing step where each 
vertex is repositioned by computing a convex combination of its position with
the positions of the endpoints of its incident edges. If this two-step
process is repeated, the successive surfaces (with 4x, then 16x, then
64x, as many triangles, and so forth) converges to a G^2 continuous
surface.  Each step *refines* the mesh, that is, each is a *refinement*
of the one prior.

The winged edge data structure is useful here, in that it gives us the
neighborhood structure for computing this refinement mesh from its
prior mesh. The tricky part of subdivision, then, is building up 
all the links of the refined mesh.

## The Assignment

This folder contains essentially the same starting point as the last
assignment. You can read in .OBJ files and display their meshed
surfaces:

	python3 loop.py objs/bunny.obj

Pressing the SPACE bar will change how that surface/mesh is displayed.
Hitting `.` will send a request to the `surface` object to compute
a refined surface according to the Loop subdivision rules (described
just below), calling the method `refinement`. This part is not yet 
implemented, and your job is write that method's code. Instead, right
now it simply makes a copy of the mesh.

Once things are working, you can use the `+` and `-` keys to scroll
amongst the various refinements, with `-` displaying a coarser mesh,
and `+` displaying a finer mesh.

## Loop Subdivision

Charles Loop's subdivision scheme (from his 1987 Master's thesis
at University of Utah) has been streamlined in its presentation
using terminology similar to that used for curve subdivision. 
Here we follow that kind of description of Schröder and Zorin's SIGGRAPH
2000 course notes. Here is a figure from their notes:

[*Figure.* Loop subdivision rules from Schroder and Zorin (2000).](loop_rules.jpg)

In curve subdivision, we split each polygonal edge of the control
polygon in half, doubling the number of vertices.  The midpoint
vertices that are introduced by this split are called the *odd
vertices* because they end up being put at odd indices (they are of
the form *2i+1*) and the original vertices, the ones that get averaged
for that midpoint split, are called the *even vertices* (their indices
are of the form *2i*). Taking this view, Chaikin's "corner-cutting"
algorithm can be described more directly: we introduce the odd
vertices of the refined polygon by computing the midpoint of the
unrefined control polygon, with weights 1/2 and 1/2. We "introduce"
the even vertices of the refined polygon by computing the 1/8,3/4,1/8-weighted
combination of three successive vertices of the unrefined polygon.

Described this way, we combine the splitting and smoothing step.

For Loop surface subdivision, for the refined mesh the odd vertices
are those introduced to split edges, and the even vertices are those
that are introduced to replace the ones on the unrefined mesh.
For odd vertices, the weighting rule is 1/8 each for the two
corners of the split edge's neighboring faces, and 3/8 each for
the endpoints of the split edge.  For even vertices, the weighting
rule is more complicated, as it depends on the number of edges 
emanating from that vertex (its degree or *valence*) and the weights
involve computing a cosine. The picture summarizes both of these computations
with their weighting schemes.

Furthermore, if a surface has a boundary (or if you want to preserve a 
"crease"), we instead use the curve subdivision rule for vertices
along that boundary. This boundary occurs when the edge does not
have a twin. Using the curve rules, the odd/even vertices will
not get pulled toward the corner of the edge's one face.

Write the code for subdivision using these splitting and smoothing
rules.

## Suggested Solution

This code, to me, feels somewhat like the postscript renderer, in that
you will probably want to add an attribute to `vertex` objects and an
attribute to `edge` objects, each corresponding to the vertex you
introduce for them during a subdivision step. For vertices your
"cloning" to make an even vertex. For edges you are "splitting"
to make an odd vertex.  You'll want this extra attribute for vertices
because you don't want to clone a vertex more than once. You'll want
this extra attribute for edges because you don't want to split an 
edge more than once. The key puzzle we're solving is to stitch together
the faces and edges of the refined surface correctly, and these new
vertices will be shared by multiple faces on that surface. 

Let *S* be the surface before the subdivision and *R* be the new,
refined surface resulting from the subdivision. Each vertex `v` on *S*
gets copied as a new "even vertex" for *R*. I would attach this to `v`
as a `v.clone` attribute that is initially `None`. Later attempts to
clone `v` won't happen because that `v.clone` attribute will be set.
Also, each half-edge `e` gets split into a new "odd vertex" for *R*.
I would attach this to `e` as an `e.split` attribute that is initially
`None`. Later attempts to split the twin of that edge should check to
see if this `split` attribute is set so that you only create one
odd vertex for each half-edge pair.

These new odd and even vertices will all get stitched together when
you create the four subfaces (say, by calling `make_face` four times)
within *R*. Do this once for each face in *S*, creating these four
subfaces in *R*. In the code I give you, I suggest this be done with a
`split_into` method called for each face of *S*. Within `f.split_into`
you'll attempt to introduce clones and splits for the vertices and
half edges of a face `f`.  In some cases those clones and/or splits
will already have been built. In other cases they will not have yet
been built. You can check the `clone` and `split` attributes to see
whether that work has been done already for neighboring faces.

Whenb you clone and split, you'll use the Loop weights shown in the
picture above, of course.

## Submitting your work

Just as in past homework, you'll want to commit and push the changes
you've made to the starting repository for this assignment. You should
update this README, or include a separate `submitted.md` file, so that
it briefly describes the work that you've completed and reports any
issues or implementation features of your code.

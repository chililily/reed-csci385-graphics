# Homework 1: object showcase

*Due: 9/8/2017*

CSCI 385: Graphics
Fall 2017  
Professor: Jim Fix  
Reed College  

# Assignment overview

Modify one of the two sample GL/GLUT python programs (`showV1` or
`showV2`) so that it generates faceted models of the following:

* Facets that form the surface of a cube.
* A mesh of facets that form the surface of a cylinder (parameterized).
* A mesh of facets that form the surface of a sphere (parameterized).
* A mesh of factes that form the surface of a torus (parameterized).
* Programmer's choice: depict a surface of your choosing.

# Status

**Legend**  
[x] complete  
[~] complete w/ bugs  
[o] in progress  
[ ] not started  
  
[x] Ex.1, cube
[x] Ex.2, cylinder
[x] Ex.3, sphere
[x] Ex.4, torus
[~] Ex.5, objFiles

## Notes

**Exercise 5, objFiles**

'sandal.obj'

The mesh for this looks incomplete, even though the number of facets generated matches the number specified in the file. My guess is that it has to do with the kinds of info in the file that weren't handled.

'teapot.obj'
I get zero division errors here when I try to normalize the surface normal vectors in the process of generating color for a facet. Didn't get around to trying to fix it and just let the color default to a predetermined value, which makes the teapot look kind of awkward. 
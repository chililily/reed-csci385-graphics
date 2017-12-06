#
# object.py
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This is the starting code for Homework 4. Please see the README for
# a description of what's here.
#
# Defines a class called "object" that contains a method for reading an 
# Alias/Wavefront .obj files and storing them as a collection of faces.
#
#   vertex: a corner of a faceted surface.  It has a 3D position 
#           and participates in faces.
#
#   face: a triangular face on a surface of some object in the 
#         scene.  It has three vertices ordered in counter-
#         clockwise fashion.
#
#   edge: a border of a face and/or the meeting of two hinged
#         faces on the surface.
#
# Also contains a class method 'object.toPS' for rendering that object, 
# using perspective projection (and occlusion checking with ray-casting),
# as a Postscript file.
#
# That rendering is prescribed by a 'camera' object whose attributes 
# describe a perspective projection.
#

from constants import *
from geom2d import vector2d, point2d, segment2d, ORIGIN2D
from geometry import vector, point, ORIGIN
from math import sqrt
import ps

from itertools import combinations
import sys

#
# class camera
#
# Represents the parameters of a 3-D snapshot, that is, a perspective
# projection on a frustum cone with the given focus point, casting
# rays on to the given film plane, specified by a point and three
# axis directions. The x and y are on the film plane. The z shoots
# perpendicularly from the film, away from the object, towards the
# focus point.
#
# Thus x,y,z form an orthonormal frame whose origin is that film
# point.
#
class camera:

    def __init__(self,focus,film_point,film_x,film_y,film_z):
        self.focus = focus
        self.film_point = film_point
        self.film_x = film_x
        self.film_y = film_y
        self.film_z = film_z # points away from the object towards the focus point
        
    def project(self,Q):
        d = (self.focus-self.film_point).dot(self.film_z)
        d2 = (self.focus-Q).dot(self.film_z)
        Qp = self.focus + (d/d2)*(Q-self.focus)
        
        Qp = Qp - self.film_point
        Qpx = Qp.dot(self.film_x)
        Qpy = Qp.dot(self.film_y)
        Qp = point2d(Qpx,Qpy)
        return (Qp,Q.z)

#
# class edge
#
# Defines an object class that represents a hinge's crease 
# or a face boundary of a faceted surface.
#
# An edge spans two vertices and participates in one or two
# faces.
#
class edge:
    
    instances = []
    dictionary = {}

    @classmethod
    # edge.with_ids(ids):
    #
    # Lookup and return an edge with this identifying
    # pair of vertex IDs.
    #
    def with_ids(cls,ids):
        if ids[1] > ids[0]:
            return cls.dictionary[ids]
        else:
            return cls.dictionary[(ids[1],ids[0])]
            
    @classmethod
    #
    # edge.add(v1,v2,f):
    #
    # Considers whether to build a new edge instance
    # that connects the two vertices v1 and v2 on the
    # face f.  If the edge v2->v1 already has been 
    # built, then this hinge face (the "twin") is
    # recorded.
    #
    # If a new edge, the edge constructor is called.
    #
    def add(cls,v1,v2,f):
        # Devise the correct identifier(s) for this edge.
        i1 = v1.id
        i2 = v2.id
        if i1 > i2:
            # Order the vertex indices canonically.
            i1,i2 = i2,i1
            v1,v2 = v2,v1
        
            
        # If the edge already exists, record this
        # hinge face.
        if (i1,i2) in cls.dictionary:
            cls.dictionary[(i1,i2)].add_face(f)
        else:
            # Otherwise, add a new edge.
            i = len(cls.instances)
            e = edge(v1,v2,f,(i1,i2),i)
            cls.dictionary[(i1,i2)] = e
            cls.instances.append(e)

    @classmethod
    def all_instances(cls):
        return cls.instances

    # edge(v1,v2,f,ids,id):
    #
    # Builds a new edge, one that spans the two given
    # vertices and forms the boundary of the given face.
    # 
    # This would likely never be called directly, and is
    # instead used by the 'add' class method above.
    #
    # This is because we don't want to build an edge that
    # has already been created (perhaps on a neighboring
    # face).
    #
    def __init__(self,v1,v2,f,ids,id):

        self.ids      = ids
        self.id       = id
        self.source   = v1
        self.target   = v2

        self.face     = f
        self.twin     = None

        self.on_film  = None # I used this to store the projected segment.

    # e.add_face(f):
    #
    # This edge occurs on a hinged pair of faces.
    # Here we record the second face on that hinge
    # in the attribute 'e.twin'.
    #
    def add_face(self,f):
        if self.twin == None:
            self.twin = f

    # e.project(camera):
    #
    # Calculates this edge's image onto the film plane of the 
    # given camera. This method requests that each endpoint's
    # projected position be determined. A segment2d object is 
    # built from these two positions and recorded for later
    # calculations made by a snapshot.
    #
    def project(self,camera):
        if self.on_film == None:
            v1 = self[0]
            v2 = self[1]
            v1.project(camera)
            v2.project(camera)
            v1p = v1.on_film
            v2p = v2.on_film
            self.on_film = segment2d(v1p,v2p)

    # e.reset_film()
    #
    # Removes the stored projection information, readying it
    # for a new snapshot to be taken. Does the same for its
    # two endpoint vertices.
    #
    def reset_film(self):
        self.on_film = None
        self[0].reset_film()
        self[1].reset_film()

    # e.render(camera):
    #
    # Issues a series of 'ps.draw_stroke' calls for the
    # visible subsegments of this edge's projected 
    # segment2d ('self.on_film').
    #
    def render(self,camera):
        xs = [0]

        # Find and draw intersections
        for e in edge.all_instances():
            p = self.on_film.intersect(e.on_film)
            if p[0] != None:
                for i in range(len(xs)):
                    if p[1]<xs[i]:
                        xs.append(xs[i])
                        xs[i] = p[1]
                        break
                    elif i == len(xs)-1:
                        xs.append(p[1])
                        break
                # ps.draw_dot(p[0])
        xs.append(1)

        # Draw included/excluded subsegments
        s = self.source.position
        t = self.target.position
        d = t-s
        s2 = self.on_film.source
        d2 = self.on_film.target-self.on_film.source
        for i in range(len(xs)-1):
            p1 = s2+xs[i]*d2
            p2 = s2+xs[i+1]*d2
            pmid = p1+0.5*(p2-p1)
            p3mid = s+0.5*(xs[i]+xs[i+1])*d

            subseg = (p1,p2)
            if not object.hides(camera,p3mid,[self.face,self.twin]):
                ps.draw_stroke(1,subseg)


    # e[0] gives the source vertex.
    # e[1] gives the target vertex.
    #
    def __getitem__(self,i):
        assert(i == 0 or i == 1)
        if i==0:
            return self.source
        else:
            return self.target
            
#
#  class vertex: 
#
#  Its instances are corners of a faceted surface. 
#  The class also houses a list of all its instances.
#
class vertex:

    # vertex class attributes:
    #
    # * instances: a list of all instances of class vertex
    #
    instances = []

    @classmethod
    #
    # vertex.with_id(id):
    #
    # Returns the instance with the given integer id.
    #
    def with_id(cls,id):
        return cls.instances[id]

    @classmethod
    #
    # vertex.all_instances():
    #
    # Returns all the instances of class vertex as a list.
    #
    def all_instances(cls):
        return cls.instances

    @classmethod
    # vertex.add(p):
    #
    # Creates and returns a new vertex instance at position p.
    #
    def add(cls,position):
        return vertex(position)

    # vertex(P):
    #
    # (Creates and) initializes a new vertex object at position P.
    #
    def __init__(self,P):
        self.position   = P
        self.id         = len(vertex.instances)
        self.normal     = None
        self.on_film    = None # I used this to store the projected point.
        self.depth      = None # I used this to store depth information from the projection.
        vertex.instances.append(self)

        
    # v.reset_film()
    #
    # Removes the stored projection information, readying it
    # for a new snapshot to be taken.
    #
    def reset_film(self):
        self.on_film = None

    # v.project(camera)
    #
    # Calculates this vertex's image onto the film plane of the 
    # given camera. A point2d object is calculated from the 
    # vertex's 3-D position point. We rely here on the 'project'
    # method of the camera object. We store the projected point
    # in the vertex's `on_film' attribute, and depth information
    # in the vertex's 'depth' attribute.
    #
    def project(self,camera):

        # This is how I projected the vertex position point. My camera object
        # has a method that returns the projected point and some depth info.
        if self.on_film == None:
            p,d = camera.project(self.position)
            self.on_film = p
            self.depth = d

#
# class face: 
#
# Its instances are triangular facets on the surface.  It has three
# vertices as its corners.
#
class face:

    # Class attributes:
    #
    #  * instances: list of all face instances
    #
    instances = []

    @classmethod
    # face.of_id(id):
    #
    # Get the face with the given integer id.
    #
    def of_id(cls,id):
        return cls.instances[id]

    @classmethod
    # face.all_instances():
    #
    # Returns the list of all face instances.
    #
    def all_instances(cls):
        return cls.instances

    @classmethod
    # face.add(V1,V2,V3):
    #
    # Creates and returns a new face instance with vertex corners
    # V1, V2, and V3.
    #
    def add(self,V1,V2,V3):
        return face(V1,V2,V3)

    #
    # face(V1,V2,V3):
    #
    # Create and initialize a new face instance.
    # Also creates its edges.
    #
    # Instance attributes:
    #
    #   * vertices: vertex instances that form the face
    #   * fn: face normal
    #   * id: integer id identifying this vertex
    #
    def __init__(self,V1,V2,V3):

        self.vertices = [V1,V2,V3]

        edge.add(V1,V2,self)
        edge.add(V2,V3,self)
        edge.add(V3,V1,self)

        self.id = len(face.instances)
        face.instances.append(self)
        self.fn = None

    #
    # f.normal():
    #
    # Returns the surface normal of this face.  Computes 
    # that normal if it hasn't been computed yet.
    #
    def normal(self):
        if not self.fn:
            p0 = self[0].position
            p1 = self[1].position
            p2 = self[2].position
            v1 = p1 - p0
            v2 = p2 - p0
            self.fn = v1.cross(v2).unit()

        return self.fn

    #
    # f.vertex(i):
    # 
    # Returns either the 0th, the 1st, or the 2nd vertex.
    #
    def vertex(self,i):
        if i > 2:
            return None
        else:
            return self.vertices[i]

    #
    # f.intersect_ray(R,d):
    #
    # Returns whether the face is hit by a ray directed
    # from a point R in the (unit) direction d.
    #
    def intersect_ray(self,R,d,camera):
        p0 = self[0].position
        p1 = self[1].position
        p2 = self[2].position

        delta = (R-p0).dot(self.normal())
        if delta < 0:
            self.fn = -self.fn / self.fn.norm()
        elif delta == 0:
            return False
        g = -d.dot(self.normal())
        if g <= 0:
            return False
        P = R + (abs(delta)/g)*d
        
        w = P-p0
        o = (p1-p0).cross(p2-p0)

        s2 = (p1-p0).cross(w).dot(o)
        s3 = w.cross(p2-p0).dot(o)

        if (s2 < 0 or s3 < 0):
            return False

        a2 = (p1-p0).cross(w).norm() / o.norm()
        a3 = w.cross(p2-p0).norm() / o.norm()

        if (a2 >= 0 and a3 >= 0 and 1-a2-a3 >= 0):
            return True
        else: 
            return False

    #
    # f[i]:
    #
    # Returns the i-th vertex around the face.
    #
    def __getitem__(self,i):
        return self.vertex(i)

#
# class object:
#
# Singleton object that houses all the methods that govern reading 
# scene (.obj) files and incorporating them into the vertex and 
# face collections above.
#
class object:

    @classmethod
    def read(cls,filename):

        obj_file = open(filename,'r')

        # Record the offset for vertex ID conversion.
        vertexi = len(vertex.all_instances())   

        # Count the number of vertex normals read.
        normali = 0                             

        for line in obj_file:

            parts = line[:-1].split()
            if len(parts) > 0:

                # Read a vertex description line.
                if parts[0] == 'v': 
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    P = point(x,y,z)
                    vertex.add(P)

                # Read a vertex normal description line.
                elif parts[0] == 'vn': 
                    dx = float(parts[1])
                    dy = float(parts[2])
                    dz = float(parts[3])
                    vn = vector(dx,dy,dz).unit()
                    # vertex.with_id(normali).set_normal(vn)
                    normali += 1

                # Read a face/fan description line.
                elif parts[0] == 'f': 

                    #### ADDS AN OFFSET vertexi FROM THE .OBJ INDEX!!! (.OBJ starts at 1) ####
                    vi_fan = [int(p.split('/')[0]) + vertexi - 1 for p in parts[1:]]

                    vi1 = vi_fan[0]
                    # add the faces of the fan
                    for i in range(1,len(vi_fan)-1):
                        vi2 = vi_fan[i]
                        vi3 = vi_fan[i+1]
                        V1 = vertex.with_id(vi1)
                        V2 = vertex.with_id(vi2)
                        V3 = vertex.with_id(vi3)
                        face.add(V1,V2,V3)

        # rescale and center the points
        object.rebox()

    @classmethod
    def rebox(cls):
        max_dims = point(sys.float_info.min,
                         sys.float_info.min,
                         sys.float_info.min)
        min_dims = point(sys.float_info.max,
                         sys.float_info.max,
                         sys.float_info.max)
        for V in vertex.all_instances():
            max_dims = max_dims.max(V.position)
            min_dims = min_dims.min(V.position)

        origin = point((min_dims.x + max_dims.x)/2.0,
                       (min_dims.y + max_dims.y)/2.0,
                       (min_dims.z + max_dims.z)/2.0)
        delta = max_dims - min_dims
        biggest = max(delta.dx,max(delta.dy,delta.dz))
        scale = sqrt(2.0)/biggest

        for V in vertex.all_instances():
            V.position = ORIGIN + scale * (V.position-origin)

    @classmethod
    def compile(cls):
        varray = []
        narray = []
        for f in face.all_instances():
            for i in [0,1,2]:
                varray.extend(f.vertex(i).position.components())
                narray.extend(f.normal().components())
        return (varray,narray)

    @classmethod
    def hides(cls,camera,point,excluding=[]):
        """
        Determine whether any of the faces in 'face.all_instances'
        would obscure the given 'point' when a snapshot is taken
        with 'camera'. The 'excluding' parameter is a list of faces
        that should not be included for consideration.

        If this is used to cast a ray to a point on an edge, then
        'excluded' should hold the face(s) that are formed by that 
        edge.
        """
        for f in face.all_instances():
            if (f == excluding[0] or f == excluding[1]):
                break
            else:
                d = camera.focus-point
                d = d / d.norm()
                if f.intersect_ray(point,d,camera):
                    return True

        return False

    @classmethod
    def toPS(cls,fname,camera):
        """
        Render the read object's geometry into a 
        Postscript file. You'll need to write the
        method 'render' for class 'edge' to emit
        'ps.draw_stroke' commands into that .ps
        file.
        """

        # Reset for the next snapshot.
        for e in edge.all_instances():
            e.reset_film()

        # Project all the vertices.
        for v in vertex.all_instances():
            v.project(camera)

        # Project all the edges.
        for e in edge.all_instances():
            e.project(camera)

        # Start making the Postscript drawing.
        ps.begin(fname)

        # Render each of the edges.
        for e in edge.all_instances():
            e.render(camera)

        # Finish the Postscript drawing.
        ps.end()



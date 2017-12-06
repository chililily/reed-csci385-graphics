from geometry import vector, point, ORIGIN
from math import sqrt, cos, pi
import sys
from OpenGL.GL import *

#
# surface.py
#
# HOMEWORK 6
#
# Exercise:
#    
#    surface.refinement
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This defines a class for representing a triangular mesh surface
# class, one that uses a half-edge winged data structure.  The
# assignment asks you to write the code for the method `refinement`
# one that returns a new surface that results from a single Loop
# subdivision of its edges and faces.
#

EPSILON = 1.0e-8
        
class vertex:
    def __init__(self,id,P):
        self.id = id
        self.position = P
        self.edge = None
        self.clone = None

    def set_edge(self,e):
        self.edge = e

    def fix_edge(self):
        assert(self.edge != None)
        e = self.edge
        while self.edge.twin != None and self.edge.twin.next != e:
            self.edge = self.edge.twin.next

    def clonef(self,id,S):
        if self.clone == None:
            p0 = self.position
            e0 = self.edge

            e = e0
            points = []
            walking = True
            forward = True
            first = True
            if e0.twin == None:
                atBound = True
            else:
                atBound = False

            while walking:
                if forward:
                    if (not first) and (e == e0 or e == e0.twin):
                        walking = False
                        break

                    if e.source == self:
                        p = e.target.position
                    else:
                        p = e.source.position
                    points.append(p)

                    if e.twin != None:
                        e = e.twin
                    else:
                        if e == e0:
                            e1 = e.next
                            if not (e1.source == self or e1.target == self):
                                e1 = e1.next
                            if e1.source == self:
                                p = e.target.position
                            else:
                                p = e.source.position
                            points.append(p)
                        if atBound:
                            walking = False
                        else:
                            e = e0.twin
                            forward = False

                    if first:
                        first = False
                    e = e.next
                    if not (e.source == self or e.target == self):
                        e = e.next
                else:
                    e = e.prev

                    if not (e.source == self or e.target == self):
                        e = e.prev

                    if e.source == self:
                        p = e.source.position
                    else:
                        p = e.target.position
                    points.append(p)

                    if e.twin == None:
                        walking = False

            n = len(points)
            c = cos(2*pi/n)
            b = 5/8 - pow(3+2*c,2) / 64

            if n < 3:
                v = 0.75*(p0-ORIGIN) + 0.125*(points[0]-ORIGIN) + 0.125*(points[1]-ORIGIN)

            else:
                v = (1-b)*(p0-ORIGIN)
                for p in points:
                    v += (b/n)*(p-ORIGIN)

            v = ORIGIN + v

            self.clone = S.make_vertex(v,id)

        else:
            self.clone = S.make_vertex(self.clone.position,id)

        return self.clone
                
class edge:
    def __init__(self,id,v0,v1):
        self.id = id
        self.source = v0
        v0.edge = self
        self.target = v1
        self.next = None
        self.prev = None
        self.face = None
        self.twin = None
        self.split = None

    def set_next(self,e):
        self.next = e
        e.prev = self

    def set_twin(self,e):
        self.twin = e
        e.twin = self

    def set_face(self,f):
        self.face = f
        f.edge = self

    def vector(self):
        return self.target.position - self.source.position

    def splitf(self,id,S):
        if self.split == None:
            fp0 = self.source.position
            fp1 = self.target.position

            # Boundary case
            if self.twin == None:
                e0v = fp1 - fp0
                newVertex = S.make_vertex(fp0+0.5*e0v,id)
                self.split = newVertex

            else:
                f0p2 = None
                f1p2 = None
                e = self

                # Find other two vertices of faces spanned by edge
                while (f0p2 == None or f1p2 == None):
                    e = e.next

                    # Target vertex is the desired vertex
                    if e.source == self.source or e.source == self.target:
                        if f0p2 == None:
                            f0p2 = e.target.position
                            e = self.twin
                        else:
                            f1p2 = e.target.position
                    # Source vertex is the desired vertex
                    else:
                        if f0p2 == None:
                            f0p2 = e.source.position
                            e = self.twin
                        else:
                            f1p2 = e.source.position

                # Calculate position of new vertex
                point = ORIGIN + 0.125*(f0p2-ORIGIN) + 0.125*(f1p2-ORIGIN) + 0.375*(fp0-ORIGIN) + 0.375*(fp1-ORIGIN)
                self.split = S.make_vertex(point,id)

        else:
            self.split = S.make_vertex(self.split.position,id)
            
        return self.split

class face:
    def __init__(self,e01,e12,e20):
        e01.set_next(e12)
        e12.set_next(e20)
        e20.set_next(e01)
        e01.set_face(self)
        e12.set_face(self)
        e20.set_face(self)
        self.norm = None

    def normal(self):
        if self.norm == None:
            v1 = self.edge.vector()
            v2 = -self.edge.prev.vector()
            self.norm = v1.cross(v2).unit()
        return self.norm

    def points(self):
        p0 = self.edge.prev.target.position
        p1 = self.edge.target.position
        p2 = self.edge.next.target.position
        return (p0,p1,p2)

    def split_into(self,new_S,idx):
        e0 = self.edge
        e1 = e0.next
        e2 = e1.next

        eid,oid = 0,0

        edges = [e0,e1,e2]
        vs,odds,evens = [],[],[]
        eids,oids = [],[]

        for e in edges:
            if not e.source in vs:
                vs.append(e.source)
            o = str(idx)+"o"+str(oid)
            oids.append(o)
            odds.append(e.splitf(o,new_S))
            oid += 1

        for v in vs:
            ev = str(idx)+"e"+str(eid)
            eids.append(ev)
            evens.append(v.clonef(ev,new_S))
            eid += 1

        new_S.make_face(oids[0],oids[1],oids[2])
        new_S.make_face(oids[-1],eids[0],oids[0])
        new_S.make_face(oids[0],eids[1],oids[1])
        new_S.make_face(oids[1],eids[2],oids[2])




class surface:
    class v_iterator:
        def __init__(self,S):
            self.index = 0
            vs = S.vertices.values()
            self.vs = [v for v in vs]

        def __iter__(self):
            return self    

        def __next__(self):
            if self.index >= len(self.vs):
                raise StopIteration()
            else:
                v = self.vs[self.index]
                self.index = self.index+1
                return v

    class f_iterator:
        def __init__(self,S):
            self.index = 0
            self.fs = S.faces

        def __iter__(self):
            return self    

        def __next__(self):
            if self.index >= len(self.fs):
                raise StopIteration()
            else:
                f = self.fs[self.index]
                self.index = self.index+1
                return f

    @classmethod
    def from_obj(cls,filename):
        S = surface()
        S.read_obj(filename)
        return S

    @classmethod
    def from_pgm(cls,filename):
        S = surface()
        S.read_pgm(filename)
        return S

    def __init__(self):
        self.vertices = {}
        self.edges = {}
        self.faces = []

    def all_vertices(self):
        return surface.v_iterator(self)

    def all_faces(self):
        return surface.f_iterator(self)

    def make_vertex(self,P,id=None): # NOTE: changed this slightly from homework 5!
        if id == None:
            id = str(len(self.vertices))
        v = vertex(id,P)
        self.vertices[id] = v
        return v

    def make_edge(self,vi0,vi1):
        v0 = self.vertices[vi0]
        v1 = self.vertices[vi1]
        eid = (vi0,vi1)
        tid = (vi1,vi0)
        e = edge(eid,v0,v1)
        self.edges[eid] = e
        if tid in self.edges:
            t = self.edges[tid]
            e.set_twin(t)
        return e

    def make_face(self,vi0,vi1,vi2):
        e01 = self.make_edge(vi0,vi1)
        e12 = self.make_edge(vi1,vi2)
        e20 = self.make_edge(vi2,vi0)
        f = face(e01,e12,e20)
        self.faces.append(f)
        return f

    def read_obj(self,filename):
        vertex_id = 1
        obj_file = open(filename,'r')
        for line in obj_file:
            parts = line[:-1].split()
            if len(parts) > 0:
                # Read a vertex description line.
                if parts[0] == 'v': 
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    P = point(x,y,z)
                    self.make_vertex(P,vertex_id)
                    vertex_id += 1
                # Read a face/fan description line.
                elif parts[0] == 'f': 
                    #### SUBTRACTS 1 FROM THE .OBJ INDEX!!! (.OBJ starts at 1) ####
                    vi_fan = [int(p.split('/')[0]) for p in parts[1:]]
                    vi1 = vi_fan[0]
                    # add the faces of the fan
                    for i in range(1,len(vi_fan)-1):
                        vi2 = vi_fan[i]
                        vi3 = vi_fan[i+1]
                        f = self.make_face(vi1,vi2,vi3)
        # rescale and center the points
        self.rebox()
        # fix the vertices
        self.fix_edges()

        obj_file.close()

    
    def rebox(self,xscale=1.0,yscale=1.0,zscale=1.0):
        max_dims = point(sys.float_info.min,
                         sys.float_info.min,
                         sys.float_info.min)
        min_dims = point(sys.float_info.max,
                         sys.float_info.max,
                         sys.float_info.max)
        for v in self.all_vertices():
            max_dims = max_dims.max(v.position)
            min_dims = min_dims.min(v.position)

        center = point((min_dims.x + max_dims.x)/2.0,
                       (min_dims.y + max_dims.y)/2.0,
                       (min_dims.z + max_dims.z)/2.0)
        delta = max_dims - min_dims
        biggest = max(delta.dx,max(delta.dy,delta.dz))
        scale = sqrt(2.0)/biggest

        for v in self.all_vertices():
            offset = (v.position-center) * scale
            offset.dx *= xscale 
            offset.dy *= yscale 
            offset.dz *= zscale 
            v.position = ORIGIN + offset
            
    def fix_edges(self):
        for v in self.all_vertices():
            v.fix_edge()

    def compile(self):
        num_vs = 0
        varray = []
        narray = []
        for f in self.all_faces():
            e1 = f.edge
            e2 = e1.next
            e3 = e2.next
            varray.extend(e1.target.position.components())
            varray.extend(e2.target.position.components())
            varray.extend(e3.target.position.components())
            num_vs += 3
            narray.extend(f.normal().components()*3)
        return (num_vs,varray,narray)


    def refinement(self):
        #
        # YOUR CODE FOR Loop subdivision refinement step GOES HERE
        # (you can mimic my code structure, or write your own code)

        S = self
        R = surface()
        idx = 0

        #
        # Make clones of the vertices within R, 
        # introduce the split vertices into R,
        # and then connect them all, one per face.
        #
        for f in S.all_faces():
            f.split_into(R,idx)
            idx += 1

        R.fix_edges()

        # Return the surface
        return R

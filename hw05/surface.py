from geometry import vector, point, ORIGIN
from contour import contour
from math import sqrt
import sys
from OpenGL.GL import *

#
# surface.py
#
# HOMEWORK 5
#
# Exercises:
#    
#    surface.read_pgm
#    surface.contour_at
#    edge.has_level
#    edge.at_level
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This defines a class for constructing a contour traced
# along a faceted surface. Points can be added to the front
# or the back of the contour (with prepend/append). Once
# all the points have been added, the contour can be
# "completed" as wither a closed or open contour.
#
# Completion "compiles" a smooth curve that approximates/
# interpolates the contour's traced polygon.
#

EPSILON = 1.0e-8
        
class vertex:
    def __init__(self,id,P):
        self.id = id
        self.position = P
        self.edge = None

    def set_edge(self,e):
        self.edge = e

    def fix_edge(self):
        assert(self.edge != None)
        e = self.edge
        while self.edge.twin != None and self.edge.twin.next != e:
            self.edge = self.edge.twin.next
                
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

    def has_level(self,lvl):
        psource = self.source.position
        ptarget = self.target.position

        if psource.y <= lvl and lvl <= ptarget.y:
            return True
        elif ptarget.y <= lvl and lvl <= psource.y:
            return True
        else:
            return False

    def at_level(self,lvl):
        psource = self.source.position
        ev = self.vector()

        if ev.dy != 0:
            weight = (lvl-psource.y) / ev.dy
        else:
            weight = 0.5
        pX = psource+weight*ev

        return pX
        
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
        
    def intersects_ray(self,R,d):
        assert(abs(d.norm() - 1.0) < EPSILON)
        
        Q1,Q2,Q3 = self.points()

        # compute normals to the plane of the facet
        v12 = Q2 - Q1
        v13 = Q3 - Q1
        out = v12.cross(v13)
        if abs(out) < EPSILON:
            # the facet is a sliver or a point
            return None
        
        P = Q1
        u = v12.unit()
        v = v13.unit()
        w = u.cross(v).unit()
        above = w.dot(R - P)
        if abs(above) < EPSILON:
            # the ray source R is in the plane of this facet
            return None

        # flip the orientation of the surface normal to the back face
        if above < 0:
            n = -w
        else:
            n = w
        ratio = -(n.dot(d))
        if ratio <= 0:
            # the ray shoots along or away from the facet's plane
            return None

        # Compute the distance from R to where it hits the plane.
        distance = abs(above) / ratio

        # Compute where the ray intersects the plane.
        S = R + (distance * d)

        height = (R-S).dot(n)

        # check if P lives within the facet
        offset = S-P
        o3 = v12.cross(offset)
        o2 = offset.cross(v13)
        if o2.dot(w) < 0 or o3.dot(w) < 0:
            # the point S is not in the cone <Q1,v2,v3>
            return None

        a2 = abs(o2)/abs(out)
        a3 = abs(o3)/abs(out)
        a1 = 1.0-a2-a3
        if a1 < 0.0 or a2 < 0.0 or a3 < 0.0:
            # the point S is beyond line <Q2,Q3> in that cone
            return None

        return (S,distance)

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

    def make_vertex(self,id,P):
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
                    self.make_vertex(vertex_id,P)
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

    def read_pgm(self,filename):
        with open(filename,"r") as pgm_file:
            rows = 0
            cols = 0
            currRow = 1
            currCol = 1
            count = 1

            for line in pgm_file:
                parts = line.split()

                # Set number of rows and columns
                if count <= 4:
                    if len(parts) > 1 and rows == 0:
                        if parts[0].isdigit() and parts[1].isdigit():
                            rows = int(parts[0])
                            cols = int(parts[1])
                    count += 1
                # Read height data
                else:
                    for p in parts:
                        if not p.isdigit():
                            break

                        # Make vertex
                        height = int(p)
                        P = point(currCol,height,currRow)
                        vId = (currRow,currCol)
                        self.make_vertex(vId,P)

                        # Make 2 facets according to 2x2 square
                        # with current vertex (vId) at position 11:
                        # [ 00  01 ]
                        # [ 10  11 ]
                        if currRow > 1 and currCol > 1:
                            vId00 = (currRow-1,currCol-1)
                            vId01 = (currRow-1,currCol)
                            vId10 = (currRow,currCol-1)

                            self.make_face(vId,vId01,vId00)
                            self.make_face(vId,vId00,vId10)

                        if currCol == cols:
                            currCol = 1
                            currRow += 1
                        else:
                            currCol += 1

        self.rebox(1.0,0.5,1.0)
        self.fix_edges()

    def contour_at(self,f,lvl):
        # Find a point on f at lvl
        e0 = f.edge
        
        if e0.has_level(lvl):
            pass
        elif e0.next.has_level(lvl):
            e0 = e0.next
        pX0 = e0.at_level(lvl)

        c = contour(pX0)

        walking = True
        forward = True
        currEdge = e0.twin
        switch = True

        while walking:
            if switch:
                e1 = currEdge.next
                e2 = e1.next
                switch = False
            else:
                e1 = currEdge.prev
                e2 = e1.prev
                switch = True

            if forward:
                if e1.has_level(lvl):
                    pXc = e1.at_level(lvl)
                    if e1.twin != None and e1.twin.next != None:
                        currEdge = e1.twin
                    else:
                        forward = False
                        switch = False
                        currEdge = e0
                elif e2.has_level(lvl):
                    pXc = e2.at_level(lvl)
                    if e2.twin != None and e2.twin.next != None:
                        currEdge = e2.twin
                    else:
                        forward = False
                        switch = False
                        currEdge = e0

                if e1 == e0 or e2 == e0:
                    walking = False

                c.append(pXc)

            else:
                if e1.has_level(lvl):
                    pXc = e1.at_level(lvl)
                    if e1.twin != None:
                        currEdge = e1.twin
                    else:
                        walking = False
                elif e2.has_level(lvl):
                    pXc = e2.at_level(lvl)
                    if e2.twin != None:
                        currEdge = e2.twin
                    else:
                        walking = False

                c.prepend(pXc)


        c.complete(forward)
        return c
    
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

    def hit_by(self,R,d):
        hits = []
        for f in self.all_faces():
            hit = f.intersects_ray(R,d)
            if hit != None:
                hits.append((f,hit[0],hit[1]))
        if len(hits) > 0:
            hits.sort(key=(lambda s: s[2]))
            return hits[0]
        else:
            return None



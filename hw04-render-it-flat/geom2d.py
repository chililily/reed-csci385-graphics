#
# geom2d.py
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This defines three names: 
#
#    point2d: a class of locations in 2-space
#    vector2d: a class of offsets between points within 2-space
#    segment2d: a class of a line segment sitting in 2-space
#    ORIGIN2D: a point at the origin 
#
# The point and vector classes/datatypes are designed based on 
# Chapter 3 of "Coordinate-Free Geometric Programming" (UW-CSE
# TR-89-09-16) by Tony DeRose.
#

from random import random
from math import sqrt, pi, sin, cos, acos
from constants import EPSILON
from OpenGL.GL import *

#
# Description of 2-D point objects and their methods.
#
class point2d:

    def __init__(self,_x,_y):
        """ Construct a new point instance from its coordinates. """
        self.x = _x
        self.y = _y

    @classmethod
    def with_components(cls,cs):
        """ Construct a point from a Python list. """ 
        return point(cs[0],cs[1])

    @classmethod
    def origin(cls):
        return point2d(0.0,0.0)
    
    def components(self):
        """ Object self as a Python list. """
        return [self.x,self.y]

    def plus(self,offset):
        """ Computes a point-vector sum, yielding a new point. """
        return point2d(self.x+offset.dx,self.y+offset.dy)

    def minus(self,other):
        """ Computes point-point subtraction, yielding a vector. """
        return vector2d(self.x-other.x,self.y-other.y)

    def dist2(self,other):
        """ Computes the squared distance between self and other. """
        return (self-other).norm2()

    def dist(self,other):
        """ Computes the distance between self and other. """
        return (self-other).norm()

    def combo(self,scalar,other):
        """ Computes the affine combination of self with other. """
        return self.plus(other.minus(self).scale(scalar))

    def combos(self,scalars,others):
        """ Computes the affine combination of self with other. """
        P = self
        for i in range(min(len(scalars),len(others))):
            P = P + scalars[i] * (others[i] - self)
        return P

    def max(self,other):
        return point(max(self.x,other.x),max(self.y,other.y))

    def min(self,other):
        return point(min(self.x,other.x),min(self.y,other.y))

    #
    # Special methods, hooks into Python syntax.
    #

    __add__ = plus  # Defines p + v

    __sub__ = minus # Defines p1 - p2

    def __bool__(self): 
        """ Defines if p: """
        return self.dist(ORIGIN) > EPSILON

    def __str__(self):
        """ Defines str(p), as homogeneous coordinates. """
        return str(self.components()+[1.0])+"^T"

    __repr__ = __str__ # Defines Python's presentation of a point.

    def __getitem__(self,i):
        """ Defines p[i] """
        return (self.components())[i]


#
# Description of 2-D vector objects and their methods.
#
class vector2d:

    def __init__(self,_dx,_dy):
        """ Construct a new vector instance. """
        self.dx = _dx
        self.dy = _dy

    @classmethod
    def with_components(cls,cs):
        """ Construct a vector from a Python list. """
        return vector2d(cs[0],cs[1])

    @classmethod
    def random_unit(cls):
        """ Construct a random unit vector """

        #
        # This method is adapted from 
        #    http://mathworld.wolfram.com/SpherePointPicking.html
        #
        theta = random() * pi * 2.0
        return vector2d(cos(theta), sin(theta))

    def components(self):
        """ Object self as a Python list. """
        return [self.dx,self.dy]

    def plus(self,other):
        """ Sum of self and other. """
        return vector2d(self.dx+other.dx,self.dy+other.dy)

    def minus(self,other):
        """ Vector that results from subtracting other from self. """
        return self.plus(other.neg())

    def scale(self,scalar):
        """ Same vector as self, but scaled by the given value. """
        return vector2d(scalar*self.dx,scalar*self.dy)

    def neg(self):
        """ Additive inverse of self. """
        return self.scale(-1.0)

    def dot(self,other):
        """ Dot product of self with other. """
        return self.dx*other.dx+self.dy*other.dy

    def cross(self,other):
        """ Cross product of self with other. """
        return self.dx*other.dy-self.dy*other.dx

    def perp(self):
        return vector2d(-self.dy,self.dx)

    def norm2(self):
        """ Length of self, squared. """
        return self.dot(self)

    def norm(self):
        """ Length of self. """
        return sqrt(self.norm2())

    def unit(self):
        """ Unit vector in the same direction as self. """
        n = self.norm()
        if n < EPSILON:
            return vector2d(1.0,0.0)
        else:
            return self.scale(1.0/n)

    #
    # Special methods, hooks into Python syntax.
    #

    __abs__ = norm  # Defines abs(v).

    __add__ = plus  # Defines v1 + v2

    __sub__ = minus # Defines v1 - v2

    __neg__ = neg   # Defines -v

    __mul__ = scale # Defines v * a

    def __truediv__(self,scalar):
        """ Defines v / a """
        return self.scale(1.0/scalar)

    def __rmul__(self,scalar):
        """ Defines a * v """
        return self.scale(scalar)

    def __bool__(self):
        """ Defines if v: """
        return self.norm() > EPSILON

    def __str__(self):
        """ Defines str(v) """
        return str(self.components()+[0.0])+"^T"

    __repr__ = __str__ # Defines the interpreter's presentation.

    def __getitem__(self,i):
        """ Defines v[i] """
        return (self.components())[i]

class segment2d:

    def __init__(self,p1,p2):
        self.source = p1
        self.target = p2

    def intersect(self,other):
        # Segments share an endpoint
        if (self.source == other.source or self.source == other.target or self.target == other.source or self.target == other.target):
            return (None,0)

        # Credit: https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        else:
            d1 = self.target-self.source
            d2 = other.target-other.source

            # <self> segment = s + w*d1
            # <other> segment = s_o + w_o*d2
            d1xd2 = d1.dx*d2.dy-d2.dx*d1.dy

            # Segments are parallel/anti-parallel
            if d1xd2 == 0:
                return (None,0)
            else:
                dsource = other.source-self.source

                # Weight along <self/other> vector at intersection
                w = (dsource.dx*d2.dy-d2.dx*dsource.dy)/d1xd2
                w_o = (dsource.dx*d1.dy-d1.dx*dsource.dy)/d1xd2

                # Point of intersection contained within both segments
                if (0 <= w and w <= 1 and 0 <= w_o and w_o <= 1):
                    return (self.source+(w*d1),w)
                else:
                    return (None,0)


    def __getitem__(self,which):
        assert(which == 0 or which == 1)
        if which == 0:
            return self.target
        else:
            return self.source
# 
# The point at the origin.
#
ORIGIN2D = point2d(0.0,0.0)

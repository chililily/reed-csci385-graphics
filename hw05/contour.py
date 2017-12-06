from geometry import vector, point, ORIGIN
from math import sqrt
import sys
from OpenGL.GL import *

#
# contour.py
#
# HOMEWORK 5
#
# compile exercise
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

class contour:
    def __init__(self,P0):

        # Used during contour construction.
        self.back = [P0]
        self.front = []

        # Set after contour completion.
        self.points = None
        self.curve = None
        self.closed = False

    # c.close()
    #
    # Sets the contour to be a closed polygon/curve.
    #
    def close(self):
        self.closed = True

    # c.prepend(P):
    #
    # Add a point to the front of the contour.
    #
    def prepend(self,P):
        assert(self.points == None)
        self.front.append(P)

    # c.append(P):
    #
    # Add a point to the end of the contour.
    #
    def append(self,P):
        assert(self.points == None)
        self.back.append(P)

    # c.complete(closed=True/False):
    #
    # Finalizes the contour, setting it to be open/closed.
    # This sets self.points and then uses these as the control
    # polygon for self.curve.
    #
    def complete(self,closed=True):
        self.points = self.back[::-1] + self.front
        self.back = None
        self.front = None
        self.closed = closed
        self.compile_curve()

    # c.compile_curve():
    #
    # Computes a list of points self.curve that are on a
    # smooth curve of an approximation/interpolation of 
    # the polygon that describes the contour.
    #
    def compile_curve(self):

        self.curve = []

        if self.closed:
            start = -1
        else:
            start = 1

        step = 4

        for i in range(start,len(self.points)-1):
            p1 = self.points[i]

            if i-1 == 0 and not self.closed:
                p0 = self.points[i-1]
            else:
                p0b = self.points[i-1]
                v0 = p0b-p1
                p0 = p1+0.5*v0
            if i+1 == len(self.points)-1 and not self.closed:
                p2 = self.points[i+1]
            else:
                p2b = self.points[i+1]
                v2 = p2b-p1
                p2 = p1+0.5*v2

            v01 = p1-p0
            v12 = p2-p1

            u = 0
            while u < 1:
                p01 = p0+u*v01
                p12 = p1+u*v12
                v012 = p12-p01
                p012 = p01+u*v012

                self.curve.append(p012)

                u += 1 / step

    # GETTERS

    # c.get_points()
    #
    # Returns the control polygon points.
    #
    def get_points(self):
        return self.points

    # c.get_curve()
    #
    # Returns the curve points.
    #
    def get_curve(self):
        return self.curve

    # c.is_closed()
    #
    # Returns whether or not the contour is closed.
    #
    def is_closed(self):
        return self.closed


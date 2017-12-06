from geometry import point, vector, EPSILON, ORIGIN
from ctypes import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *
#
# polygon.py
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This contains functions for drawing 2D polygons and
# polylines made up of 3D points. The points either 
# live in the same x-y plane or the same x-z plane.
#
# This draws the lines as triangle pairs, along with
# triangular "caps" that form the beveled corners of
# the shape.
#
# It defines two key functions:
#
#   1. draw_poly: directly renders the polygon using
#      GL_TRIANGLES
#
#   2. vbo_poly: hands back a new VBO for rendering
#      the polygon, specifying the vertices of the
#      triangles, to be used by shaders.
#
# Example:
#
#   draw_poly(points,plane,width,closed=True):
#
# Draws a polygon whose corners are specified by
# the 'points' list, ones that live in either the
# "x-y" or "x-z" plane, with the specified line width,
# either closed or open.
#
# vbo_poly is similar, but returns a pair (n,b) where
# b is the vertex buffer object and n is the number of
# vertices in that object.
#

def x_y_by90(v):
    return vector(-v.dy,v.dx,v.dz)

def x_z_by90(v):
    return vector(v.dz,v.dy,-v.dx)

def render_poly_step(p, q, by90, width, renderer, caps=None):
    v = (q-p).unit() * width
    ov = by90(v)
    iv = -ov

    op = p + ov
    ip = p + iv
    oq = q + ov
    iq = q + iv
    
    renderer(ip,op,oq)
    renderer(oq,iq,ip)

    if caps != None:
        ocap,icap = caps
        renderer(ocap,op,p)
        renderer(ip,icap,p)

    return (oq,iq)


def render_poly(points,plane,width,renderer,closed=True):
    n = len(points)
    if plane == "x-y":
        by90 = x_y_by90
    else:
        by90 = x_z_by90

    caps = None
    for i in range(0,n-1):
        caps = render_poly_step(points[i],points[i+1],by90,width,renderer,caps)
    if closed:
        caps = render_poly_step(points[n-1],points[0],by90,width,renderer,caps)
        render_poly_step(points[0],points[1],by90,width,renderer,caps)

def draw_poly(points,plane,width,closed=True):
    if len(points) <= 2:
        return
    def draw(p,q,r):
        p.glVertex3()
        q.glVertex3()
        r.glVertex3()
    glBegin(GL_TRIANGLES)
    render_poly(points,plane,width,draw,closed)
    glEnd()

def vbo_poly(points,plane,width,closed=True):
    if len(points) <= 2:
        return
    buffer = []
    count = 0

    def include(p,q,r):
        nonlocal count
        buffer.extend(p.components())
        buffer.extend(q.components())
        buffer.extend(r.components())
        count += 3

    render_poly(points,plane,width,include,closed)

    contour_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, contour_buffer)
    glBufferData(GL_ARRAY_BUFFER, len(buffer)*4, (c_float*len(buffer))(*buffer), GL_STATIC_DRAW)

    return (count,contour_buffer)


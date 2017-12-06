#
# showV2/show.py
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This is a sample GLUT program that constructs an object made 
# up of triangular facets.  It relies heavily on the geometry and
# quaternion packadges.  We'll discuss the design of geometry.py 
# first when we examine affine spaces this and next week.  We'll
# look at using quaternions for specifying rotations, the ideas
# that inform quat.py, in later weeks.
#
# The OpenGL drawing part of the code occurs in drawScene.  The
# building of the geometric model occurs in makeObject(), and this
# relies on functions (e.g. 'make_tetra') defined in 'object.py', 
# and called in __main__ to create a list of triangular facets.
#

import sys
import os.path as path
from quat import quat
from geometry import vector,point
from object import *
from random import random
from math import sin, cos, acos, pi, sqrt

from OpenGL.GLUT import *
from OpenGL.GL import *

# These are initialized in 'main' below.
trackball = None
facets = None
show_which = 0
smoothness = 3

def makeObject():
    if show_which == 0:
        return make_tetra()
    elif show_which == 1:
        return make_cube()
    elif show_which == 2:
        return make_cyl(smoothness)
    elif show_which == 3:
        return make_sphere(smoothness)
    elif show_which == 4:
        return make_torus(smoothness)
    elif show_which == 5:
        # For the purposes of this assignment,
        # assumes file is in folder objFiles one level up.
        filename = input("Enter the name of a file to read: ")

        parentDir = path.abspath(path.join(__file__,"../.."))
        rpath = "objFiles/"+filename
        absPath = os.path.join(parentDir,rpath)
        
        return make_fromOBJ(absPath)
    else:
        # Return no facets.
        return []

def drawObject():    
    # Draw all the triangular facets.
    glBegin(GL_TRIANGLES)
    for f in facets:
        glColor3f(f.material.red, f.material.green, f.material.blue)
        glVertex3fv(f[0].components()) 
        glVertex3fv(f[1].components()) 
        glVertex3fv(f[2].components()) 
    glEnd()

def drawScene():
    """ Issue GL calls to draw the scene. """

    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Clear the transformation stack.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Transform the objects drawn below by a rotation.
    trackball.glRotate()
    
    # Draw a floating "pixel."
    glColor(1.0,1.0,1.0)
    glPointSize(20)
    #
    glBegin(GL_POINTS)
    point(0.0,0.0,2.0).glVertex3()
    glEnd()

    # Draw the object,
    drawObject()

    # Render the scene.
    glFlush()


def myKeyFunc(key, x, y):
    """ Handle a "normal" keypress. """
    global facets, smoothness, show_which

    # Handle the SPACE bar.
    if key == b' ':
        # Redraw.
        glutPostRedisplay()

    # Handle smoothness using '-' and '=/+' keys
    if key == b'-' and smoothness > 0:
        smoothness -= 1
        facets = makeObject()
        glutPostRedisplay()

    if (key == b'=' or key == b'+') and smoothness < 100:
        smoothness += 1
        facets = makeObject()
        glutPostRedisplay()

    # Handle ESC key.
    if key == b'\033':  
    # "\033" is the Escape key
        sys.exit(1)

    # Handle object selection.
    #
    if key == b'0':
        # Tetrahedron.
        show_which = 0
        facets = makeObject()
        glutPostRedisplay()
    #
    if key == b'1':
        # Cube.
        show_which = 1 
        facets = makeObject()
        glutPostRedisplay()
    #
    if key == b'2':
        # Cylinder
        show_which = 2
        facets = makeObject()
        glutPostRedisplay()
    #
    if key == b'3':
        # Sphere
        show_which = 3
        facets = makeObject()
        glutPostRedisplay()
    #
    if key == b'4':
        # Torus
        show_which = 4
        facets = makeObject()
        glutPostRedisplay()
    #
    if key == b'5':
        # Hmm...
        show_which = 5
        facets = makeObject()
        glutPostRedisplay()


def myArrowFunc(key, x, y):
    """ Handle a "special" keypress. """
    global trackball

    x_axis = vector(1.0,0.0,0.0)
    y_axis = vector(0.0,1.0,0.0)

    # Apply an adjustment to the overall rotation.
    if key == GLUT_KEY_DOWN:
        trackball = quat.for_rotation( pi/12.0,x_axis) * trackball
    if key == GLUT_KEY_UP:
        trackball = quat.for_rotation(-pi/12.0,x_axis) * trackball
    if key == GLUT_KEY_LEFT:
        trackball = quat.for_rotation(-pi/12.0,y_axis) * trackball
    if key == GLUT_KEY_RIGHT:
        trackball = quat.for_rotation( pi/12.0,y_axis) * trackball

    # Redraw.
    glutPostRedisplay()


def initRendering():
    """ Initialize aspects of the GL scene rendering.  """
    glEnable (GL_DEPTH_TEST)


def resizeWindow(w, h):
    """ Register a window resize by changing the viewport.  """
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if w > h:
        glOrtho(-w/h*2.0, w/h*2.0, -2.0, 2.0, -2.0, 2.0)
    else:
        glOrtho(-2.0, 2.0, -h/w * 2.0, h/w * 2.0, -2.0, 2.0)


def main(argc, argv):
    """ The main procedure, sets up GL and GLUT. """
    global trackball, facets

    trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))
    facets = makeObject()

    glutInit(argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(360, 360)
    glutCreateWindow( b'object showcase - Press ESC to quit' )
    initRendering()

    # Register interaction callbacks.
    glutKeyboardFunc(myKeyFunc)
    glutSpecialFunc(myArrowFunc)
    glutReshapeFunc(resizeWindow)
    glutDisplayFunc(drawScene)

    print()
    print('Press the arrow keys to rotate the object.')
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()

    return 0

if __name__ == '__main__': main(len(sys.argv),sys.argv)

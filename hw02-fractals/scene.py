#
# scene.py
#
# Author: Jim Fix
# CSCI 385: Computer Graphics, Reed College, Fall 2017
#
# This is a sample GLUT program that displays 2D "painting" using a
# OpenGL coordinate frame transformations in combination with two
# drawing procedures 'RTRI' and 'DISK'. The first draws a right
# triangle with sides of unit length. The second draws a solid
# circle with unit radius.
#
# This can be used as inspiration for drawing your own scene for
# Homework 2.
#

import sys
from random import random
from math import pi,sin,cos

from OpenGL.GLUT import *
from OpenGL.GL import *

scene = 1
levels = 0
angle = 30

### SIMPLE FIGURES =========================
# 
# RTRI
#
# Draws an isoceles right triangle whose corner is at the origin
# and whose sides are along the +x and +y axes with unit length.
#
def RTRI():
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0,0.0)
    glVertex2f(1.0,0.0)
    glVertex2f(0.0,1.0)
    glEnd()

# DISK
#
# Draws a unit disk centered at the origin.
#
def DISK():
    sides = 100
    dtheta = 2.0 * pi / sides
    for i in range(100):
        theta = i*dtheta
        # draw a pie slice on the disk
        glBegin(GL_TRIANGLES)
        glVertex2f(0.0,0.0)
        glVertex2f(cos(theta),sin(theta))
        glVertex2f(cos(theta+dtheta),sin(theta+dtheta))
        glEnd()


# BOX
#
# Draws a unit square with lower-left corner at the origin.
#
def BOX():
    RTRI()
    glPushMatrix()
    glTranslatef(1.0,1.0,0.0)
    glRotatef(180.0,0.0,0.0,1.0)
    RTRI()
    glPopMatrix()

# RECT
#
# Draws a 1x2 rectangle (1 wide, 2 high) with lower-left corner at the
# origin.
#
def RECT():
    BOX()
    glPushMatrix()
    glTranslatef(0.0,1.0,0.0)
    BOX()
    glPopMatrix()

# Draws equilaterial triangle (side length 1) with lower-left corner at
# origin.
def eqTRI():
    glBegin(GL_TRIANGLES)
    glVertex2f(0.0,0.0)
    glVertex2f(cos(pi/3),sin(pi/3))
    glVertex2f(1.0,0.0)
    glEnd()

def SPINE():
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.02,0)
    glVertex2f(-0.02,1)
    glVertex2f(0.02,0)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(0.02,0)
    glVertex2f(0.02,1)
    glVertex2f(-0.02,1)
    glEnd()

def LEAF():
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.03,0)
    glVertex2f(-0.03,0.75)
    glVertex2f(0.03,0)
    glEnd()

    glBegin(GL_TRIANGLES)
    glVertex2f(0.03,0)
    glVertex2f(0.03,0.75)
    glVertex2f(-0.03,0.75)
    glEnd()

### COMPLEX FIGURES =========================
# HOUSE, etc.
#
# Below are a series of procedures that draw the elements of a
# scene containing a house, a tree, and the sun.
#
def WINDOW():
    glColor(0.8,0.65,0.3)
    glPushMatrix()
    glScalef(0.2,0.2,0.2)
    BOX()
    glPopMatrix()
#
#
def DOOR():
    glPushMatrix()
    glScalef(0.3,0.18,0.2)
    RECT()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.15,0.35,0)
    glScalef(0.15,0.15,0.15)
    DISK()
    glPopMatrix()
#
#
def HOUSE():
    glColor(0.93,0.93,0.94)
    glPushMatrix()
    glScalef(0.9,1,0.9)
    DISK()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.1,-0.15,0.0)
    glColor(0.8,0.8,0.9)
    DOOR()
    glColor(0.3,0.3,0.4)
    glScalef(0.86,0.86,0.86)
    glTranslatef(0.01,0,0)
    DOOR()
    glPopMatrix()
#
#
def TREE():
    glColor(0.4,0.3,0.1)

    # Trunk
    glPushMatrix()
    glTranslatef(-0.5,0.0,0.0)
    BOX()
    glTranslatef(0.0,1.0,0.0)
    BOX()
    glTranslatef(0.0,1.0,0.0)
    BOX()
    glPopMatrix()

    # Pointy bit
    glColor(0.2,0.4,0.3)
    glPushMatrix()
    glTranslatef(0.0,1.5,0.0)
    glScalef(1.5,4,1)
    RTRI()
    glRotatef(90,0,0,1)
    RTRI()
    glPopMatrix()

    # Meow.
    glPushMatrix()
    glTranslatef(0,3,0)
    glScalef(1/6,1/6,1/6)
    glPushMatrix()
    glTranslatef(1,-1,0)
    glScalef(1.7,1.3,1)
    glRotatef(-100,0,0,1)
    glColor(0.57,0.27,0.17)
    DISK()
    glPopMatrix()
    glColor(0.6,0.3,0.2)
    DISK()
    glPushMatrix()
    glScalef(1.2,1.5,1.5)
    glTranslatef(0.2,0.67,0)
    glRotatef(-70,0,0,1)
    RTRI()
    glPopMatrix()
    glPushMatrix()
    glScalef(1.2,1.5,1.5)
    glTranslatef(-0.3,0.67,0)
    glRotatef(170,0,0,1)
    RTRI()
    glPopMatrix()
    glPopMatrix()
#
#   
def MOON():
    glColor(0.97,0.98,1)
    DISK()
    glPushMatrix()
    glTranslatef(0.3,0.2,0)
    glColor(0.12,0.1,0.2)
    DISK()
    glPopMatrix()

def YARD():
    glColor(0.90,0.90,0.92)
    glPushMatrix()
    glTranslate(5.0,0.0,0.0)
    glRotate(180,0.0,0.0,1.0)
    glScalef(10.0,10.0,10.0)
    BOX()
    glPopMatrix()

    glPushMatrix()
    glTranslate(4.0,0.0,0.0)
    glRotate(180,0.0,0.0,1.0)
    glScalef(10,0.9,10)
    glColor(0.92,0.92,0.94)
    BOX()
    glPopMatrix()

    glPushMatrix()
    glTranslate(4.0,0.0,0.0)
    glRotate(180,0.0,0.0,1.0)
    glScalef(10,0.4,10)
    glColor(0.94,0.94,0.96)
    BOX()
    glPopMatrix()

    glPushMatrix()
    glTranslate(4.0,0.0,0.0)
    glRotate(180,0.0,0.0,1.0)
    glScalef(10,0.1,10)
    glColor(0.96,0.96,0.98)
    BOX()
    glPopMatrix()


def SNOWPERSON():
    glColor(0.96,0.96,0.98)
    DISK()
    glTranslatef(0,1,0)
    glScalef(0.7,0.7,0.7)
    DISK()
    glTranslatef(0,1,0)
    glScalef(0.7,0.7,0.7)
    DISK()

    # Hat
    glPushMatrix()
    glTranslatef(-0.55,0.9,0)
    glScalef(1.1,0.9,1)
    glColor(0.5,0.1,0.15)
    BOX()
    glTranslatef(0,1,0)
    glRotatef(160,0,0,1)
    glScalef(1,1.2,1)
    glColor(0.6,0.5,0.3)
    SPINE()
    glPopMatrix()

    # Eyes
    glPushMatrix()
    glTranslatef(0.4,0.5,0.7)
    glScalef(0.2,0.2,0.2)
    glColor(0.1,0.1,0.1)
    DISK()
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.4,0.5,0.7)
    glScalef(0.2,0.2,0.2)
    glColor(0.1,0.1,0.1)
    DISK()
    glPopMatrix()


def simple():
    glTranslate(0.0,-0.5,0.0)

    glPushMatrix()
    glTranslatef(1.5,0.1,0)
    glScalef(0.15,0.15,0.15)
    SNOWPERSON()
    glPopMatrix()

    # Draw the house.
    glPushMatrix()
    glTranslatef(0.3,0,0)
    HOUSE()
    glPopMatrix()

    # Draw the yard.
    YARD()

    # Plant a happy little tree.
    glPushMatrix()
    glTranslate(-1.0,0.0,0.0)
    glScale(0.25,0.25,0.25)
    TREE()
    glPopMatrix()

    # Let there be light!
    glPushMatrix()
    glTranslate(-1.3,2.0,0.0)
    glScalef(0.15,0.15,0.15)
    MOON()
    glPopMatrix()

# Draw Sierpinski triangle
def sierpinski(depth):    
    if depth == 0:
        glColor(1,1,1)
        eqTRI()
    else:
        # Bottom left triangle
        glPushMatrix()
        glScalef(0.5,0.5,0.5)
        sierpinski(depth-1)
        glPopMatrix()

        # Top triangle
        glPushMatrix()
        glScalef(0.5,0.5,0.5)
        glTranslatef(cos(pi/3),sin(pi/3),0.0)
        sierpinski(depth-1)
        glPopMatrix()

        # Bottom right triangle
        glPushMatrix()
        glScalef(0.5,0.5,0.5)
        glTranslatef(1.0,0.0,0.0)
        sierpinski(depth-1)
        glPopMatrix()

# Draw Koch snowflake (main function)
def snowflake(depth):
    glPushMatrix()

    # Draw base triangle, centered in window
    glTranslatef(-cos(pi/6),-sin(pi/6),0)
    glScalef(2,2,2)
    glColor(1,1,1)
    eqTRI()
    
    # On the current side ( in the form of ____ or __/\__ ),
    # Koch_side(0) draws a triangle at 1/3rd scale of current frame (which is
    # the scale where the current side is length 1)

    # __ side
    glPushMatrix()
    glTranslatef(1,0,0)
    glRotatef(180,0,0,1)
    Koch_side(0)
    Koch_side(depth)
    glPopMatrix()

    # / side
    glPushMatrix()
    glRotatef(60,0,0,1)
    Koch_side(0)
    Koch_side(depth)
    glPopMatrix()

    # \ side
    glPushMatrix()
    glTranslatef(0.5,sin(pi/3),0)
    glRotatef(-60,0,0,1)
    Koch_side(0)
    Koch_side(depth)
    glPopMatrix()

    glPopMatrix()

# Koch snowflake recursive function
def Koch_side(depth):
    if depth == 0:
        glPushMatrix()
        glScalef(1/3,1/3,1/3)
        glTranslatef(1,0,0)
        glColor(1,1,1)
        eqTRI()
        glPopMatrix()
    else:
        # Leftmost triangle
        glPushMatrix()
        glScalef(1/3,1/3,1/3)
        Koch_side(0)
        Koch_side(depth-1)
        glPopMatrix()

        # Rightmost triangle
        glPushMatrix()
        glScalef(1/3,1/3,1/3)
        glTranslatef(2,0,0)
        Koch_side(0)
        Koch_side(depth-1)
        glPopMatrix()

        # Left angled triangle (on bigger triangle)
        glPushMatrix()
        glScalef(1/3,1/3,1/3)
        glTranslatef(1,0,0)
        glRotatef(60,0,0,1)
        Koch_side(0)
        Koch_side(depth-1)
        glPopMatrix()

        # Right angled triangle (on bigger triangle)
        glPushMatrix()
        glScalef(1/3,1/3,1/3)
        glTranslatef(1.5,sin(pi/3),0)
        glRotatef(-60,0,0,1)
        Koch_side(0)
        Koch_side(depth-1)
        glPopMatrix()

# Draw branched leaf/tree
def branched(depth,angle):
    if depth == 0:
        # Draw leaf
        glColor(0.2,0.6,0)
        LEAF()

    else:
        # Spine
        glPushMatrix()
        glColor(0.4,0.3,0.2)
        SPINE()
        glTranslatef(0,0.95,0)
        glScalef(0.8,0.8,0.8)
        glRotatef(angle/6,0,0,1)
        branched(depth-1,angle*0.9)
        glPopMatrix()

        # Left branch
        glPushMatrix()
        glTranslatef(0,1/4,0)
        glRotatef(angle,0,0,1)
        glScalef(0.8,0.8,0.8)
        branched(depth-1,angle*0.9)
        glPopMatrix()

        # Right branch
        glPushMatrix()
        glTranslatef(0,2/3,0)
        glRotatef(-angle,0,0,1)
        glScalef(0.8,0.8,0.8)
        branched(depth-1,angle*0.9)
        glPopMatrix()


def drawScene():
    """ Issue GL calls to draw the scene. """
    global levels,angle

    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT)

    # Clear the transformation stack.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if scene == 1:
        simple()
    elif scene == 2:
        # Sierpinski triangle, with frame scaled+translated
        # to center triangle with appropriate size in window
        glPushMatrix()
        glTranslatef(-cos(pi/6),-sin(pi/6),0)
        glScalef(2,2,2)
        sierpinski(levels)
        glPopMatrix()
    elif scene == 3:
        snowflake(levels)
    else:
        glPushMatrix()
        glTranslatef(0,-2,0)
        branched(levels,angle)
        glPopMatrix()

    # Render the scene.
    glFlush()


def myKeyFunc(key, x, y):
    """ Handle a "normal" keypress. """
    global scene,levels,angle

    # Handle the SPACE bar.
    if key == b' ':
        # Redraw.
        glutPostRedisplay()

    # Handle ESC key.
    if key == b'\033':	
	# "\033" is the Escape key
        sys.exit(1)

    # Handle recursion depth (+ and -)
    if key == b'-' and levels > 0:
        levels -= 1
        glutPostRedisplay()

    if (key == b'=' or key == b'+') and levels < 30:
        levels += 1
        glutPostRedisplay()


    # Handle branch angle ([ and ])
    if key == b'[' and angle > -90:
        angle -= 1
        glutPostRedisplay()

    if key == b']' and angle < 90:
        angle += 1
        glutPostRedisplay()

    # Scene selection (1-4 keys)
    if key == b'1':
        # Simple scene
        scene = 1 
        glutPostRedisplay()
    #
    if key == b'2':
        # Sierpinski
        scene = 2
        glutPostRedisplay()
    #
    if key == b'3':
        # Snowflake
        scene = 3
        glutPostRedisplay()
    #
    if key == b'4':
        # Fern
        scene = 4
        glutPostRedisplay()


def myArrowFunc(key, x, y):
    """ Handle a "special" keypress. """
    # Redraw.
    glutPostRedisplay()


def initRendering():
    """ Initialize aspects of the GL scene rendering.  """
    glClearColor(0.12, 0.1, 0.2, 1.0)


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

    glutInit(argv)
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(360, 360)
    glutCreateWindow( b'pretty scene - Press ESC to quit' )
    initRendering()

    # Register interaction callbacks.
    glutKeyboardFunc(myKeyFunc)
    glutSpecialFunc(myArrowFunc)
    glutReshapeFunc(resizeWindow)
    glutDisplayFunc(drawScene)

    print()
    print('Press +/- to change levels and [ and ] to change angle.')
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()

    return 0

if __name__ == '__main__': main(len(sys.argv),sys.argv)

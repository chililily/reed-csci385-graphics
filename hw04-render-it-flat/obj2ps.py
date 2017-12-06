#
# obj2ps.py
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# The main script for Homework 4.
#
# Usage:
#
#     python3 obj2ps.py <wavefront .obj file name>
#
#
# This will read in a surface model described in the
# provided .obj file. The object can then be oriented
# so as to position it for a snapshot. Finally, once
# the code in 'object.py' is completed, this will
# generate a Postscript rendering of the object when
# the . key is pressed.
#
# See the README file for more details on this 
# project.
#

import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from object import object, camera, face, vertex
from random import random
from math import sin, cos, acos, asin, pi, sqrt
from ctypes import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *

trackball = None
flashlight = None

floor_buffer = None
vertex_buffer = None
normal_buffer = None
bary_buffer = None

floor_shader = None
mesh_shader = None

fileroot = 'object'

xStart = 0
yStart = 0
width = 1000
height = 750
wireframe = False
snap = 0
ddd = 1.0

def init_shaders(vs_name,fs_name):
    """Compile the vertex and fragment shaders from source."""

    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader,open(vs_name,'r').read())
    glCompileShader(vertex_shader)
    result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
    if result:
        print('Vertex shader compilation successful.')
    else:
        print('Vertex shader compilation FAILED:')
        print(glGetShaderInfoLog(vertex_shader))
        sys.exit(-1)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, open(fs_name,'r').read())
    glCompileShader(fragment_shader)
    result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
    if result:
        print('Fragment shader compilation successful.')
    else:
        print('Fragment shader compilation FAILED:')
        print(glGetShaderInfoLog(fragment_shader))
        sys.exit(-1)

    shs = glCreateProgram()
    glAttachShader(shs,vertex_shader)
    glAttachShader(shs,fragment_shader)
    glLinkProgram(shs)

    return shs

def draw():
    """ Issue GL calls to draw the object. """

    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Clear the transformation stack.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glPushMatrix()

    glTranslatef(0.0,0.0,-2.0)

    # Transform the objects drawn below by a rotation.
    trackball.glRotate()

    glColor3f(0.5,0.4,0.35)
    glBegin(GL_TRIANGLES)
    glEnd()

    # * * * * * * * * * * * * * * * *
    # Draw all the triangular facets.
    shs = mesh_shader

    glUseProgram(shs)
    h_vertex =    glGetAttribLocation(shs,'vertex')
    h_normal =    glGetAttribLocation(shs,'normal')
    h_bary =      glGetAttribLocation(shs,'bary')
    h_light =     glGetUniformLocation(shs,'light')
    h_eye =       glGetUniformLocation(shs,'eye')
    h_wireframe = glGetUniformLocation(shs,'wireframe')

    # all the vertex positions
    glEnableVertexAttribArray(h_vertex)
    glBindBuffer (GL_ARRAY_BUFFER, vertex_buffer)
    glVertexAttribPointer(h_vertex, 3, GL_FLOAT, GL_FALSE, 0, None)
        
    # all the vertex normals
    glEnableVertexAttribArray(h_normal)
    glBindBuffer (GL_ARRAY_BUFFER, normal_buffer)
    glVertexAttribPointer(h_normal, 3, GL_FLOAT, GL_FALSE, 0, None)

    # all the vertex barycentric coordinates (for wireframe mesh)
    glEnableVertexAttribArray(h_bary)
    glBindBuffer(GL_ARRAY_BUFFER, bary_buffer)
    glVertexAttribPointer(h_bary, 3, GL_FLOAT, GL_FALSE, 0, None)
        
    # position of the flashlight
    light = flashlight.rotate(vector(0.0,0.0,1.0));
    glUniform3fv(h_light, 1, (4.0*light).components())

    # position of the viewer's eye
    eye = trackball.recip().rotate(vector(0.0,0.0,1.0))
    glUniform3fv(h_eye, 1, eye.components())

    # possible raise flag to show wireframe mesh
    glUniform1i(h_wireframe, 1 if wireframe else 0)

    glDrawArrays (GL_TRIANGLES, 0, len(face.instances) * 3)

    glDisableVertexAttribArray(h_vertex)
    glDisableVertexAttribArray(h_normal)
    glDisableVertexAttribArray(h_bary)

    glPopMatrix()

    # Render the object.
    glFlush()

    glutSwapBuffers()

def keypress(key, x, y):
    """ Handle a "normal" keypress. """

    global wireframe,snap,ddd

    if key == b'\033':	
	# "\033" is the Escape key
        sys.exit(1)
    
    if key == b' ':
        wireframe = not wireframe
        resize(width,height)
        glutPostRedisplay()

    if key == b'=':
        ddd += 0.1
        resize(width,height)
        glutPostRedisplay()

    if key == b'-':
        ddd -= 0.1
        resize(width,height)
        glutPostRedisplay()

    if key == b'.':

        print("Taking snapshot. Hold still...")

        eye = point.origin() + trackball.recip().rotate(vector(0.0,0.0,2.5))
        plane = point.origin() + trackball.recip().rotate(vector(0.0,0.0,2.0))
        up = trackball.recip().rotate(vector(0.0,1.0,0.0))
        right = trackball.recip().rotate(vector(1.0,0.0,0.0))
        away = trackball.recip().rotate(vector(0.0,0.0,1.0))

        name = fileroot+str(snap)+".ps"
        snap = snap + 1

        lines = object.toPS(name,camera(eye,plane,right,up,away))

        print("Wrote "+name+".")

        #sys.exit(1)
        
def arrow(key, x, y):
    """ Handle a "special" keypress. """
    global trackball,flashlight

    if key == GLUT_KEY_DOWN or key == GLUT_KEY_UP:
        axis = trackball.recip().rotate(vector(1.0,0.0,0.0))
    if key == GLUT_KEY_LEFT or key == GLUT_KEY_RIGHT:
        axis = trackball.recip().rotate(vector(0.0,1.0,0.0))
    if key == GLUT_KEY_LEFT or key == GLUT_KEY_DOWN:
        angle = -pi/12.0
    if key == GLUT_KEY_RIGHT or key == GLUT_KEY_UP:
        angle = pi/12.0

    if key in {GLUT_KEY_LEFT,GLUT_KEY_RIGHT,GLUT_KEY_UP,GLUT_KEY_DOWN}:
        # Apply an adjustment to the position of the light.
        flashlight = quat.for_rotation(angle,axis) * flashlight
        # Redraw.
        glutPostRedisplay()

def world(mousex,mousey):
    x = 2.0 * (mousex - width/2) / min(width,height)
    y = 2.0 * (height/2 - mousey) / min(width,height)
    return (x,y)

def mouse(button, state, x, y):
    global xStart, yStart
    
    # Start tracking mouse for trackball motion.
    xStart, yStart = world(x,y)

    glutPostRedisplay()

def motion(x, y):
    global trackball, xStart, yStart

    # Capture mouse's position.
    xNow, yNow = world(x,y)

    # Update trackball orientation based on movement.
    dx = xNow-xStart
    dy = yNow-yStart
    axis = vector(-dy,dx,0.0).unit()
    angle = asin(min(sqrt(dx*dx+dy*dy),1.0))
    trackball = quat.for_rotation(angle,axis) * trackball

    # Ready state for next mouse move.
    xStart = xNow
    yStart = yNow

    # Update window.
    glutPostRedisplay()

def init(filename):
    """ Initialize aspects of the GL object rendering.  """
    global \
    trackball, flashlight, \
    vertex_buffer, normal_buffer, bary_buffer, floor_buffer, \
    floor_shader, mesh_shader

    # Initialize quaternions for the light and trackball
    flashlight = quat.for_rotation(0.0,vector(1.0,0.0,0.0))
    trackball = quat.for_rotation(0.0,vector(1.0,0.0,0.0))

    # Read the .OBJ file into VBOs.
    object.read(filename)
    vertices, normals = object.compile()
    barys = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0] * len(face.instances)
    floor = [-2.0,-0.01,-2.0, -2.0,-0.01,+2.0, +2.0,-0.01,+2.0,
             +2.0,-0.01,+2.0, +2.0,-0.01,-2.0, -2.0,-0.01,-2.0]

    # Scene vertices, both floor and object.
    floor_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, floor_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(floor)*4, 
                  (c_float*len(floor))(*floor), GL_STATIC_DRAW)

    vertex_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(vertices)*4, 
                  (c_float*len(vertices))(*vertices), GL_STATIC_DRAW)

    # Object normals.
    normal_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, normal_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(normals)*4, 
                  (c_float*len(normals))(*normals), GL_STATIC_DRAW)

    # Object face barycenter determination.
    bary_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, bary_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(barys)*4, 
                  (c_float*len(barys))(*barys), GL_STATIC_DRAW)

    # Set up the shaders.
    floor_shader  = init_shaders('shaders/vs-floor.c',
                                 'shaders/fs-floor.c')
    mesh_shader   = init_shaders('shaders/vs-mesh.c',
                                 'shaders/fs-mesh.c')
                 
    # Set up OpenGL state.
    glEnable (GL_DEPTH_TEST)


def resize(w, h):
    """ Register a window resize by changing the viewport.  """
    global width, height, scale

    glViewport(0, 0, w, h)
    width = w
    height = h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    """
    if w > h:
        glOrtho(-w/h, w/h, -1.0, 1.0, 1.0, 3.0)
    else:
        glOrtho(-1.0, 1.0, -h/w, h/w, 1.0, 3.0)
    """
    if w > h:
        glFrustum(-w/h, w/h, -1.0, 1.0, 1.0, 3.0)
    else:
        glFrustum(-1.0, 1.0, -h/w, h/w, 1.0, 3.0)


def init_snaps(filename):
    global snap,fileroot

    fileroot = filename.split('/')[-1].split('.')[0]
    files = os.listdir(".")
    snap = 1
    for fn in files:
        if len(fn) > len(fileroot + ".ps"):
            if fn[:len(fileroot)] == fileroot and fn[-3:] == ".ps":
                try:
                    number = int(fn[len(fileroot):-3])
                    if number >= snap:
                        snap = number+1
                except:
                    pass
    

def run(filename):
    """ The main procedure, sets up GL and GLUT. """

    # Initialize the GLUT window.
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(width, height)
    glutCreateWindow( 'obj2ps - Press . to print or ESC to quit' )

    # Figure out the first snapshot name.
    init_snaps(filename)

    # Initialize the object viewer's state.
    init(filename)

    # Register interaction callbacks.
    glutKeyboardFunc(keypress)
    glutSpecialFunc(arrow)
    glutReshapeFunc(resize)
    glutDisplayFunc(draw)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)

    # Issue some instructions.
    print()
    print('Drag the object with the mouse to reorient it.')
    print('Use the arrow keys to move the light source.')
    print('Hit space to see the wireframe mesh.')
    print('Type . to generate a Postcript rendering.')
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()
    return 0


if len(sys.argv) > 1:
    run(sys.argv[1])
else:
    run('bunny.obj')

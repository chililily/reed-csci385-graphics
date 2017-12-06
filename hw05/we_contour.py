#
# we_contour.py
#
# HOMEWORK 5
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This is the main script for Homework 5. It opens up either a .obj
# file or a .pgm file, then reads it into a winged-half-edge data
# structure, an object of class 'surface'. There are two actions you
# can perform:
#
#   1. contour query
#
#   Click on the surface. A contour will be traced around the surface
#   at that click's y coordinate value. If SMOOTH_CONTOURS is set to
#   the contour will be drawn as a curve that approximates the lines
#   traced on the faceted surface. If instead set to False, the lines
#   themselves will be drawn.
#
#   2. surface walk
#   
#   By pressing 'w', you can switch into "walk mode."  In this mode,
#   the user can click on the surface to choose one of its faces. That
#   face will be highlighted in the display. If the user presses 'y'
#   and 'r' then a different, neighboring face will be highlighted.
#   The user can continue to walk on the surface in this way. By
#   pressing 't' the user can turn around on this walk.
#
# When in walk mode, an iso-elevation contour can still be traced
# by pressing '.'. It will be traced from the location of the 
# click that started that walk.
#
import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from surface import surface
from contour import contour
from polygon import draw_poly,vbo_poly
from random import random
from math import sin, cos, acos, asin, pi, sqrt
from ctypes import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *

ACCELERATED_CONTOURS = True
SMOOTH_CONTOURS = True
LINE_WIDTH = 0.0075

trackball = None
flashlight = None

contours = []
contour_vbos = []
vertex_buffer = None
normal_buffer = None
num_vertices = None
object = None

surface_shader = None
flat_shader = None

MODE_ALL = 0
MODE_TRON = 1
MODE_RIBBONS = 2
DRAW_MODES = 3
draw_mode = MODE_ALL

xStart = 0
yStart = 0
dragging = False
shoot = None
walk = None
walking = False

line_width = 2
line_scale = 0.005
smoov = False

width = 1000
height = 750

def init_shaders(vs_name,fs_name):
    """Compile the vertex and fragment shaders from source."""

    print("Compiling '"+vs_name+"' shader...")
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

    print("Compiling '"+fs_name+"' shader...")
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

def draw_triangles(tri_vbo,numv,color):

    glUseProgram(flat_shader)

    h_vertex = glGetAttribLocation(flat_shader,'vertex')
    glEnableVertexAttribArray(h_vertex)
    glBindBuffer (GL_ARRAY_BUFFER, tri_vbo)
    glVertexAttribPointer(h_vertex, 3, GL_FLOAT, GL_FALSE, 0, None)

    h_color  = glGetUniformLocation(flat_shader,'color')
    glUniform3fv(h_color, 1, color)

    glDrawArrays (GL_TRIANGLES, 0, numv)
    glDisableVertexAttribArray(h_vertex)

    glUseProgram(0)

def draw_contours():
    if ACCELERATED_CONTOURS:
        for cv in contour_vbos:
            (n,c) = cv
            draw_triangles(c,n,[0.6,0.3,0.45])
    else:
        for c in contours:
            glColor3f(0.6,0.3,0.45)
            if smoov:
                draw_poly(c.get_curve(),"x-z",line_width*line_scale,closed=c.closed)
            else:
                draw_poly(c.get_points(),"x-z",line_width*line_scale,closed=c.closed)

def draw_walk():

    def facet(f,fill=False):
        n = f.normal() * 0.01
        ps = f.points()
        if fill:
            glBegin(GL_POLYGON)
            (ps[0]+n).glVertex3()
            (ps[1]+n).glVertex3()
            (ps[2]+n).glVertex3()
            glEnd()
        else:
            glBegin(GL_LINE_STRIP)
            (ps[0]+n).glVertex3()
            (ps[1]+n).glVertex3()
            (ps[2]+n).glVertex3()
            (ps[0]+n).glVertex3()
            glEnd()
        
    if shoot != None:
        f = shoot[0]
        P = shoot[1]
        d = shoot[2]

        # highlight the shot face and the shot
        glColor3f(0.0,0.0,0.5)
        facet(shoot[0],True)
        glColor3f(0.3,0.3,1.0)
        glBegin(GL_LINE_STRIP)
        glVertex3f(P.x,P.y,P.z)
        glVertex3f(P.x+d.dx,P.y+d.dy,P.z+d.dz)
        glEnd()

    if walk != None:
        f = walk.face
        re,le = walk.next.twin,walk.prev.twin
        l = le.face if le != None else None
        r = re.face if re != None else None

        # highlight the walk face
        glColor3f(0.5,1.0,0.5)
        facet(f)

        # highlight the walk right face
        glColor3f(1.0,1.0,0.5)
        if r != None: facet(r)

        # highlight the walk left face
        glColor3f(1.0,0.5,0.5)
        if l != None: facet(l)


def draw_object():

    if draw_mode == MODE_ALL:
        # * * * * * * * * * * * * * * * *
        # BEGIN drawing of all the triangular facets.
        #
        #
        
        # * * *
        # A. Select which shaders we went to use
        glUseProgram(surface_shader)
        shs = surface_shader

        # * * *
        # B. Identify the variables in the shader code.
        h_vertex =    glGetAttribLocation(shs,'vertex')
        h_normal =    glGetAttribLocation(shs,'normal')
        h_light =     glGetUniformLocation(shs,'light')
        h_eye =       glGetUniformLocation(shs,'eye')
        
        # * * *
        # C. Associate buffers/values with those variables.
        
        # all the vertex positions
        glEnableVertexAttribArray(h_vertex)
        glBindBuffer (GL_ARRAY_BUFFER, vertex_buffer)
        glVertexAttribPointer(h_vertex, 3, GL_FLOAT, GL_FALSE, 0, None)

        # all the face normals
        glEnableVertexAttribArray(h_normal)
        glBindBuffer (GL_ARRAY_BUFFER, normal_buffer)
        glVertexAttribPointer(h_normal, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # position of the flashlight
        light = flashlight.rotate(vector(0.0,1.0,0.0));
        glUniform3fv(h_light, 1, (4.0*light).components())
    
        # position of the viewer's eye
        eye = trackball.recip().rotate(vector(0.0,0.0,1.0))
        glUniform3fv(h_eye, 1, eye.components())
    
        # * * *
        # D. Issue the geometry.
        glDrawArrays (GL_TRIANGLES, 0, num_vertices)
    
        # * * *
        # E. Disable some stuff.
        glDisableVertexAttribArray(h_vertex)
        glDisableVertexAttribArray(h_normal)
        glUseProgram(0)

    if draw_mode == MODE_TRON:
        draw_triangles(vertex_buffer,num_vertices,[0.05,0.05,0.1])

def draw():
    """ Issue GL calls to draw the object. """

    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set up the transformation stack.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glPushMatrix()
    glTranslatef(0.0,0.0,-2.0)
    trackball.glRotate()

    # Draw the scene.
    draw_contours()
    draw_walk()
    draw_object()

    glPopMatrix()

    # Render the effect of all the commands above.
    glFlush()
    glutSwapBuffers()

def add_contour(f,y):
    c = object.contour_at(f,y)
    if c != None:
        contours.append(c)
        if SMOOTH_CONTOURS:
            cv = vbo_poly(c.get_curve(),"x-z",LINE_WIDTH,closed=c.closed)
        else:
            cv = vbo_poly(c.get_points(),"x-z",LINE_WIDTH,closed=c.closed)
        contour_vbos.append(cv)

def keypress(key, x, y):
    """ Handle a "normal" keypress. """

    global shoot,walk,walking,draw_mode

    if key == b'\033':	
	# "\033" is the Escape key
        sys.exit(1)

    if key == b'o':
        draw_mode = (draw_mode + 1) % DRAW_MODES

    if key == b'w':
        walking = not walking
        if not walking:
            shoot = None
            walk = None

    if key == b't':
        if walk != None:
            walk = walk.twin

    if key == b'r':
        if walk != None:
            if walk.prev.twin != None:
                walk = walk.prev.twin

    if key == b'y':
        if walk != None:
            if walk.next.twin != None:
                walk = walk.next.twin
    
    glutPostRedisplay()

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
        flashlight = quat.for_rotation(angle,axis) * flashlight
        glutPostRedisplay()

def world(mousex,mousey):
    x = 2.0 * (mousex - width/2) / min(width,height)
    y = 2.0 * (height/2 - mousey) / min(width,height)
    return (x,y)

def mouse(button, state, x, y):
    global xStart, yStart, dragging, shoot, walk

    if state == 0:
        # Start tracking mouse for trackball motion.
        xStart, yStart = world(x,y)
        dragging = False

    else:
        if not dragging:
            wx,wy = world(x,y)

            x_axis = trackball.recip().rotate(vector(1.0,0.0,1.0))
            y_axis = trackball.recip().rotate(vector(0.0,1.0,0.0))
            z_axis = trackball.recip().rotate(vector(0.0,0.0,1.0))
            R = ORIGIN + (x_axis * wx + y_axis * wy + z_axis*4.0)
            d = -z_axis
            hits = object.hit_by(R,d)

            if hits != None:
                f = hits[0]
                P = hits[1]
                if walking:
                    shoot = (f,P,-d)
                    walk = f.edge
                else:
                    add_contour(f,P.y)
                    shoot = None
                    walk = None
            else:
                shoot = None
                walk = None

        dragging = False

    glutPostRedisplay()

def motion(x, y):
    global trackball, xStart, yStart, dragging

    # Capture mouse's position.
    xNow, yNow = world(x,y)

    # Update trackball orientation based on movement.
    dx = xNow-xStart
    dy = yNow-yStart
    dd = dx*dx + dy*dy 
    if dragging or (dd > 0.001):
        dragging = True
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
    num_vertices, vertex_buffer, normal_buffer, \
    object, \
    surface_shader, flat_shader

    # Initialize quaternions for the light and trackball
    flashlight = quat.for_rotation(0.0,vector(1.0,0.0,0.0))
    trackball  = quat.for_rotation(0.0,vector(1.0,0.0,0.0))

    # Read the .OBJ/.PGM file.
    if filename[-3:] == 'obj':
        object = surface.from_obj(filename)
    elif filename[-3:] == 'pgm':
        object = surface.from_pgm(filename)
    else:
        print("Unknown file format. Should be a .obj or .pgm file.\n")
        quit()
    
    # Get the information from the surface for the VBOs just below.
    num_vertices, vertices, normals = object.compile()

    # Surface vertices.
    vertex_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(vertices)*4, (c_float*len(vertices))(*vertices), GL_STATIC_DRAW)

    # Surface normals.
    normal_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, normal_buffer)
    glBufferData (GL_ARRAY_BUFFER, len(normals)*4, (c_float*len(normals))(*normals), GL_STATIC_DRAW)

    # Set up the shader(s).
    surface_shader = init_shaders('shaders/vs-surface.c','shaders/fs-surface.c')
    flat_shader = init_shaders('shaders/vs-flat.c','shaders/fs-flat.c')
                 
    # Set up OpenGL state.
    glEnable (GL_DEPTH_TEST)


def resize(w, h):
    """ Register a window resize by changing the viewport.  """
    global width, height

    glViewport(0, 0, w, h)
    width = w
    height = h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if w > h:
        glOrtho(-w/h, w/h, -1.0, 1.0, 1.0, 3.0)
    else:
        glOrtho(-1.0, 1.0, -h/w, h/w, 1.0, 3.0)

def run(filename):
    """ The main procedure, sets up GL and GLUT. """

    # Initialize the GLUT window.
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(width, height)
    glutCreateWindow( 'we contour - Press ESC to quit' )

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
    print('Use the arrow keys to move the light source.')
    print('Drag the object with the mouse to reorient it.')
    print('Click the mouse to choose a surface location.')
    print('If in tracing mode, a contour will be traced from that location.')
    print('If in walking mode, a face will be highlighted.')
    print()
    print('Press w to enter/leave walk mode.')
    print('Press r/y to walk forward.')
    print('Press t to turn forward.')
    print('Press . to trace a contour from the selected face.')
    print()
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()
    return 0


if len(sys.argv) > 1:
    run(sys.argv[1])
else:
    run('objs/bunny.obj')

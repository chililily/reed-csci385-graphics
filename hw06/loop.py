#
# loop.py
#
# HOMEWORK 6
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This is the main script for Homework 6. It opens up either an .obj
# file or a .pgm file, then reads it into a winged-half-edge data
# structure, an object of class 'surface'. There is one main action
# you can perform:
#
#   * a Loop subdivision refinement step
#
#   By pressing '.' you introduce a refined (smoother, more facets)
#   mesh model computed according to the subdivision rules you write
#   as a surface.refinement method.
#
# This is not yet implemented and, instead, gives you an empty surface
# for the refinement.
#
# Once you've correctly implemented the step, '.' extends a sequence
# of models with an additional refined surface. Hitting '-' and '+'
# allows you then to move amongst the refinements, either to coarser
# ones or to finer ones.
#
# Hitting SPACE allows you to see the mesh rather than just the surface.
#
import sys
from geometry import point, vector, EPSILON, ORIGIN
from quat import quat
from surface import surface
from random import random
from math import sin, cos, acos, asin, pi, sqrt
from ctypes import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *

ACCELERATED_CONTOURS = True
SMOOTH_CONTOURS = False
LINE_WIDTH = 0.0075

trackball = None
flashlight = None

models  = None
buffers = None

surface_shader = None

MODE_SURFACE = 0
MODE_MESH    = 1
DRAW_MODES   = 2
draw_mode = MODE_SURFACE

xStart = 0
yStart = 0
dragging = False

width = 1000
height = 750

current_level = 0
number_levels = 0

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

def draw_object():

    # * * * * * * * * * * * * * * * *
    # BEGIN drawing of all the triangular facets.
    #
    #
        
    # * * *
    # A. Select the shader we went to use
    glUseProgram(surface_shader)
    shs = surface_shader

    num_vertices  = buffers[current_level][0]
    vertex_buffer = buffers[current_level][1]
    normal_buffer = buffers[current_level][2]
    bary_buffer   = buffers[current_level][3]

    # * * *
    # B. Identify the variables in the shader code.
    h_vertex =    glGetAttribLocation(shs,'vertex')
    h_normal =    glGetAttribLocation(shs,'normal')
    h_bary =      glGetAttribLocation(shs,'bary')
    h_light =     glGetUniformLocation(shs,'light')
    h_eye =       glGetUniformLocation(shs,'eye')
    h_mesh =      glGetUniformLocation(shs,'wireframe')
        
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

    # all the face normals
    glEnableVertexAttribArray(h_bary)
    glBindBuffer (GL_ARRAY_BUFFER, bary_buffer)
    glVertexAttribPointer(h_bary, 3, GL_FLOAT, GL_FALSE, 0, None)
     
    # position of the flashlight
    light = flashlight.rotate(vector(0.0,1.0,0.0));
    glUniform3fv(h_light, 1, (4.0*light).components())
    
    # position of the viewer's eye
    eye = trackball.recip().rotate(vector(0.0,0.0,1.0))
    glUniform3fv(h_eye, 1, eye.components())
    
    # draw the wireframe of the mesh?
    glUniform1i(h_mesh, draw_mode)

    # * * *
    # D. Issue the geometry.
    glDrawArrays (GL_TRIANGLES, 0, num_vertices)
    
    # * * *
    # E. Disable some stuff.
    glDisableVertexAttribArray(h_vertex)
    glDisableVertexAttribArray(h_normal)
    glUseProgram(0)


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

    global draw_mode,current_level,number_levels

    if key == b'\033':	
	# "\033" is the Escape key
        sys.exit(1)

    if key == b' ':
        draw_mode = (draw_mode + 1) % DRAW_MODES

    if key == b'+' or key == b'=':
        current_level += 1
        if current_level >= number_levels:
            current_level = number_levels
        print("showing level",current_level,"of",number_levels)

    if key == b'_' or key == b'-':
        current_level -= 1
        if current_level < 0:
            current_level = 0
        print("showing level",current_level,"of",number_levels)

    if key == b'.':
        model  = models[number_levels]
        rmodel = model.refinement()
        models.append(rmodel)
        buffers.append(buffers_for_model(rmodel))
        number_levels += 1
        current_level = number_levels
        print("showing level",current_level,"of",number_levels)

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

def buffers_for_model(object):
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

    # Barycentric coordinate layout.
    bary_buffer = glGenBuffers(1)
    glBindBuffer (GL_ARRAY_BUFFER, bary_buffer)
    barys = [1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0] * (num_vertices // 3)
    glBufferData (GL_ARRAY_BUFFER, len(barys)*4, (c_float*len(barys))(*barys), GL_STATIC_DRAW)

    return (num_vertices,vertex_buffer,normal_buffer,bary_buffer)

def init(filename):
    """ Initialize aspects of the GL object rendering.  """
    global \
    trackball, flashlight, \
    models, buffers, \
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
    
    models  = [object]
    buffers = [buffers_for_model(object)]

    # Set up the shader(s).
    surface_shader = init_shaders('shaders/vs-mesh.c','shaders/fs-mesh.c')
                 
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
    glutCreateWindow( 'Loop subdivision - Press ESC to quit' )

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
    print()
    print('Press SPACE to change the display mode.')
    print('Press -/+ to display the coarser/finer model.')
    print('Press . to refine the mesh.')
    print()
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()
    return 0


if len(sys.argv) > 1:
    run(sys.argv[1])
else:
    run('objs/bunny.obj')

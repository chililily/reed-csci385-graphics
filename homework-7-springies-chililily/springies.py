#
# springies.py
#
# HOMEWORK 7
#
# Author: Jim Fix
# CSCI 385, Reed College, Fall 2017
#
# This is the script that runs Homeowrk 7. It begins with a
# blank 2D world where masses can be added (with mouse clicks)
# and springs can be added by dragging the mouse between two
# masses.
#
# When in EDITING mode, masses and springs can be moved around
# and deleted, and their attributes can be modified (weight for
# massed, resting length for springs).
#
# When in SIMULATION mode, and when you've completed the code,
# the masses will move according to the forces that act upon them.
# These forces include:
#
#    • A downward (-y) force due to GRAVITY.
#    • A slowdown (-velocity) force due to DAMPENING.
#    • Hooke's law force from masses connected by springs.
#
# Masses can be FIXED, in which case, they don't move.
#
# There is an additional pseudo-force used to make a spring-mass
# system act more like cloth: a DEFORMATION correction (which I
# denote "REFORM"). This prevents a spring from stretching beyond
# some ratio of its resting length.
#
# Modify the code so that it moves the positions of the masses
# according to a spring-mass simulation.
#
# This has you write these methods of Mass:
#
#     • euler_step
#     • compute_acceleration
#     • check_bounce
#
# that are used by the 'make_step' method. You may also rewrite
# 'make_step' completely if you like.
#
# It has you write these methods of Spring:
#
#     • force
#     • reform
#
# The first should be used by 'compute_acceleration' and the
# second is used to perform the cloth simulation tweak
# described in this paper:
#
# "Deformation Constraints in a Mass-Spring Model to Describe
#  Rigid Cloth Behavior" X. Provot, in Graphics Interface '95.
#
# This tweak simply moves unfixed masses so as to pull each 
# over-stratched spring's endpoints to a maximum stretch 
# (i.e. deformation) over its resting length. They describe
# the "overelasticity" problem and fix it in Section 5.
#
# With these methods completed, you should have a simulation
# similar to the one I showed in lecture.
#
import sys
from geometry import point, vector, EPSILON, ORIGIN
from ctypes import *
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT.freeglut import *

MOUSE_DOWN = 0
MOUSE_UP   = 1

MASS_SELECTED    = 0
SPRING_SELECTED  = 1
SPRING_BUILDING  = 2
MASS_MOVEMENT    = 3

MASS_THRESHOLD   = 0.05
SPRING_THRESHOLD = 0.05
MASS_INCREASE  = 1.1
SPRING_INCREASE  = 1.1

DAMPING   = 0.2
DEFORMATION = 1.25
GRAVITY     = 9.8

class GLOBALS:
    gravity_on       = True
    reform_on        = True

    time_step        = 1.0 / 500.0
    frame_rate       = 150

    paused           = True

    selected         = None
    why_selected     = None
    highlighted      = None

    last_mouse       = None
    
class Mass:
    def __init__(self, mass0, position0):
        self.mass        = mass0
        self.position0   = position0
        self.position    = position0
        self.velocity0   = vector(0.0,0.0,0.0)
        self.velocity    = vector(0.0,0.0,0.0)
        self.fixed       = False
        self.springs     = []
        Springies.masses.append(self)

    def get_position(self):
        return self.position

    def set_position(self,position):
        self.velocity = vector(0.0,0.0,0.0)
        self.position = position

    def is_fixed(self):
        return self.fixed

    def set_fixed(self, fxd):
        self.fixed = fxd

    def get_mass(self):
        return self.mass

    def set_mass(self, mss):
        self.mass = mss

    def add_spring(self,spring):
        self.springs.append(spring)

    def remove_spring(self,spring):
        self.springs.remove(spring)

    def snapshot(self):
        self.position0 = self.position
        self.velocity0 = self.velocity
        
    def delete(self):
        springs = self.springs[:]
        for spring in springs:
            spring.delete()
        Springies.masses.remove(self)

    def euler_step(self, time_step, acceleration):
        self.velocity = self.velocity0 + time_step*acceleration
        self.position = self.position0 + time_step*self.velocity0
        
    def compute_acceleration(self):
        Fg,Fd = vector(0.0,0.0,0.0),vector(0.0,0.0,0.0)

        if GLOBALS.gravity_on:
            Fg = vector(0.0,-self.mass*GRAVITY,0.0)
        if self.velocity0.norm() != 0:
            Fd = -DAMPING*(self.velocity0 / self.velocity0.norm())

        Fs = vector(0.0,0.0,0.0)

        for spring in self.springs:
            Fs += spring.force(self)

        F_net = Fs + Fd + Fg
        return F_net / self.mass

    def check_bounce(self):
        if self.position.y < -1.0:
            tbounce = GLOBALS.time_step*(-self.position0.y / self.velocity0.dy)
            pbounce = self.position0 + tbounce*self.velocity0
            self.position = pbounce + (GLOBALS.time_step - tbounce)*(-self.velocity0)
            self.velocity = self.velocity.neg()

    def make_step(self):
        if not self.fixed:
            acceleration = self.compute_acceleration()
            self.euler_step(GLOBALS.time_step, acceleration)
            self.check_bounce()
    
class Spring:
    def __init__(self,mass1,mass2,stiffness):
        self.mass = [mass1,mass2]
        mass1.add_spring(self)
        mass2.add_spring(self)
        self.stiffness = stiffness
        self.resting_length = self.get_length()
        Springies.springs.append(self)
        
    def force(self,on_mass):
        assert(on_mass == self.mass[0] or on_mass == self.mass[1])

        direction = self.mass[1].get_position() - self.mass[0].get_position()
        direction /= direction.norm()

        k = (self.get_length() - self.get_resting_length()) / self.get_resting_length()
        if on_mass != self.mass[0]:
            direction = direction.neg()

        return k*direction
    
    def reform(self):
        if self.get_deformation() > DEFORMATION:
            direction = self.mass[1].get_position() - self.mass[0].get_position()
            midpoint = self.mass[0].position + 0.5*direction
            direction /= direction.norm()
            scale = DEFORMATION*self.get_resting_length()

            if not (self.mass[1].fixed or self.mass[0].fixed):
                scale /= 2
                self.mass[1].position = midpoint + scale*direction
                self.mass[0].position = midpoint + (-scale*direction)
            elif self.mass[0].fixed:
                self.mass[1].position = self.mass[0].position + scale*direction
            else:
                self.mass[0].position = self.mass[1].position + (-scale*direction)
            
    def center(self):
        point0 = self.mass[0].get_position()
        point1 = self.mass[1].get_position()
        return point0.combo(0.5,point1)

    def get_length(self):
        return (self.mass[1].get_position() - self.mass[0].get_position()).norm()

    def get_resting_length(self):
        return self.resting_length

    def set_resting_length(self,length):
        self.resting_length = length

    def get_deformation(self):
        return self.get_length() /  self.resting_length

    def delete(self):
        self.mass[0].remove_spring(self)
        self.mass[1].remove_spring(self)
        Springies.springs.remove(self)
        
class Springies:

    masses  = []
    springs = []

    def closest_mass_to(location):
        minimum = None
        minimum_mass = None
        for mass in Springies.masses:
            distance = (mass.get_position() - location).norm()
            if minimum_mass == None or distance < minimum:
                minimum = distance
                minimum_mass = mass
        return (minimum,minimum_mass)

    def closest_spring_to(location):
        minimum = None
        minimum_spring = None
        for spring in Springies.springs:
            distance = (spring.center() - location).norm()
            if minimum_spring == None or distance < minimum:
                minimum = distance
                minimum_spring = spring
        return (minimum,minimum_spring)

    def update():

        for mass in Springies.masses:
            mass.snapshot()

        for mass in Springies.masses:
            mass.make_step()

        if GLOBALS.reform_on:
            for spring in Springies.springs:
                spring.reform()


HIGHLIGHT_LINE_WIDTH = 0.05
LINE_WIDTH           = 0.03
HIGHLIGHT_MASS_SIZE  = 0.13
MASS_SIZE            = 0.1

WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 750

def draw_line(start, end, width):
    v = (end-start).unit() * width / 2.0
    ov = vector(-v.dy,v.dx,v.dz)
    iv = -ov

    op = start + ov
    ip = start + iv
    oq = end + ov
    iq = end + iv
    
    glBegin(GL_TRIANGLES)

    ip.glVertex3()
    op.glVertex3()
    oq.glVertex3()

    oq.glVertex3()
    iq.glVertex3()
    ip.glVertex3()

    glEnd()

def draw_disk(center,radius):
    glBegin(GL_POLYGON)
    a = 0.0
    sides = 16
    da = 2.0 * math.pi / sides

    while a < 2.0 * math.pi:
        glVertex3f(center.x + radius*math.cos(a), center.y + radius*math.sin(a), center.z)
        a += da
    glEnd()

def draw_mass(mass,size,color,level):
    p = point.with_components(mass.get_position().components())
    p.z = 0.1 * level
    glColor3f(color[0],color[1],color[2])
    draw_disk(p,size/2.0*mass.get_mass())

def draw_spring(spring,size,color,level):
    p = point.with_components(spring.mass[0].get_position().components())
    q = point.with_components(spring.mass[1].get_position().components())
    p.z = 0.1 * level
    q.z = 0.1 * level
    glColor3f(color[0],color[1],color[2])
    deform = max(min(spring.get_deformation(),10.0),0.333333)
    draw_line(p,q,size/deform)
    
def draw():
    """ Issue GL calls to draw the object. """

    # Clear the rendering information.
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set up the transformation stack.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glPushMatrix()

    if GLOBALS.selected != None and GLOBALS.why_selected == SPRING_SELECTED:
        draw_spring(GLOBALS.selected, HIGHLIGHT_LINE_WIDTH, (0.7,0.4,0.4), -2)

    if GLOBALS.highlighted != None and isinstance(GLOBALS.highlighted,Spring):
        draw_spring(GLOBALS.highlighted, HIGHLIGHT_LINE_WIDTH, (0.7,0.7,0.4), -1)

    if GLOBALS.selected != None and GLOBALS.why_selected == SPRING_BUILDING:
        p = GLOBALS.selected.get_position()
        if GLOBALS.highlighted != None:
            q = GLOBALS.highlighted.get_position()
        else:
            q = GLOBALS.last_mouse
        draw_line(p, q, HIGHLIGHT_LINE_WIDTH)

    # Draw springs, included selected/highlighted ones.
    for spring in Springies.springs:
        draw_spring(spring, LINE_WIDTH, (0.5,0.8,0.3), 1)

    if GLOBALS.highlighted != None and isinstance(GLOBALS.highlighted,Mass):
        draw_mass(GLOBALS.highlighted, HIGHLIGHT_MASS_SIZE, (0.7,0.7,0.4), 2)

    if GLOBALS.selected != None and GLOBALS.why_selected == MASS_MOVEMENT:
        draw_mass(GLOBALS.selected, HIGHLIGHT_MASS_SIZE, (0.7,0.4,0.4), 3)

    # Draw masses, included selected/highlighted ones.
    for mass in Springies.masses:
        if mass.is_fixed():
            draw_mass(mass, MASS_SIZE, (0.2,0.3,0.15), 4)
        else:
            draw_mass(mass, MASS_SIZE, (0.3,0.6,0.3), 4)

    glPopMatrix()
    glFlush()
    glutSwapBuffers()

def keypress(key, x, y):
    """ Handle a "normal" keypress. """

    if key == b'\033':	
        sys.exit(1)

    if (key == b'g' or key == b'G') and not GLOBALS.paused:
        GLOBALS.gravity_on = not GLOBALS.gravity_on

    if (key == b'd' or key == b'D') and not GLOBALS.paused:
        GLOBALS.reform_on = not GLOBALS.reform_on

    if key == b' ':
        if GLOBALS.selected == None:
            GLOBALS.paused = not GLOBALS.paused

    if GLOBALS.paused:
        if key == b'\x7f':
            if GLOBALS.selected != None:
                GLOBALS.selected.delete()
                GLOBALS.selected = None
                GLOBALS.highlighted = None

        if key == b'.':
            if GLOBALS.selected != None:
                if GLOBALS.why_selected == MASS_MOVEMENT:
                    GLOBALS.selected.set_fixed(not GLOBALS.selected.is_fixed())
                    GLOBALS.selected = None
                    GLOBALS.highlighted = None

        if key == b'=' or key == b'+':
            if GLOBALS.selected != None:
                if GLOBALS.why_selected == MASS_MOVEMENT:
                    m = GLOBALS.selected.get_mass()
                    GLOBALS.selected.set_mass(m * MASS_INCREASE)
                elif GLOBALS.why_selected == SPRING_SELECTED:
                    l = GLOBALS.selected.get_resting_length()
                    GLOBALS.selected.set_resting_length(l * SPRING_INCREASE)

        if key == b'-' or key == b'_':
            if GLOBALS.selected != None:
                if GLOBALS.why_selected == MASS_MOVEMENT:
                    m = GLOBALS.selected.get_mass()
                    GLOBALS.selected.set_mass(m / MASS_INCREASE)
                elif GLOBALS.why_selected == SPRING_SELECTED:
                    l = GLOBALS.selected.get_resting_length()
                    GLOBALS.selected.set_resting_length(l / SPRING_INCREASE)

    glutPostRedisplay()


def world(mousex,mousey):
    x = 2.0 * (mousex - WINDOW_WIDTH/2.0) / min(WINDOW_WIDTH,WINDOW_HEIGHT)
    y = 2.0 * (WINDOW_HEIGHT/2.0 - mousey) / min(WINDOW_WIDTH,WINDOW_HEIGHT)
    return (x,y)


def mouse(button, state, x, y):

    wx, wy = world(x,y)
    wp = point(wx,wy,0.0)

    if not GLOBALS.paused:
        return

    if state == MOUSE_DOWN:
        if GLOBALS.selected != None and GLOBALS.why_selected == MASS_MOVEMENT:
            # If it's the second click in a mouse movement, let go.
            GLOBALS.selected.set_position(wp)
            GLOBALS.selected = None
        elif GLOBALS.selected != None and GLOBALS.why_selected == SPRING_SELECTED:
            GLOBALS.selected = None
        elif GLOBALS.selected == None:
            # If it's a fresh click then...
            how_close_mass, which_mass = Springies.closest_mass_to(wp)
            how_close_spring, which_spring = Springies.closest_spring_to(wp)
            if which_mass != None and how_close_mass < MASS_THRESHOLD:
                # ...start moving a mass.
                GLOBALS.selected = which_mass
                GLOBALS.why_selected = MASS_MOVEMENT
            elif which_spring != None and how_close_spring < SPRING_THRESHOLD:
                # ...select a spring for editing.
                GLOBALS.selected = which_spring
                GLOBALS.why_selected = SPRING_SELECTED
            else:
                # ...otherwise create a new mass and start moving it.
                Mass(1.0,wp)
        
    elif state == MOUSE_UP:
        if GLOBALS.selected != None and GLOBALS.why_selected == SPRING_BUILDING:
            # If we're building a spring, see if we're near an existing mass.
            mass1 = GLOBALS.selected
            how_close_mass, which_mass = Springies.closest_mass_to(wp)
            if how_close_mass != None and which_mass != mass1 and how_close_mass < MASS_THRESHOLD:
                mass2 = which_mass
                Spring(mass1,mass2,1000.0)
                GLOBALS.selected = None
            else:
                GLOBALS.selected = None

    glutPostRedisplay()


def drag(x, y):

    wx, wy = world(x,y)
    wp = point(wx,wy,0.0)

    GLOBALS.highlighted = None
    if GLOBALS.selected != None and GLOBALS.why_selected == SPRING_BUILDING:
        how_close_mass, which_mass = Springies.closest_mass_to(wp)
        if how_close_mass < MASS_THRESHOLD:
            GLOBALS.highlighted = which_mass
        else:
            GLOBALS.last_mouse = wp

    elif GLOBALS.selected != None and GLOBALS.why_selected == MASS_MOVEMENT:
        if (wp - GLOBALS.selected.get_position()).norm() > 0.1:
            GLOBALS.why_selected = SPRING_BUILDING
            GLOBALS.last_mouse = wp
    
    glutPostRedisplay()


def move(x, y):

    wx, wy = world(x,y)
    wp = point(wx,wy,0.0)

    if not GLOBALS.paused:
        return

    GLOBALS.highlighted = None
    if GLOBALS.selected == None:
        how_close_mass, which_mass = Springies.closest_mass_to(wp)
        how_close_spring, which_spring = Springies.closest_spring_to(wp)
        if which_mass != None and how_close_mass < MASS_THRESHOLD:
            GLOBALS.highlighted = which_mass
        elif which_spring != None and how_close_spring < SPRING_THRESHOLD:
            GLOBALS.highlighted = which_spring
    elif GLOBALS.why_selected == SPRING_BUILDING:
        how_close_mass, which_mass = Springies.closest_mass_to(wp)
        if how_close_mass != None and how_close_mass != GLOBALS.selected and how_close_mass < MASS_THRESHOLD:
            GLOBALS.highlighted = which_mass
    elif GLOBALS.why_selected == MASS_MOVEMENT:
        GLOBALS.selected.set_position(wp)

    glutPostRedisplay()


def init():
    """ Initialize aspects of the GL object rendering.  """
    glEnable (GL_DEPTH_TEST)


def resize(w, h):
    """ Register a window resize by changing the viewport.  """
    global WINDOW_WIDTH, WINDOW_HEIGHT

    glViewport(0, 0, w, h)
    WINDOW_WIDTH = w
    WINDOW_HEIGHTt = h

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if w > h:
        glOrtho(-w/h, w/h, -1.0, 1.0, -1.0, 1.0)
    else:
        glOrtho(-1.0, 1.0, -h/w, h/w, -1.0, 1.0)

def simulation_step(time):

    if not GLOBALS.paused:
        Springies.update()
        if time % GLOBALS.frame_rate == 0:
            time = 0
            glutPostRedisplay()
        else:
            time = time + 1

    glutTimerFunc(1, simulation_step, time)


def run():
    """ The main procedure, sets up GL and GLUT. """

    # Initialize the GLUT window.
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowPosition(0, 20)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow( '(cloth) SPRINGIES!!! - Press ESC to quit' )

    # Initialize the object viewer's state.
    init()

    # Register interaction callbacks.
    glutKeyboardFunc(keypress)
    glutReshapeFunc(resize)
    glutDisplayFunc(draw)
    glutMouseFunc(mouse)
    glutMotionFunc(drag)
    glutPassiveMotionFunc(move)
    glutTimerFunc(0, simulation_step, 0)

    # Issue some instructions.
    print()
    print()
    print()
    print('•-/////-•-/////-•-/////-•-/////-•-/////-•-/////-•-/////-•')
    print('                                                         ')
    print('  WELCOME to SPRINGIES! (w/ thanks to Douglas DeCarlo.)  ')
    print('                                                         ')
    print('•-/////-•-/////-•-/////-•-/////-•-/////-•-/////-•-/////-•')
    print()
    print('Click the mouse add a mass.')
    print('Drag the mouse from one mass to another to make spring.')
    print('Press SPACE to start/pause the simulation.')
    print()
    print('Clicking on a highlighted mass or spring (YELLOW) will select it.')
    print()
    print('When a mass is selected (RED highlight):')
    print('   Moving the mouse will place it elsewhere.')
    print('   Pressing DELETE will remove the mass.')
    print('   Pressing +/- will increase/decrease its mass.')
    print('   Pressing . will toggle its fixedness and deselect it.')
    print('   Clicking will deslect it.')
    print()
    print('When a spring is selected (RED highlight):')
    print('   Pressing DELETE will remove the spring.')
    print('   Pressing +/- will increase/decrease its resting length.')
    print('   Clicking will deslect it.')
    print()
    print('Hit G to toggle gravity off/on.')
    print('Hit D to toggle cloth deformation off/on.')
    print()
    print('Press ESC to quit.\n')
    print()

    glutMainLoop()
    return 0

run()

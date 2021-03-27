# Homework 7: springies

*Due: 12/14/2017*

For this assignment I'd like you to complete the code for a spring-mass
simulation. You've been provided a basic editor that lets you add point
masses to a 2-D world and then connect them in pairs with virtual
springs. Your job is to write the code that animates them using
the numeric integration techniques we discussed in class (a first-order
Euler method suffices), assuming that the springs exert forces,
according to Hooke's law, on the masses at their endpoints. Your code
will be employed to make a series of updates to the positions of all
the masses in the world, frame by frame, according to spring-mass
physics. The calculations are performed quickly and accurately enough 
so that the successive frames make them appear to be falling and 
moving around almost in real time, though a bit more like in a 1/5th-speed
slow motion.

The goal here is to give you a taste of numeric simulation, and
to give you the opportunity to play a bit to see how touchy the tuning
of a simulation can be.

## The Starting Code

This folder contains few files. There is just the main script 
`springies.py` along with the usual supporting `geometry.py`. There are
no shaders, no geometry files to load, and the data structure is
simple enough (essentially an undirected graph) that I decided to
put them in the same file as the GL and GLUT code. 

You might just scan through the `springies.py` code now to see what's
there. The key components you'll need to modify are at the near
top---there are a few methods of the class `Mass` that you'll need to
complete, and there a few methods of the class `Spring` that you'll
need to complete. The remainder of this code handles the following:
drawing the springs and masses (including which have been selected
and/or are near the mouse pointer), handling mouse and keyboard
interactions during editing, and setting up all the GLUT event
handlers to glue everything together.

I'd look a bit at the three key classes you will work with: `Mass`,
`Spring`, `GLOBALS`, and `Springies`.  The last two are never
instantiated. Rather, they contain the global variables and the
functions that make the simulation happen. The first two classes model
the nodes and the edges of the spring-mass network that the user
creates.  The main simulation function `Springies.update` uses their
methods to do this, once with each simulated time step. It performs
the following:

* Takes a "snapshot" of each mass's position and velocity. You might
find this useful if you go beyond Euler integration (say, 4th order
Runge-Kutta), but it can be useful in managing the Euler step 
calculation, too. (`Mass.snapshot`)

* Modifies the positions and velocities of all the masses with an
Euler integration step. We'll describe what this requires below.
(`Mass.make_step`) 

* Then (maybe) "tweaks" each mass's position to prevent "overelasticity"
as described in the paper by Provot. This involves visiting each
spring and checking its "deformation." (`Spring.reform`)

## Interaction

You should also try running the code with the command

	python3 springies.py

This will bring up the siulation's world and put it in editor mode. A
brief guide to the program will get printed in the console. You can
poke around a bit to get a feel for editing. Click the mouse a few
times to create some masses. Drag the mouse from one mass to another
to add a spring. Click on a mass to select it, and then move it around
with the mouse (and hit keys to edit it). With the keyboard you can
change its weight, make it fixed or free, or delete it.  Click on the
center of a spring to select it. You can change its resting length or
delete the spring.

Hitting the SPACE bar will set the simulation in motion and animate
it. Right now, though, the masses will not change their position at
all. The simulation code needs to be written by you for this animation
to run.

## The Assignment

**Write the code** of the methods that support the `Mass.make_step` method.
There are three to write:

• compute_acceleration  
• euler_step  
• check_bounce  

`compute_acceleration`

The first computes all the forces that apply to that mass. There are three
forces that you should at least include:

1. Damping. In order to keep the numeric problems of using Euler's method
at bay, we skim a little off the top of a mass's velocity. To do this,
you include a force in the opposite direction of its `velocity` vector.
You can use the constant `DAMPING` defined at the top of the script (at
least that value worked for my solution).

2. Gravity. This is a downward force on the particle. You can scale it
by the mass's mass times the `GRAVITY` constant. You only want to do this
if `GLOBALS.gravity_on` is set.

3. Hooke's Law spring forces. Each spring connected to this mass gets
pulls it with a force proportional to the stretch/compression of the
spring from its resting length. If the spring is three times its
resting length, it pulls the mass towards the connected mass twice
as much as it would if the spring were twice its resting length. That is,
the force (by Hooke's Law) is proportional to
*(length - resting_length) / resting_length*. It pushes the mass away
from the other mass when the spring is compressed, that is, when
*length - resting_length* is negative.

For (3), I encourage you to **write the code** for the method
`Spring.force`. This code is used to "ask" the spring to compute the
Hooke's Law force for a mass, based on its position relative to the
other connected mass.

We sum up all these forces, adding the vector components of damping
plus gravity, plus the force due to each of the connected springs.

`euler_step`

For the Euler step, we update the `position` and `velocity` of the mass
using a Taylor first approximation:  *f(t+h) = f(t) + h f'(t)*.
So, for example, the `position` is bumped by the `velocity` scaled by
`GLOBALS.time_step`.

`check_bounce`

To keep things somewhat controlled, we simulate a floor by checking whether
or not the mass has moved to a position with *y* value smaller than -1.0.
You need to modify the position and the velocity of the mass to account
for this floor bounce. If the `euler_step` puts it below the floor, 
move it to a place where it has instead bounced off the floor, it sits above
the floor, and is instead heading in the opposite direction.

Lastly, I'd like you to **implement deformation constraints** according to
the Provot paper (linked on the course web site).  In that paper, Provot
proposes putting a limit on the deformation of any spring. He does this
in a fairly *ad hoc* way. He compares the ratio of a spring's length to
its resting length. If that ratio is too large (you can compare that with
the `DEFORMATION` constant I define at the top of the script) then he
simply moves the spring's two endpoint masses closer to the spring's 
center so that the length meets this deformed ratio. (If only one
of the masses is free, and the other is `fixed`, then we yoy just move the
free mass.)

We do this in the `Spring.reform` method which fixes the deformation problem.

## Alternatives

This is a fairly prescribed assignment since we have hit the end of the
semester. If you happen to have the time to do so, feel free to instead go 
"off script" a bit. You could instead perform a spring-mass simulation
with an .OBJ file's surface, or a terrain, or make a 3-D cube of Jell-O(tm).
As long as you build a spring-mass simulation similar to what is described
just above you will have met the requirements of the assignment.  

Or add whatever features you like to this simulation. Feel free to play
a bit if you like. Being able to save and restore spring-mass arrangements
would be nice, for example. Making the simulation more accurate with a
higher-order integration step would be a good challenge.

If you are feeling ambitious, you could instead see whether you can get 
GLSL shaders to do the calculations (for a regular grid of masses)
instead.

## Submitting your work

Once again, commit and push the changes you've made to the starting
repository for this assignment. Update this README or 
a `submitted.md` file so I learn about the work that you've done.

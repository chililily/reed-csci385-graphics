#
# object.py
#
# Defines an RGB struct 'class color'.
# Defines a three-vertex struct 'class facet', that also has a color attribute.
# Defines a function 'make_object' that produces a list of facets.
#

from geometry import point,vector
from random import uniform,random
from math import sin, cos, tan, pi
from numpy import dot

class color:
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b


class facet:

    def __init__(self, _p0,_p1,_p2, _m):
        self.vertices = [_p0,_p1,_p2]
        self.material = _m

    def __getitem__(self,i):
        return self.vertices[i]


def make_tetra():

    # Make a tetrahedron.

    fs = []

    # missing ---
    c0  = color(1.0,1.0,0.0)
    p00 = point.with_components( [ 1.0,-1.0, 1.0] )
    p01 = point.with_components( [ 1.0, 1.0,-1.0] )
    p02 = point.with_components( [-1.0, 1.0, 1.0] )
    f0  = facet(p00,p01,p02,c0) 
    fs.append(f0)

    # missing ++-
    c1  = color(0.0,1.0,1.0)
    p10 = point.with_components( [ 1.0,-1.0, 1.0] )
    p11 = point.with_components( [-1.0, 1.0, 1.0] )
    p12 = point.with_components( [-1.0,-1.0,-1.0] )
    f1  = facet(p10,p11,p12,c1) 
    fs.append(f1)

    # missing -++
    c2  = color(1.0,0.0,1.0)
    p20 = point.with_components( [-1.0,-1.0,-1.0] )
    p21 = point.with_components( [ 1.0, 1.0,-1.0] )
    p22 = point.with_components( [ 1.0,-1.0, 1.0] )
    f2  = facet(p20,p21,p22,c2) 
    fs.append(f2)

    # missing +-+
    c3  = color(1.0,1.0,1.0)
    p30 = point.with_components( [ 1.0, 1.0,-1.0] )
    p31 = point.with_components( [-1.0,-1.0,-1.0] )
    p32 = point.with_components( [-1.0, 1.0, 1.0] )
    f3  = facet(p30,p31,p32,c3) 
    fs.append(f3)

    return fs

def make_cube():
    fs = []

    # Time/energy permitting -- iterate

    c0  = color(0.25,0.0,0.0)
    p00 = point.with_components( [ 1.0,-1.0, 1.0] )
    p01 = point.with_components( [-1.0,-1.0, 1.0] )
    p02 = point.with_components( [-1.0, 1.0, 1.0] )
    f0  = facet(p00,p01,p02,c0) 
    fs.append(f0)

    c1  = color(0.5,0.0,0.0)
    p10 = point.with_components( [ 1.0,-1.0, 1.0] )
    p11 = point.with_components( [ 1.0, 1.0, 1.0] )
    p12 = point.with_components( [-1.0, 1.0, 1.0] )
    f1  = facet(p10,p11,p12,c1) 
    fs.append(f1)

    c2  = color(0.75,0.0,0.0)
    p20 = point.with_components( [ 1.0,-1.0,-1.0] )
    p21 = point.with_components( [ 1.0, 1.0, 1.0] )
    p22 = point.with_components( [ 1.0,-1.0, 1.0] )
    f2  = facet(p20,p21,p22,c2) 
    fs.append(f2)

    c3  = color(1.0,0.0,0.0)
    p30 = point.with_components( [ 1.0, 1.0,-1.0] )
    p31 = point.with_components( [ 1.0,-1.0,-1.0] )
    p32 = point.with_components( [ 1.0, 1.0, 1.0] )
    f3  = facet(p30,p31,p32,c3) 
    fs.append(f3)

    c4  = color(0.0,0.25,0.0)
    p40 = point.with_components( [ 1.0, 1.0, 1.0] )
    p41 = point.with_components( [-1.0, 1.0,-1.0] )
    p42 = point.with_components( [-1.0, 1.0, 1.0] )
    f4  = facet(p40,p41,p42,c4) 
    fs.append(f4)

    c5  = color(0.0,0.5,0.0)
    p50 = point.with_components( [ 1.0, 1.0,-1.0] )
    p51 = point.with_components( [-1.0, 1.0,-1.0] )
    p52 = point.with_components( [ 1.0, 1.0, 1.0] )
    f5  = facet(p50,p51,p52,c5) 
    fs.append(f5)

    c6  = color(0.0,0.75,0.0)
    p60 = point.with_components( [-1.0, 1.0,-1.0] )
    p61 = point.with_components( [-1.0,-1.0,-1.0] )
    p62 = point.with_components( [-1.0,-1.0, 1.0] )
    f6  = facet(p60,p61,p62,c6) 
    fs.append(f6)

    c7  = color(0.0,1.0,0.0)
    p70 = point.with_components( [-1.0, 1.0,-1.0] )
    p71 = point.with_components( [-1.0,-1.0, 1.0] )
    p72 = point.with_components( [-1.0, 1.0, 1.0] )
    f7  = facet(p70,p71,p72,c7) 
    fs.append(f7)

    c8  = color(0.0,0.0,0.25)
    p80 = point.with_components( [-1.0,-1.0,-1.0] )
    p81 = point.with_components( [ 1.0,-1.0, 1.0] )
    p82 = point.with_components( [-1.0,-1.0, 1.0] )
    f8  = facet(p80,p81,p82,c8) 
    fs.append(f8)

    c9  = color(0.0,0.0,0.5)
    p90 = point.with_components( [ 1.0,-1.0,-1.0] )
    p91 = point.with_components( [ 1.0,-1.0, 1.0] )
    p92 = point.with_components( [-1.0,-1.0,-1.0] )
    f9  = facet(p90,p91,p92,c9) 
    fs.append(f9)

    c10  = color(0.0,0.0,0.75)
    p100 = point.with_components( [-1.0, 1.0,-1.0] )
    p101 = point.with_components( [-1.0,-1.0,-1.0] )
    p102 = point.with_components( [ 1.0,-1.0,-1.0] )
    f10  = facet(p100,p101,p102,c10) 
    fs.append(f10)

    c11  = color(0.0,0.0,1.0)
    p110 = point.with_components( [ 1.0,-1.0,-1.0] )
    p111 = point.with_components( [-1.0, 1.0,-1.0] )
    p112 = point.with_components( [ 1.0, 1.0,-1.0] )
    f11  = facet(p110,p111,p112,c11) 
    fs.append(f11)

    return fs

def make_cyl(s):

    fs = []
    step = 3+s

    # Center points of circular faces (front and back) in the x-y plane
    ccf = point.with_components( [ 0.0, 0.0, 1.0] )
    ccb = point.with_components( [ 0.0, 0.0,-1.0] )

    # Constructs triangle mesh by looping completely around a circle using a specified number of steps (sides).
    # Each loop specifies 4 points, two on the front circle and two on the back;
    # then two facets are made using the center point of a circular face and the two corresponding points.
    # Another two facets are made for the cylinder's sides by dividing the rectangle of 4 specified points in half.
    for i in range(0,step):
        x_i = cos(2*pi*i/step)
        x_j = cos(2*pi*(i+1)/step)
        y_i = sin(2*pi*i/step)
        y_j = sin(2*pi*(i+1)/step)
        pf_i = point.with_components( [ x_i, y_i, 1] )
        pf_j = point.with_components( [ x_j, y_j, 1] )
        pb_i = point.with_components( [ x_i, y_i,-1] )
        pb_j = point.with_components( [ x_j, y_j,-1] )
        c1 = color(abs(x_i),abs(y_i),0.75)
        c2 = color(abs(x_j),abs(y_j),0.25)
        fs.extend( [ facet(ccf,pf_i,pf_j,c1), facet(ccb,pb_i,pb_j,c2), facet(pf_i,pf_j,pb_i,c1), facet(pb_i,pb_j,pf_j,c2) ] )

    return fs

def make_sphere(s):

    fs,cs = [],[]
    step = 3+s

    # Generate colors
    for i in range(0,2*step):
        cr = abs(cos(i*pi/(2*step)))
        cg = abs(sin(i*pi/(2*step)))
        cb = abs(tan(i*pi/(2*step)))
        cs.append(color(cr,cg,cb))

    # Points at N-S poles
    pN = point.with_components( [ 0.0, 1.0, 0.0] )
    pS = point.with_components( [ 0.0,-1.0, 0.0] )

    # Generate mesh by making triangle fans at the poles
    # and latitudinal triangle strips elsewhere.
    for i in range(0,step+1):
        j = i+1         # 'i' signifies current ring, 'j' next ring

        # y-position for i- and j-rings
        y_i = cos(i*pi/step)
        y_j = cos(j*pi/step)

        # Radii for i- and j-rings
        r_i = abs(sin(i*pi/step))
        r_j = abs(sin(j*pi/step))

        # Make triangles
        for m in range(0,step):
            n = m+1
            if i == 0 or i == step:
                # If at the poles, make a fan
                r = sin(pi/step)
                x_m = r*cos(2*pi*m/step)
                x_n = r*cos(2*pi*n/step)
                z_m = r*sin(2*pi*m/step)
                z_n = r*sin(2*pi*n/step)
                p_m = point.with_components( [ x_m, y_j, z_m ] )
                p_n = point.with_components( [ x_n, y_j, z_n ] )
                if i == 0:
                    f = facet(pN,p_m,p_n,cs[0])
                else:
                    f = facet(pS,p_m,p_n,cs[2*step-1])
                fs.append(f)
            else:
                # Otherwise, make a latitudinal strip
                x_m = cos(2*pi*m/step)
                x_n = cos(2*pi*n/step)
                z_m = sin(2*pi*m/step)
                z_n = sin(2*pi*n/step)
                p_im = point.with_components( [ r_i*x_m, y_i, r_i*z_m ] )
                p_in = point.with_components( [ r_i*x_n, y_i, r_i*z_n ] )
                p_jm = point.with_components( [ r_j*x_m, y_j, r_j*z_m ] )
                p_jn = point.with_components( [ r_j*x_n, y_j, r_j*z_n ] )
                f1 = facet(p_im,p_in,p_jm,cs[2*i])
                f2 = facet(p_jm,p_jn,p_in,cs[2*i+1])
                fs.extend([f1,f2])

    return fs

def make_torus(s):

    fs = []
    step = 3+s

    minr = 0.5      # Minor radius // Requires minr < majR to work as intended.
    majR = 1        # Major radius // 

    rings = []
    ucirc = []

    # Calculate all the vertices for the mesh by making rings of points
    # (circles with r=0.5, starting in the x-y plane), 
    # rotating CCW about the y-axis.
    for i in range(0,step):
        ps = []
        if i == 0:
            # Unit circle in x-y plane centered at (1,0,0)
            for n in range(0,step):
                x = (majR-minr)*cos(2*pi*n/step)+majR
                y = (majR-minr)*sin(2*pi*n/step)
                z = 0 
                p = [x,y,z]
                ucirc.append(p)
            rings.append(ucirc)
        else:
            angle = 2*pi*i/step
            # Rotation matrix
            r = [[cos(angle),0,sin(angle)],[0,1,0],[-sin(angle),0,cos(angle)]]
            for n in range(0,step):
                # Rotate the nth point on the unit circle
                p = dot(ucirc[n],r)
                ps.append(p)
            rings.append(ps)

    rings.append(rings[0])

    # For every ring,
    for r in range(0,len(rings)-1):

        # for every point in that ring,
        for p in range(0,len(rings[r])):

            # take the next point on that ring
            # and two corresponding points on an adjacent (CCW) ring
            # (wrap around if it's the last point),
            if p == len(rings[r])-1:
                r0p0 = point.with_components(rings[r][p])
                r0p1 = point.with_components(rings[r][0])
                r1p0 = point.with_components(rings[r+1][p])
                r1p1 = point.with_components(rings[r+1][0])
            else:
                r0p0 = point.with_components(rings[r][p])
                r0p1 = point.with_components(rings[r][p+1])
                r1p0 = point.with_components(rings[r+1][p])
                r1p1 = point.with_components(rings[r+1][p+1])

            # make two colours based on the positions of two of those points
            # (one per ring),
            c0 = color(abs(r0p0[0]-1),abs(r0p0[1]),abs(r0p0[2])/2)
            c1 = color(abs(r1p1[0]-1),abs(r1p1[1]),abs(r1p1[2])/2)

            # and make two facets from those points and colors.
            f0 = facet(r0p0,r0p1,r1p0,c0)
            f1 = facet(r1p0,r1p1,r0p1,c1)
            fs.extend([f0,f1])

    return fs

def make_fromOBJ(filename):

    # Makes triangle mesh from OBJ file.
    # Only processes vertex and facet info; ignores the rest

    vs,ps = [None],[None]        # Occupy index 0 so vertex indices match
    fs = []

    cmax = 0                      # Max coordinate value found in file; used for scaling
    hue = [random(),random(),random()]

    try:
        with open(filename, 'r') as fi:
            vsDone = False
            for line in fi:

                # Remove whitespace in line and split by term
                l = line.rstrip()
                terms = l.split(" ")

                # Line represents a vertex
                if terms[0] == "v":
                    p = []
                    for i in range(1,len(terms)):
                        if abs(float(terms[i])) > cmax:
                            cmax = abs(float(terms[i]))
                        p.append(float(terms[i]))
                    ps.append(p)

                # Line represents a facet
                elif terms[0] == "f":

                    # Scale all vertex coordinates before making facets
                    # (bunny is super small and teapot is super not otherwise)
                    if not vsDone:
                        for i in range(1,len(ps)):
                            for n,coord in enumerate(ps[i]):
                                ps[i][n] = 1.5*coord/cmax
                            v = point.with_components(ps[i])
                            vs.append(v)
                        vsDone = True

                    # Get vertices
                    v1 = vs[int(terms[1])]
                    v2 = vs[int(terms[2])]
                    v3 = vs[int(terms[3])]

                    if len(terms) == 5:
                        # If 4 vertices specified for a facet,
                        # split into two.
                        # More can be specified but they won't be handled
                        v4 = vs[int(terms[4])]
                        c1 = getColor(v1,v2,v3,hue)
                        c2 = getColor(v4,v2,v3,hue)
                        f1 = facet(v1,v2,v3,c1)
                        f2 = facet(v4,v2,v3,c2)
                        fs.extend([f1,f2])
                    else:
                        c = getColor(v1,v2,v3,hue)
                        f = facet(v1,v2,v3,c)
                        fs.append(f)

    except IOError:
        print("Could not read file: ", filename)

    return fs

def getColor(v1,v2,v3,hue):

    # Generates the color for a facet on an object,
    # given the facet's vertices and the object's hue;
    # color is determined using a combination of
    # ambient and diffuse lighting.

    lightPos = vector(0.0,0.0,1.0)

    ambStrength = 0.3
    ambient,diffuse = [],[]
    for val in hue:
        ambient.append(ambStrength*val)

    # Get surface normal for the facet
    u = vector(v3[0]-v1[0],v3[1]-v1[1],v3[2]-v1[2])
    w = vector(v1[0]-v2[0],v1[1]-v2[1],v1[2]-v2[2])
    normal = u.cross(w)

    try:
        # Normalize surface normal
        normal = normal/normal.norm()

        # Get the facet's centroid
        center = vector((v1[0]+v2[0]+v3[0])/3,
                    (v1[1]+v2[1]+v3[1])/3,
                    (v1[2]+v2[2]+v3[2])/3)

        # Direction vector for light, normalized
        lightDir = lightPos-center
        lightDir = lightDir/lightDir.norm()

        # Amount of diffuse lighting
        d = max(normal.dot(lightDir),0.0)
        for val in hue:
            diffuse.append(d*val)

        c = color(ambient[0]+diffuse[0],ambient[1]+diffuse[1],ambient[2]+diffuse[2])
    except ZeroDivisionError:
        # Default to hue if error in calculations
        # (this happens on the teapot for some reason)
        c = color(hue[0],hue[1],hue[2])

    return c

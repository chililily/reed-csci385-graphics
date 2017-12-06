import random

ps_file = None

ps_poly = "/poly { 4 dict\n\
begin\n\
  /N exch def\n\
  /A 360 N div def\n\
  1 0 moveto\n\
  N {\n\
    A cos A sin lineto\n\
    /A A 360 N div add def\n\
  } repeat\n\
  closepath\n\
end\n\
} def\n"

def header():
    f = ps_file
    f.write(ps_poly)

def begin(fname):
    global ps_file
    ps_file = open(fname,"w")
    f = ps_file
    f.write("%!PS-Adobe-2.0\n")
    header()
    f.write("gsave\n")
    f.write("72 8.5 2 div mul dup translate\n")
    f.write("0 72 11 8.5 sub mul translate\n")
    f.write("1 720 div setlinewidth\n")
    f.write("1000.0 1000.0 scale\n")

def draw_stroke(gray,segment):
    f = ps_file
    g = 1.0-gray
    p1 = segment[0]
    p2 = segment[1]
    f.write(str(g) + " setgray\n")
    f.write("newpath\n")
    f.write(str(p1.x)+" "+str(p1.y)+" moveto\n")
    f.write(str(p2.x)+" "+str(p2.y)+" lineto\n")
    f.write("closepath\n")
    f.write("stroke\n")

def pick_color():
    f = ps_file
    r = random.random()
    g = random.random()
    b = random.random()
    f.write(str(r) + " " + str(g) + " " + str(b) + " setrgbcolor\n")

def draw_dot(p):
    f = ps_file
    f.write("gsave\n")
    f.write(str(p.x)+" "+str(p.y)+" translate\n")
    f.write("0.0025 0.0025 scale\n")
    f.write("15 poly\n")
    f.write("fill\n")
    f.write("grestore\n")

def set_gray(g):
    f = ps_file
    f.write(str(1.0-g) + " setgray\n")
    

def end():
    f = ps_file
    f.write("grestore\n")
    f.write("showpage\n")
    f.close()




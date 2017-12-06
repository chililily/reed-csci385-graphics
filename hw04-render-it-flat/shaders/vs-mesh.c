#version 120

attribute vec3 vertex;   // location on the surface
attribute vec3 normal;   // normal direction of the surface at location
attribute vec3 bary;     // barycentric info (affine combination weights)

uniform vec3 light;      // position of a point light source
uniform vec3 eye;        // position of the eyepoint
uniform int  wireframe;  // draw the wireframe mesh? (1 or 0)

varying vec3 n;
varying vec3 P;
varying vec3 bcoord;

void main() {
  n = normal;
  P = vertex;
  bcoord = bary;
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(P,1.0);
}

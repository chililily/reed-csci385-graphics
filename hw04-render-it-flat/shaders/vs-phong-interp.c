#version 120

attribute vec3 vertex;   // location on the surface

uniform vec3 light;      // position of a point light source
uniform vec3 eye;        // position of the eyepoint
uniform vec3 up;

varying vec3 P;

void main() {
  P = vertex;
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(P,1.0);
}

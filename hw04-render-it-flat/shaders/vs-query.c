#version 120

attribute vec3 vertex;   // location on the surface
attribute vec3 on_off;    // color to render on the surface

varying vec3 c_on_off;

void main() {
  c_on_off = on_off;
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(vertex,1.0);
}

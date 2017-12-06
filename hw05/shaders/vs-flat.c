#version 120

attribute vec3 vertex; 
uniform vec3 color;
  
void main() {
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(vertex,1.0);
}

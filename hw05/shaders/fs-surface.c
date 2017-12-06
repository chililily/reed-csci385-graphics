#version 120

varying vec3 I;  

uniform vec3 light;      // UNUSED
uniform vec3 eye;        // UNUSED

void main() {
  gl_FragColor = vec4(I,1.0);
}

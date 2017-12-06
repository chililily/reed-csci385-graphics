#version 120

varying vec3 c_on_off;

void main() {
  gl_FragColor = vec4(c_on_off,1.0);
  // gl_FragColor = vec4(0.5,0.3,0.2,1.0);
}

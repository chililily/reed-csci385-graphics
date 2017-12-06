#version 120

attribute vec3 vertex;   // location on the surface
attribute vec3 normal;   // normal direction of the surface at location

uniform vec3 light;      // position of a point light source
uniform vec3 eye;        // position of the eyepoint

varying vec3 I;

void main() {
  vec3 n = normal;
  vec3 P = vertex;

  float gloss = 0.25;     // brightness of highlight
  float shininess = 2;  // sharpness of highlight
  
  vec3 light_c    = vec3(0.5, 0.5, 0.5);   // light color
  vec3 ambient_c  = vec3(0.15, 0.15, 0.15);   // ambient scene color
  vec3 material_c = vec3(0.65, 0.65, 0.65);
  
  vec3 l = normalize(light - P);
  vec3 e = normalize(eye - P);
  vec3 r = -l + 2.0 * dot(l,n) * n;
  float p = shininess;
  float s = gloss;
  
  vec3 ambient = ambient_c * material_c;
  vec3 diffuse = light_c * material_c * max(dot(l,n),0.0);
  vec3 specular = light_c * s * max(dot(l,n),0.0) * pow(max(dot(e,r),0.0),p);

  I = ambient+diffuse+specular;
  gl_Position = gl_ProjectionMatrix*gl_ModelViewMatrix*vec4(P,1.0);
}

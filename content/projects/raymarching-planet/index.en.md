---
title: "Ray marched planets with an atmosphere"
category: shaders
summary: "A post-process shader for Unigine that draws a planet through SDF ray marching. The surface is defined by a distance field displaced by a height map, and the same pass computes lighting, layered clouds and light scattering in the atmosphere."
date: 2025-05
tags: [hlsl, raymarching, sdf, unigine, atmosphere]
tech: [HLSL, Unigine, Ray marching, SDF, Post-process, Rayleigh scattering]
banner: frame_614.png
cover: frame_3.png
theme: stars
gallery:
    - frame_5.png
    - frame_9.png
    - frame_11.png
    - frame_10.png
---

## Problem statement

<figure>
  <img src="/projects/raymarching-planet/assets/hero2_2.png" alt="" loading="lazy">
</figure>

A planet in a space scene is a sphere with a radius of thousands of units, of which less than half
the surface reaches the frame. A polygonal solution requires either a dense mesh or tessellation
with transitions between levels of detail, and the relief is baked into the geometry in advance and
changes only by rebuilding the asset. The cost of preparing the mesh does not depend on how much of
it is visible.

The shader builds the planet analytically. There is no geometry in the scene: the body is described
by a distance field and computed in a full-screen post-process pass, where every pixel of the frame
casts a ray, finds the intersection with the surface and determines the colour at the hit point. The
relief is introduced by a height map during the march itself, so its detail is limited by the
resolution of the texture and is unrelated to the contents of the scene.

The ray march, the interaction with the depth buffer, the relief, the UV mapping, the lighting, the
clouds and the whole system of settings are written from scratch. The atmosphere shader is based on
a [Shadertoy](https://www.shadertoy.com/view/WlBfzD) GLSL shader, rewritten for HLSL and the Unigine
engine.

The shader was developed inside a closed 3D project, so the sources are not available. The fragments
below are the ones that define how the computation is arranged.

## The post-process pass

The material is declared as a post-process and runs before temporal antialiasing. Reading the screen
buffer and writing to it within a single pass is not possible, so the screen colour is copied into a
temporary texture and the result of the march is written into the screen one:

```text
Expression RENDER_CALLBACK_BEGIN_TAA =
#{
    Texture screen_texture = engine.render_state.getScreenColorTexture();
    Texture source = engine.render.getTemporaryTexture(screen_texture);
    source.copy(screen_texture);
    setTexture("screen_texture", source);
    renderPassToTexture("raymarching_planet", screen_texture);
    engine.render.releaseTemporaryTexture(source);
#}
```

The ray is reconstructed from screen coordinates: the origin is placed on the near plane and the
direction is taken from the view direction in view space.

```hlsl
float3 view_v = normalize(screenUVToViewDirection(IN_UV.xy));
float3 ro = view_v * s_depth_range.x;
float3 rd = view_v * -1.0f;
```

The computation is carried out in view space, into which the position of the planet and the
directions towards the light sources are transformed by the `s_modelview` matrix. The transform back
to world space is performed only for the texture mapping, which needs the body's own orientation.

## Scaling the scene

The radius of the planet and the distance to it are measured in thousands of units: in the working
configuration of the moon that is a radius of 4000 at a distance of about 11 800. A march at such
magnitudes spends steps and loses precision on unit increments, so the position and the radius are
divided by a common factor and the hit point is multiplied by it back:

```hlsl
float sphereRadius    = var_sphere_radius / var_parallax_scaler;
float3 spherePosViewP = spherePosView / var_parallax_scaler;

RayMarchingResult rmr = RayMarch(ro, rd, MAX_STEP, MAX_DIST, SURF_DIST,
                                 spherePosViewP, sphereRadius, sunDirection);
float3 p      = ro + rd * rmr.d;
float3 p_real = p * var_parallax_scaler;
```

The ray origin lies on the near plane and practically coincides with the origin of view space, so
dividing the distance and the radius at the same time preserves the angular size of the planet on
screen and changes only the length of the ray path. The real dimensions of the body in the scene are
untouched: the factor affects only the space in which the march is performed.

## The distance field and the relief

The basis is the signed distance to a sphere, from which the value of the height map at the point is
subtracted, that is, the surface is displaced outwards in proportion to the brightness of the
texture. The intensity factor is set by the material and equals 50 at a radius of 4000 in the
configuration of the moon.

```hlsl
float SdSphere(float3 p, float3 sp, float r){
    return length(sp - p) - r;
}

float GetDistance(float3 p, float3 sp, float sr, float lod_d){
    float sphere = SdSphere(p, sp, sr);
    float dist = 0.0f;
    #ifdef STATE_USE_HEIGHT_MAP
        dist = getHeightMap(p, sp, sr, lod_d) * var_hight_intensity;
    #endif
    return sphere - dist;
}
```

The march advances by a step equal to the current distance to the surface and stops when the maximum
distance is exceeded or the proximity threshold is reached. The `loop` attribute forbids the compiler
from unrolling a loop with a variable iteration count.

```hlsl
float d = 0.0;
loop for(int i = 0; i < maxStep; i++){
    float3 p = rayOrigin + rayDirection * d;
    float dS = GetDistance(p, sp, sr, p.z);
    d += dS;
    if(d > maxDist || dS < surfDist) break;
}
```

The height map is read with a level of detail bias computed from the depth of the point and a
configurable distance threshold. The bias was introduced because of how often the texture is read:
it is sampled at every iteration of the march and again when the normal is computed, so a coarser
mip level is taken for distant areas, which reduces both the load on the texture cache and the
high-frequency noise of the relief near the horizon.

## Compositing with the scene

The post-process pass writes over a finished frame and without an additional condition would cover
all the geometry. The hit point is projected back and compared with the value from the depth buffer
of the scene:

```hlsl
float4 planetPosProj = mul(s_camera_projection, float4(p_real, 1.0f));
planet_depth = step(depth - planetPosProj.z / planetPosProj.w, 0.0f);

float mask = step(d, MAX_DIST) * planet_depth;
...
OUT_COLOR.rgb = lerp(color.rgb, finalColor, mask) + atmColor;
```

The mask combines two conditions: the ray converged to the surface, and the hit point is not
occluded by geometry. The whole computation of the surface colour is performed under this mask, so
background pixels cost only the march itself.

## Mapping and rotation

The hit point is transformed into world space, shifted to the centre of the planet and rotated by a
matrix built from the Euler angles that define the tilt of the axis. A spherical mapping is then
applied: the longitude comes from `atan2` in the equatorial plane, the latitude from the angle
between the vector to the point and the axis of the planet.

```hlsl
float2 calculateUV(float3 p, float3 spWorld, float sr){
    float3 pw = mul(s_imodelview, float4(p, 1.0f)).xyz;
    float3 pl = pw - spWorld;
    float3x3 rotMatrix = eulerToRotationMatrix(var_sphere_ratation);
    float3 rotatedPl = mul(rotMatrix, pl);

    float3 up = float3_up * sr;
    float fi = acos(dot(up, rotatedPl) / (sr * length(rotatedPl)));
    float atanVal = ((atan2(rotatedPl.y, rotatedPl.x) / PI) + 1.0f) / 2.0f;
    return float2(atanVal, (fi / PI));
}
```

The daily rotation is done by shifting the mapping along the longitude in proportion to time rather
than by rotating the body. The shift is computed once and applied to the base texture, the height
map, the clouds and the masks, which rules out any divergence between the layers.

## Normals and lighting

<video width="780" height="458" autoplay muted loop playsinline><source src="/projects/raymarching-planet/assets/light_demo.mp4" type="video/mp4">
Your browser does not support the video tag or this video format. You can download the video anyway.
</video>

The normal is computed as a finite difference of the distance field with a configurable step. Since
the field includes the displacement by the height map, the relief takes part in the shading without
a separate normal map.

```hlsl
float3 GetNormal(float3 p, float3 sp, float sr){
    float d = GetDistance(p, sp, sr, p.z);
    float2 e = float2(var_normal_step, 0.0f);
    float3 n = d - float3(GetDistance(p - e.xyy, sp, sr, p.z),
                          GetDistance(p - e.yxy, sp, sr, p.z),
                          GetDistance(p - e.yyx, sp, sr, p.z));
    return normalize(n);
}
```

The lighting is Lambertian, and the depth of the terminator is exposed as a separate parameter: the
dot product is blended with one, so the night side is brightened independently of the day side.

```hlsl
bright = saturate(dot(sunDirection, normalVec));
bright = lerp(float3_one, bright, var_sun_shadow_intensity) * var_sun_color.rgb;
```

Three lighting schemes are supported: a single source, two sources with a weight of dominance
between them, and a moon mode in which the direction of the second source of the scene is taken.
A Blinn specular highlight and an emission by mask are available in addition. The emission has a
mode in which the mask is multiplied by the inverted illumination, so its contribution remains only
on the unlit side and falls to zero at the terminator.

## Clouds

The clouds are computed not by a separate pass but as samples of a single texture at several points
along the ray, offset from the surface by a given height:

```hlsl
loop for(int j = 1; j < var_cloud_ray_count + 1; j++){
    float cloud_d = j * var_cloud_ray_step + var_cloud_height;
    float3 p = rayOrigin + rayDirection * d - rayDirection * cloud_d / var_parallax_scaler;
    cloud_int += GetCloudIntensity(p, j / var_cloud_ray_count, sp, sr) * var_cloud_intensity;
}
```

Each point yields its own mapping, so as the camera moves the layers shift relative to one another,
and that is what creates the visible thickness of the cloud cover. The shadow of the clouds is
computed with one additional sample: the hit point is displaced towards the light source and the
same texture is read at that position, and the result is subtracted from the illumination of the
surface. The accumulated cloud density is also subtracted from the specular mask, since a reflection
from an area covered by cloud must not be registered.

## Texture animation through a flow map

<video width="780" height="458" autoplay muted loop playsinline><source src="/projects/raymarching-planet/assets/flowmap_demo.mp4" type="video/mp4">
Your browser does not support the video tag or this video format. You can download the video anyway.
</video>

The motion of the clouds and the currents is set by a map of directions. A shift along such a map
cannot be accumulated continuously: the displacement grows with time and stretches the texture. A
scheme of two phases offset by half a period with cross blending is used instead:

```hlsl
float flowTime = s_time * flowmapSpeed;
float fracFlowTime1 = frac(flowTime);
float fracFlowTime2 = frac(flowTime + 0.5f);
float2 phase1 = uv + flowmapUv * fracFlowTime1;
float2 phase2 = uv + flowmapUv * fracFlowTime2;
float flowLerpTime = abs((fracFlowTime1 - 0.5f) * 2.0f);
```

At the moment one phase resets its weight is zero and the frame is formed by the other phase, so the
discontinuity never reaches the image. The mechanism is shared by the surface and the clouds, while
the strength and speed parameters are separate for each.

## Atmosphere

<figure>
  <a href="https://www.shadertoy.com/view/WlBfzD" target="_blank" rel="noopener">
    <img src="/projects/raymarching-planet/assets/atmosphere_reference.png" alt="The original atmosphere shader on Shadertoy" loading="lazy">
  </a>
  <figcaption>The original Shadertoy shader taken as the basis of the atmosphere</figcaption>
</figure>

The atmospheric scattering is taken from Shadertoy and rewritten for HLSL. It implements a single
scattering model: a given number of points is taken along the segment of the ray inside the
spherical shell, a ray towards the light source is cast from each of them, the optical depth is
computed along it, and the accumulated light is weighted by wavelength-dependent scattering
coefficients.

```hlsl
float3 scatteringCoefficients = pow(400.0 / var_atm_wave_lengths,
                                    float3(4.0, 4.0, 4.0)) * var_atm_scattering_strength;
```

The density falls off exponentially with altitude and reaches zero at the boundary of the shell, so
the transition to space produces no visible cut-off line:

```hlsl
float elevation = length(p - planetPosition) - planetRadius;
float elevationScalar = elevation / atmosphereSize;
return exp(-elevationScalar * densityFalloff) * (1.0 - elevationScalar);
```

The ends of the segment are found by an analytical intersection of the ray with the sphere rather
than by marching. Two cases are handled: the ray passes through the atmosphere, or it runs into the
planet and the segment is then cut off at the surface. The second case accounts for the falloff of
the glow at the limb and for the dark band above the night side.

```hlsl
float2 rayIntersectSphere(in float3 ro, in float3 rd, in float3 ce, float ra) {
    float3 oc = ro - ce;
    float b = dot(oc, rd);
    float c = dot(oc, oc) - ra * ra;
    float h = b * b - c;
    if (h < 0.0) return float2(-1.0, -1.0);
    h = sqrt(h);
    return float2(-b - h, -b + h);
}
```

The intersections are analytical, so the atmosphere is computed at the original scale of the scene
and does not depend on the factor applied during the surface march. The number of points along the
view ray and along the ray towards the source is set by the material and capped at 50: the product
of these two values determines the number of samples per pixel, and without the cap a value entered
in the editor goes straight into the frame time.

## Analytical optical depth

A separate branch was an attempt to replace the nested loops with a closed form. For a medium with
an exponentially decreasing density in spherical geometry the optical depth is expressed through the
Chapman function, which is approximated by a polynomial, so the whole segment is computed without
samples along the ray.

```hlsl
float OpticalDepthExpSphereMedia(float3 ro, float3 rd, float dist,
                                 float3 center, float radius, float hfalloff)
{
    float3 topos = ro - center;
    float rX = length(topos);
    float rRcpX = 1.0f / rX;
    float cosThetaX = dot(topos * rRcpX, normalize(rd));
    float rY = RadAtDist(rX, rRcpX, cosThetaX, dist);
    float cosThetaY = CosAtDist(rX, rRcpX, cosThetaX, dist);
    ...
    float ch = abs(chX - chY);
    return saturate(ch * (1.0f / hfalloff));
}
```

The variant is arranged as a separate material state and is disabled in the current configuration:
it produces a single-colour glow set by a parameter and does not reproduce the dependence of the
colour on the wavelength, which is the reason the atmosphere is computed point by point in the first
place. The branch is kept as a replacement for bodies that occupy a few pixels of the frame, where
the difference between the models is indistinguishable while the difference in cost is two nested
loops against a few dozen arithmetic operations.

## Configurability

The large parts of the shader are declared as material states rather than as runtime flags:

```text
Group "States" {
    State use_height_map = true
    State clouds         = false
    State atmosphere     = false
    State emission       = false
    State specular       = false
    State two_suns       = false
}
```

The split into states determines three properties:

- **A disabled feature does not affect the cost of the frame.** Each state produces its own variant
  of the shader, and the code behind `#ifdef STATE_CLOUDS` and similar directives is absent from the
  compiled program. The set of features grows without making the simple cases worse.
- **The material interface matches the configuration.** Parameter groups are bound to their states
  and hidden while a feature is off, so the editor shows only the fields that affect the result.
- **A celestial body is described by data.** An inheriting material sets the surface and relief
  textures, the position, the radius, the axial tilt and the rotation speed, the lighting scheme and
  the parameters of the clouds and the atmosphere. One base material serves both a planet with a
  dense atmosphere and a cloud layer and an airless moon with pronounced relief.

## Limitations

Every instance of the material is a separate full-screen pass, so several planets in the frame mean
several passes. The approach is intended for scenes with a single visible body in the near plane.

Interaction with the scene is limited to the depth test: the planet is correctly occluded by
geometry, but it casts no shadow on it and takes no part in reflections or global illumination.

Subtracting the height map from the distance to the sphere breaks the condition of a correct
distance field: the march step is no longer guaranteed to be safe. At a high relief intensity the
ray steps over narrow features, which is compensated for by lowering the proximity threshold and
raising the number of steps, that is, at the expense of performance.

There is no shadowing by the relief. The lighting is computed from the normal of the field, and rays
from the surface to the light source are not traced, so slopes do not shade one another and deep
relief forms look flat under a low sun.

The cloud cover is approximated by several layers of a single texture rather than by a volumetric
render, and at a grazing view along the surface the layering is discernible. At the seam of the
spherical mapping the coordinates change abruptly, because of which the hardware choice of the level
of detail along that line can produce a band of reduced sharpness.

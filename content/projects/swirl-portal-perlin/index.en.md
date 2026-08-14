---
title: "Space gate activation shader"
category: shaders
summary: "A shader for Unigine that draws a portal funnel on a single quad. The frame is built in log-polar coordinates: two spiral copies of one noise map are multiplied together, offset by domain warping and clipped by a mask of varying radius."
date: 2026-06
tags: [hlsl, unigine, vfx, log-polar, domain-warping, perlin]
tech: [HLSL, Unigine, Log-polar mapping, Domain warping, Perlin noise, Shadertoy]
theme: stars
# Page media. Files go into assets/ next to this index.ru.md,
# after which the lines are uncommented.
# banner: banner.png
cover: cover.png
# gallery:
#     - {src: frame_activation.png, caption: "Gate opening"}
#     - {src: frame_edge.png, caption: "Ragged boundary"}
#     - {src: frame_core.png, caption: "Core glow"}
links:
    - {label: "Demo on Shadertoy", url: "https://www.shadertoy.com/view/7f3SR7", icon: external}
---

<video width="780" height="438" autoplay muted loop playsinline><source src="/projects/swirl-portal-perlin/assets/activation.mp4" type="video/mp4">
Your browser does not support the video tag or this video format. You can download the video anyway.
</video>


## Problem statement

An activation effect for the space gate in the FreedomSpace space simulator on the Unigine engine: a
funnel with a spiral pattern, an uneven boundary and a glowing core. The whole picture is built in a
fragment shader on a single quad of an unlit material from one grayscale noise map. The funnel, depth
and rotation are obtained by transforming coordinates before sampling: a point on the quad is mapped
into a log-polar system, where a shift along one axis is equivalent to scaling the plane relative to
the center.

<video width="780" height="438" autoplay muted loop playsinline><source src="/projects/swirl-portal-perlin/assets/activation_2.mp4" type="video/mp4">
Your browser does not support the video tag or this video format. You can download the video anyway.
</video>

## Interactive demo

A port of the effect to GLSL, the computation is the same: the noise map is bound as a channel, the
parameters are hardcoded as constants.

<div class="embed-16x9">
<iframe src="https://www.shadertoy.com/embed/7f3SR7?gui=true&amp;t=10&amp;paused=false&amp;muted=true"
          title="Swirl Portal Perlin on Shadertoy"
          frameborder="0" allowfullscreen
          allow="accelerometer; gyroscope; fullscreen">
</iframe>
</div>

## Log-polar coordinates

The UV is mapped to the range from minus one to one, so the center of the plane lands at the origin.
Then polar coordinates are taken, but the radius is used through a logarithm:

```hlsl
float2 uv = DATA_UV.xy * 2.0 - 1.0;

float r     = length(uv);
float angle = atan2(uv.y, uv.x);
float depth = log2(max(r, 1e-4));
float u     = angle / TWO_PI;          // exactly 1.0 per revolution
float t     = s_time;
float lod   = max(0.0, -depth - 1.0);  // explicit mip: no seam + no center aliasing
```

The pair `(angle, depth)` is the complex logarithm of the point: a circle of constant radius maps to
a line of constant `depth`, a ray from the center to a line of constant angle. The mapping is
conformal, locally it is a rotation and a uniform scaling with a coefficient proportional to the
radius, so the texture is nowhere stretched along a single axis, and its apparent scale decreases
toward the center in proportion to `r`.

A uniform shift in `depth` corresponds to multiplying the radius by a constant coefficient, so motion
of the pattern that is linear in time along this axis produces uniform scaling of the picture
relative to the center, and a shift by one texture period reproduces the same frame at a different
scale: the motion has neither an initial nor a final state. The radius is bounded from below by
`1e-4`, otherwise the logarithm at the center goes to minus infinity.

## Seamlessness and level of detail

The angle is normalized to a full revolution, so `u` changes by exactly one per revolution. On the
ray where `atan2` jumps from plus pi to minus pi, the sampling coordinate jumps by `ang_tiles`, and
for integer `ang_tiles` the jump is a multiple of the texture repeat period: the same value is
sampled on both sides of the ray.

The coordinate is continuous, but its screen-space derivative is discontinuous on this ray and grows
toward the center in inverse proportion to the radius. The hardware mipmap selection follows exactly
these derivatives, so the level is set explicitly: `TEXTURE_BIAS` in UUSL expands to `SampleLevel`,
and the third argument is not a bias but the level itself. The quantity `lod = max(0, -depth - 1)`
inside the circle `r = 0.5` grows by one at each doubling of proximity to the center, matching the
growth of sampling density, and is continuous in the angle. As a result there is no band of reduced
sharpness at the seam, and the center of the funnel is not covered by high-frequency noise.

## Noise map

<figure>
  <img src="/projects/swirl-portal-perlin/assets/noise-super-perlin.png" alt="Super Perlin 512x512 noise map" loading="lazy" width="512">
  <figcaption>Super Perlin 11, 512x512, a single map is used for all four samples</figcaption>
</figure>

The shader reads the red channel of one texture. The requirements for the map follow from the design
of the computation:

- Seamless along both axes
- Presence of mipmaps
- Several octaves in one map
- No pronounced directionality

The map used is [Super Perlin 11](https://opengameart.org/content/noise-texture-pack-super-perlin-11-512x512png)
at 512x512 resolution: grayscale multi-octave Perlin with a mean near the middle of the range, to
which the thresholds of the color scale and the value of `contrast` are fitted.

## Two spiral layers

Adding `swirl_strength * depth` to the angular coordinate produces a shift proportional to the
logarithm of the radius, so a line of constant value is defined by the equation `angle = const -
swirl_strength * log2(r)`. This is a logarithmic spiral: it crosses rays from the center at a single
angle, and the twist looks the same at any distance.

```hlsl
float2 sp1 = float2(
    u * var_ang_tiles + var_swirl_strength * depth + var_flow_speed.x * t,
    depth * var_radial_scale - var_flow_speed.y * t);
float2 sp2 = float2(
    u * var_ang_tiles * var_layer_mul + var_swirl_strength * depth - var_flow_speed.x * t,
    depth * var_radial_scale * var_layer_mul - var_flow_speed.y * 1.3 * t);
```

Even a single sample gives not blobs but threads: light streaks that are long along the spiral and
narrow across it. In the conformal pair `(angle, ln r)` the transition to sampling coordinates is
linear:

```text
x = ang_tiles / (2*PI) * angle + swirl_strength / ln2 * ln r
y =                              radial_scale  / ln2 * ln r
```

At `ang_tiles = 6`, `swirl_strength = 4` and `radial_scale = 3` the singular values of this matrix
are approximately 7.3 and 0.57, that is, a round texture blob maps into an ellipse with an axis ratio
of about 13: the radial frequency is roughly 4.5 times higher than the angular one, and the shift by
`swirl_strength` rotates the shape along the spiral.

The second layer reads the same texture at a frequency multiplied by `layer_mul` along both axes,
that is, it acts as the next octave; its angular drift is of the opposite sign, and its radial speed
differs by a factor of 1.3. The layers have no common period, so the relative arrangement of the
threads does not repeat over a revolution. Seamlessness requires integer `ang_tiles` and `ang_tiles *
layer_mul`; a fractional value of either quantity produces a seam along the angle transition ray.

The direction of the flow is set by the sign of `flow_speed.y`: the quantity is subtracted from
`depth * radial_scale`, so a positive value carries the pattern away from the center, a negative one
draws it inward. The radial coordinate fits `radial_scale` texture periods into a doubling of the
radius, so the speed in doublings per second equals `flow_speed.y / radial_scale`.

## Domain warping

Spirals built directly give a strictly regular family of lines. Before sampling, both coordinates are
offset by a vector field from the same texture at a low frequency, that is, the noise argument is
itself computed through noise:

```hlsl
float2 warpCoord = float2(u * var_ang_tiles + var_swirl_strength * depth * 0.5,
                          depth * var_radial_scale * 0.5 - var_flow_speed.y * 0.5 * t);
float2 warp = float2(
    TEXTURE_BIAS(tex_noise, warpCoord,             lod + 1.0).r,
    TEXTURE_BIAS(tex_noise, warpCoord + 0.37,      lod + 1.0).r) * 2.0 - 1.0;
sp1 += warp * var_warp_strength;
sp2 += warp * var_warp_strength;
```

The warp field is low-frequency in two ways: its coordinate scale is half the base one, and its level
of detail is one higher. The second component of the vector is taken with an offset of 0.37, which is
not a multiple of the repeat period, so the components are uncorrelated and a second texture is not
needed. The amplitude `warp_strength` is measured in texture periods: 0.35 shifts the sample by a
third of a period. The `ang_tiles` factor in the angular part is preserved, so the warp is seamless
under the same condition, and the same vector is added to both layers, so their mutual pattern stays
coherent.

## Density and contrast

A single scalar field is assembled from the two samples:

```hlsl
float n1 = TEXTURE_BIAS(tex_noise, sp1, lod).r;
float n2 = TEXTURE_BIAS(tex_noise, sp2, lod).r;

float density = saturate(n1 * n2 * 2.0);
density = pow(density, var_contrast);

float shimmer = saturate(n1 - n2 + 0.5);
```

A product, not a sum: a low value of either layer zeroes the result, so only the overlaps of threads
from both layers stay bright. The slope of the second layer's lines in the angle is smaller by a
factor of `layer_mul`, the families run at an angle to each other and cut each other into short
bright segments. For two weakly correlated fields with a mean near 0.5 the product gives a mean near
0.25, hence the factor of 2.0 and the `saturate` clamp.

Raising to the power `contrast` is a gamma transform on the interval from zero to one: mid values are
shifted toward zero more strongly than high ones, one stays in place, the threads narrow, the gaps
darken. The difference of the layers gives the `shimmer` field with a mean in the middle of the
range; it marks the divergence of the layers and takes part only in computing the hue.

## Color

The color is assembled on a three-point scale driven by density, with two `smoothstep` transitions:

```hlsl
float3 col = var_color_shadow.rgb;
col = lerp(col, var_color_mid.rgb, smoothstep(0.05, 0.45, density));
col = lerp(col, var_color_hot.rgb, smoothstep(0.45, 0.95, density));

col = lerp(col, col.bgr, shimmer * (1.0 - density) * 0.5);

col *= var_brightness;
col += var_color_hot.rgb * saturate(1.0 - r) * var_core_glow;
```

The thresholds 0.05, 0.45 and 0.95 are tied to the histogram of the density field, which depends on
the noise map and the value of `contrast`: a map with a different mean requires recomputation,
otherwise the image drifts either into a solid dark color or into blowout.

The hue is changed by permuting channels: `col.bgr` gives the second color without a hue rotation
matrix and without a gradient lookup table, and the weight of the permutation is multiplied by `1 -
density`, so the cores of the threads keep `color_hot`. The `brightness` factor pushes bright areas
past one, where the glow post-processing picks them up. The core glow is added by the cone
`saturate(1.0 - r)`, which covers the center of the mapping where detail is reduced.

## Boundary mask

Clipping by a circle of constant radius gives a clean boundary along which the quad reads as a flat
figure. The clip radius is made a function of the angle: noise from the current point is added to the
base value.

```hlsl
float tear = density * 0.7 + (warp.x * 0.5 + 0.5) * 0.3;
float edge = var_edge_radius + tear * var_edge_tear;        // boundary varies with noise
float band = smoothstep(edge - var_edge_soft, edge, r);     // 0 inside -> 1 outside
float mask = 1.0 - band;

float rim = band * mask * 4.0;                              // peaks in the transition band
col += var_color_hot.rgb * rim * var_edge_glow;

OUT_FRAG_COLOR = col * mask;
OUT_FRAG_OPACITY = var_opacity * mask;
```

The boundary offset is assembled from two fields in a 70 to 30 ratio: the high-frequency density
gives short tongues along the threads, the low-frequency warp adds wide lobes. The edge glow is
obtained from the product `band * mask`, where the second quantity complements the first to one: the
function `b * (1 - b)` is zero on both sides of the transition and reaches a maximum of 0.25 at `b =
0.5`, hence the factor of 4.0. The peak is obtained without a second `smoothstep` and without
computing the distance to the boundary.

The mask enters both the color and the opacity, so with `[src_alpha one_minus_src_alpha]` blending
the contribution of a pixel is proportional to its square: the falloff toward the edge is steeper
than the mask itself, and the color does not bleed past the clip. If `edge_soft` exceeds the range of
radii of the quad, the transition band covers it entirely: the mask becomes a smooth falloff from the
center to the edge, the maximum of `band * mask` shifts almost to the center, and the same branch of
code works as a second core glow.

## Limitations

The effect is flat: the funnel and depth exist only in the coordinates of the mapping, so at a
grazing viewing angle and where it intersects scene geometry the quad reads as a plane. Two-sided
mode is enabled, but the same picture is visible from the back.

The values `ang_tiles` and `layer_mul` are restricted to integers, so smooth retuning of the
frequency in the angle, including animating the opening by changing the number of arms, breaks
seamlessness.

The thresholds of the color scale are hardcoded as constants fitted to the histogram of a specific
noise map: changing the map requires refitting `contrast`, and with a noticeable shift of the mean
also editing the thresholds themselves in the code. The logarithm of the radius is bounded from below
by a constant, and the region within this limit is covered by the core glow: with `core_glow` at zero
a blob with a degenerate mapping is exposed.
</content>
</invoke>

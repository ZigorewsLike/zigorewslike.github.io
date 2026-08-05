---
title: "Plasma shader in GLSL"
category: shaders
summary: "A fragment shader with animated plasma. Example of the Shaders / Graphics category."
date: 2025-07
featured: true
tags: [glsl, webgl, realtime]
tech: [GLSL, WebGL, JavaScript]
# cover: cover.png
# banner: banner.png
links:
  - { label: "Source", url: "https://github.com/username/shader", icon: github }
  - { label: "Live demo", url: "https://shadertoy.com/view/XXXX", icon: external }
---

## Idea

An example project from the **graphics programming** category. The body is free-form,
so it's easy to embed an interactive WebGL canvas via raw HTML.

Below is a stub with an animated canvas (replace it with your own WebGL renderer):

<canvas id="demo-canvas" width="640" height="360"
        style="width:100%;border-radius:12px;border:1px solid var(--border);background:#000"></canvas>

<script>
(function () {
  const c = document.getElementById("demo-canvas");
  if (!c) return;
  const ctx = c.getContext("2d");
  let t = 0;
  (function loop() {
    const w = c.width, h = c.height;
    const img = ctx.createImageData(w, h);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const v = Math.sin(x * 0.04 + t) + Math.sin(y * 0.05 + t) +
                  Math.sin((x + y) * 0.03 + t);
        const i = (y * w + x) * 4;
        img.data[i]     = 128 + 127 * Math.sin(v);
        img.data[i + 1] = 128 + 127 * Math.sin(v + 2);
        img.data[i + 2] = 128 + 127 * Math.sin(v + 4);
        img.data[i + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    t += 0.03;
    requestAnimationFrame(loop);
  })();
})();
</script>

### How it works

The usual fragment approach: for each pixel we compute a color as a function of
coordinates and time. In a real project this would be a GLSL shader instead of canvas 2D.
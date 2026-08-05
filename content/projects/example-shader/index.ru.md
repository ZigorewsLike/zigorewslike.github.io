---
title: "Плазма-шейдер на GLSL"
category: shaders
summary: "Фрагментный шейдер с анимированной плазмой. Пример категории Shaders / Graphics."
date: 2025-07
featured: true
tags: [glsl, webgl, realtime]
tech: [GLSL, WebGL, JavaScript]
# cover: cover.png
# banner: banner.png
links:
  - { label: "Исходники", url: "https://github.com/username/shader", icon: github }
  - { label: "Живое демо", url: "https://shadertoy.com/view/XXXX", icon: external }
---

## Идея

Пример проекта из категории **графического программирования**. Тело — свободное,
поэтому сюда легко встроить интерактивный WebGL-канвас прямо через сырой HTML.

Ниже — заглушка с анимированным canvas (замени на свой WebGL-рендер):

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

### Как это работает

Обычный фрагментный подход: для каждого пикселя считаем цвет как функцию координат
и времени. В реальном проекте здесь будет GLSL-шейдер, а не canvas 2D.

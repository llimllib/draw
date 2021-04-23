const $ = (s) => document.querySelector(s);

// https://stackoverflow.com/a/15666143
// https://www.html5rocks.com/en/tutorials/canvas/hidpi/
var PIXEL_RATIO = (function () {
  var ctx = document.createElement('canvas').getContext('2d'),
    dpr = window.devicePixelRatio || 1,
    bsr =
      ctx.webkitBackingStorePixelRatio ||
      ctx.mozBackingStorePixelRatio ||
      ctx.msBackingStorePixelRatio ||
      ctx.oBackingStorePixelRatio ||
      ctx.backingStorePixelRatio ||
      1;

  return dpr / bsr;
})();

createHiDPICanvas = function (w, h, ratio) {
  if (!ratio) {
    ratio = PIXEL_RATIO;
  }
  can.width = w * ratio;
  can.height = h * ratio;
  can.style.width = w + 'px';
  can.style.height = h + 'px';
  can.getContext('2d').setTransform(ratio, 0, 0, ratio, 0, 0);
  return can;
};
// end SO

function fullscreenCanvas(canvas) {
  return () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    // text still looks awful. figure it out at some point iunno
    const ctx = canvas.getContext('2d');
    ctx.setTransform(PIXEL_RATIO, 0, 0, PIXEL_RATIO, 0, 0);
    return ctx;
  };
}

function choose(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

let t = 0;
function draw(ctx, w, h) {
  const cw = w / 2,
    ch = h / 2;
  let sprites = [];
  return () => {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, w, h);
    ctx.fillStyle = 'orange';
    ctx.font = '48px serif';
    if (Math.random() < 0.3) {
      sprites.push({
        x0: t,
        // ch: choose(['+', '-', '[', ']', 'v', '^', '*', '&']),
        ch: choose(['A', 'J', 'B', '9', '0', '3']),
        angle: Math.random() * (2 * Math.PI),
      });
    }
    sprites.forEach((sp) => {
      const velocity = 2;
      // A rainbow is the result if you have three out of phase sine waves! neat
      // https://krazydad.com/tutorials/makecolors.php
      const x =
          cw + ((t % w) - cw) + (t - sp.x0) * velocity * Math.cos(sp.angle),
        y = ch + (t - sp.x0) * velocity * Math.sin(sp.angle),
        r = Math.sin(x / (w / 3)) * 127 + 128,
        g = Math.sin(x / (w / 3) + (2 * Math.PI) / 3) * 127 + 128,
        b = Math.sin(x / (w / 3) + (4 * Math.PI) / 3) * 127 + 128;
      sp.x = x;
      sp.y = y;
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillText(sp.ch, x, y);
    });
    // eliminate dead sprites
    sprites = sprites.filter(
      (sp) => sp.x > 0 && sp.x < w + 50 && sp.y > 0 && sp.y < h + 50
    );
    t += 1;
  };
}

window.addEventListener('DOMContentLoaded', async (_evt) => {
  const canvas = $('#canvas');
  window.canvas = canvas;

  // TODO how to pull the updated context out of here?
  window.addEventListener('resize', fullscreenCanvas(canvas), false);

  // set the canvas for the screen ratio, and get a context
  const ctx = fullscreenCanvas(canvas)();

  setInterval(
    draw(ctx, canvas.width / PIXEL_RATIO, canvas.height / PIXEL_RATIO),
    Math.floor(1000 / 60)
  );
});

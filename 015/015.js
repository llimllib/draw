const $ = (s) => document.querySelector(s);

// https://stackoverflow.com/a/15666143
// https://www.html5rocks.com/en/tutorials/canvas/hidpi/
var PIXEL_RATIO = (function() {
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

createHiDPICanvas = function(w, h, ratio) {
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

function rand() {
  return Math.random();
}

function randint(n) {
  return Math.floor(rand() * n);
}

let t = 0;
function draw(ctx, w, h) {
  const cw = w / 2,
    ch = h / 2;
  let sprites = [];
  return () => {
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, w, h);
    if (Math.random() < 0.1 && sprites.length < 1000) {
      sprites.push({
        t0: t,
        x: randint(w),
        y: randint(h),
        dx: randint(9) + 1,
        dy: randint(9) + 1,
      });
    }
    sprites.forEach((s) => {
      s.x = s.x + s.dx;
      s.y = s.y + s.dy;
      if (s.x > w || s.x < 0) {
        s.dx = -s.dx;
      }
      if (s.y > h || s.y < 0) {
        s.dy = -s.dy;
      }
      const r = Math.sin(s.x / (w / 3)) * 127 + 128,
        g = Math.sin(s.x / (w / 3) + (2 * Math.PI) / 3) * 127 + 128,
        b = Math.sin(s.x / (w / 3) + (4 * Math.PI) / 3) * 127 + 128;
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(s.x, s.y, 20, 20);
    });
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

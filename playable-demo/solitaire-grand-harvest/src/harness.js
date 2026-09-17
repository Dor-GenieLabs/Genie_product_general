// Deterministic in-browser test harness (same clock virtualisation as examples/coin-master/src/harness.js).
// autoplay(): follows the hint (first playable card, else draw) until the end card shows.
window.gameEnd = function () { window.__ge = true; };
var realNow = performance.now.bind(performance), realDate = Date.now(); window.vt = realNow(); var vt0 = vt;
performance.now = function () { return vt; }; Date.now = function () { return realDate + (vt - vt0); };
window.adv = function (ms) { var g = app.game, n = Math.max(1, Math.round(ms / 16.667)); for (var i = 0; i < n; i++) { vt += 16.667; g.step(vt, 16.667); } };
window.shot = function (name) { return new Promise(function (res) { app.game.renderer.snapshot(function (img) { fetch('http://127.0.0.1:8766/' + name + '.png', { method: 'POST', body: img.src }).then(function () { res('saved ' + name); }).catch(function (e) { res('err ' + e); }); }); adv(40); }); };
window.tap = function (lx, ly) { var c = document.querySelector('canvas'), r = c.getBoundingClientRect(); var x = r.left + lx * r.width / 720, y = r.top + ly * r.height / 1280; var o = { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, buttons: 1 }; c.dispatchEvent(new MouseEvent('mousedown', o)); c.dispatchEvent(new MouseEvent('mouseup', Object.assign({}, o, { buttons: 0 }))); adv(34); };
window.st = function () { var s = app.game.scene.keys.Main; return { state: s.state, coins: s.coins, streak: s.streak, taps: s.taps, left: s.boardLeft(), stock: s.stockCards.length, ended: s.ended }; };
window.autoplay = function (maxSteps) {
  var s = app.game.scene.keys.Main, log = [], steps = 0;
  while (!s.ended && steps++ < (maxSteps || 60)) {
    var p = s.playable();
    if (p.length) { tap(p[0].x, p[0].y); log.push('play ' + p[0].v); } else { tap(175, 812); log.push('draw'); }
    adv(700);
  }
  adv(2500);
  return { log: log, st: st(), endcard: document.getElementById('endcard').className, gameEndCalled: !!window.__ge };
};

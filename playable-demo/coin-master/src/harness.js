// Deterministic browser test harness for the Coin Master playable.
// Paste into the devtools console (or run through an automation tool) after the page loads.
// It virtualizes both clocks Phaser uses (performance.now for the game loop / timers,
// Date.now for the TweenManager) and steps the game loop by hand, so the flow runs the
// same whether the tab is visible, hidden, or throttled.
//
//   adv(ms)        advance the game by ms of virtual time (renders every frame)
//   tap(lx, ly)    dispatch a click at logical 720x1280 coordinates
//   st()           current game state summary
//   shot(name)     POST a renderer snapshot PNG to http://127.0.0.1:8766/<name>.png
//                  (start a receiver first; see knowledge/apk-to-playable-lessons.md)
window.gameEnd = function () { window.__ge = true; };
var realNow = performance.now.bind(performance), realDate = Date.now();
window.vt = realNow(); var vt0 = vt;
performance.now = function () { return vt; };
Date.now = function () { return realDate + (vt - vt0); };
window.adv = function (ms) { var g = app.game, n = Math.max(1, Math.round(ms / 16.667)); for (var i = 0; i < n; i++) { vt += 16.667; g.step(vt, 16.667); } };
window.shot = function (name) { return new Promise(function (res) { app.game.renderer.snapshot(function (img) { fetch('http://127.0.0.1:8766/' + name + '.png', { method: 'POST', body: img.src }).then(function () { res('saved ' + name); }).catch(function (e) { res('err ' + e); }); }); adv(40); }); };
window.tap = function (lx, ly) { var c = document.querySelector('canvas'), r = c.getBoundingClientRect(); var x = r.left + lx * r.width / 720, y = r.top + ly * r.height / 1280; var o = { bubbles: true, cancelable: true, clientX: x, clientY: y, button: 0, buttons: 1 }; c.dispatchEvent(new MouseEvent('mousedown', o)); c.dispatchEvent(new MouseEvent('mouseup', Object.assign({}, o, { buttons: 0 }))); adv(34); };
window.st = function () { var s = app.game.scene.keys.Main; return { state: s.state, coins: s.coins, spins: s.spins, hand: s.hand.visible, ended: s.ended }; };

// Full scripted playthrough (spin -> coins, spin -> attack, spin -> raid, build, end card):
window.playthrough = async function () {
  var log = []; function L(k) { log.push(k + ': ' + JSON.stringify(st())); }
  adv(1000); L('start');
  tap(360, 1150); adv(5000); L('after spin 1 (coins)');
  tap(360, 1150); adv(4000); L('attack open'); tap(415, 640); adv(3400); L('after attack');
  tap(360, 1150); adv(4000); L('raid open'); tap(250, 520); adv(1200); tap(470, 500); adv(1200); tap(300, 700); adv(3700); L('after raid');
  tap(620, 560); adv(3000); L('after build');
  return { log: log, endcard: document.getElementById('endcard').className, gameEndCalled: !!window.__ge };
};

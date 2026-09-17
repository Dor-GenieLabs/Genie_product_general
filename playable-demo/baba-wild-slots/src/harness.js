// Deterministic browser test harness for the Baba Wild Slots playable.
// Same idea as examples/coin-master/src/harness.js: virtualize both clocks Phaser uses
// (performance.now for the game loop / timers, Date.now for the TweenManager) and step the
// game loop by hand, so the flow runs the same whether the tab is visible, hidden, or throttled.
//
//   adv(ms)        advance the game by ms of virtual time (renders every frame)
//   tap(lx, ly)    dispatch a click at logical 720x1280 coordinates
//   st()           current game state summary
//   shot(name)     POST a renderer snapshot PNG to http://127.0.0.1:8768/<name>.png (start snapshot_receiver.py first)
window.gameEnd = function () { window.__ge = true; };
var realNow = performance.now.bind(performance), realDate = Date.now();
window.vt = realNow(); var vt0 = vt;
performance.now = function () { return vt; };
Date.now = function () { return realDate + (vt - vt0); };
window.adv = function (ms) { var g = app.game, n = Math.max(1, Math.round(ms / 16.667)); for (var i = 0; i < n; i++) { vt += 16.667; g.step(vt, 16.667); } };
window.shot = function (name) { return new Promise(function (res) { app.game.renderer.snapshot(function (img) { fetch('http://127.0.0.1:8768/' + name + '.png', { method: 'POST', body: img.src }).then(function () { res('saved ' + name); }).catch(function (e) { res('err ' + e); }); }); adv(40); }); };
window.tap = function (lx, ly) { var sc = app.game.scale; sc.transformX = function (x) { return x; }; sc.transformY = function (y) { return y; }; var c = document.querySelector('canvas'); var o = { bubbles: true, cancelable: true, clientX: lx, clientY: ly, button: 0, buttons: 1 }; c.dispatchEvent(new MouseEvent('mousedown', o)); adv(17); c.dispatchEvent(new MouseEvent('mouseup', Object.assign({}, o, { buttons: 0 }))); adv(17); };
window.st = function () { var s = app.game.scene.keys.Main; return { state: s.state, coins: s.coins, win: s.winShown, spinIndex: s.spinIndex, hand: s.hand.visible, ended: s.ended, reels: s.reels.map(function (r) { return Math.round(r.pos * 100) / 100; }) }; };

// Full scripted playthrough (spin 1 line win, spin 2 anticipation + jackpot + big win, end card):
window.playthrough = async function () {
  var log = []; function L(k) { log.push(k + ': ' + JSON.stringify(st())); }
  adv(1000); L('start');
  tap(360, 945); adv(2600); L('spin 1 stopped'); adv(2200); L('after line win');
  tap(360, 945); adv(2400); L('anticipation'); adv(2400); L('spin 2 stopped'); adv(1500); L('big win open');
  adv(4000); L('counter done'); adv(4500); L('after collect');
  return { log: log, endcard: document.getElementById('endcard').className, gameEndCalled: !!window.__ge };
};

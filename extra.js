// 날짜에 따라 자동으로: D-day 표시, 끝난 팝업은 '종료된 팝업'으로 이동
(function () {
  var now = new Date();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  function d(s) { var a = s.split('-'); return new Date(+a[0], a[1] - 1, +a[2]); }
  function diff(s) { return Math.round((d(s) - today) / 86400000); }

  var board = document.getElementById('board');
  if (board) {
    var endedBoard = document.getElementById('ended-board');
    var ended = 0;
    Array.prototype.slice.call(board.querySelectorAll('li[data-end]')).forEach(function (li) {
      var left = diff(li.dataset.end), toStart = diff(li.dataset.start);
      var tag = li.querySelector('[data-dday]');
      if (left < 0) { endedBoard.appendChild(li); ended++; if (tag) tag.remove(); return; }
      if (!tag) return;
      if (toStart > 0) { var s = d(li.dataset.start); tag.textContent = (s.getMonth() + 1) + '.' + s.getDate() + ' 오픈'; tag.classList.add('opens'); }
      else if (left === 0) tag.textContent = '오늘 종료';
      else if (left <= 3) tag.textContent = 'D-' + left + ' 종료 임박';
      else tag.remove();
    });
    if (ended) {
      document.getElementById('ended').hidden = false;
      document.getElementById('ended-count').textContent = ended;
      document.getElementById('live-count').textContent = board.querySelectorAll('li[data-end]').length;
    }
  }
  var main = document.querySelector('main[data-end]');
  if (main && diff(main.dataset.end) < 0) document.getElementById('ended-banner').hidden = false;
})();

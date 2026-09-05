/* One runtime for interactions. All travel content is already in the HTML. */
(function (root) {
  'use strict';
  const toMinutes = value => {
    if (typeof value !== 'string' || !/^\d{2}:\d{2}$/.test(value)) return NaN;
    const [h, m] = value.split(':').map(Number);
    return h <= 24 && m < 60 && (h < 24 || m === 0) ? h * 60 + m : NaN;
  };
  function windowResult(now, end, nowDay, endDay, buffer) {
    const n = toMinutes(now), e = toMinutes(end), b = Number(buffer);
    if (!Number.isFinite(n) || !Number.isFinite(e) || n >= 1440 || e >= 1440 ||
        ![0, 1].includes(Number(nowDay)) || ![0, 1].includes(Number(endDay)) ||
        buffer === '' || !Number.isInteger(b) || b < 0 || b > 120) {
      return { valid: false, error: '請填入有效時間與 0–120 分鐘整數緩衝。' };
    }
    const start = n + Number(nowDay) * 1440, deadline = e + Number(endDay) * 1440;
    const raw = deadline - start;
    return { valid: true, start, deadline, raw, buffer: b, available: Math.max(0, raw - b) };
  }
  function evaluateOption(o, w) {
    if (!w.valid) return { level: 'no', label: '✕ 請先修正時間', reason: w.error };
    if (w.raw <= 0) return { level: 'no', label: '✕ 現在不要去了', reason: '集合時間已到或早於現在；若確實跨午夜，請選正確的翌日。' };
    const required = o.out + o.visit + o.back + (o.checkin || 0);
    let need = required, suffix = '';
    if (o.departures) {
      const departure = o.departures.map(toMinutes).find(t =>
        w.start + o.out + o.checkin <= t && t + o.visit + o.back + w.buffer <= w.deadline);
      if (departure === undefined) return { level: 'no', label: '✕ 來不及', reason: '沒有能趕上、完成 90 分鐘遊程並準時回飯店的班次。須同時容納去程、提早報到、候車與回程。' };
      need = departure + o.visit + o.back - w.start;
      suffix = `可試 ${String(Math.floor(departure / 60)).padStart(2, '0')}:${String(departure % 60).padStart(2, '0')} 班，含候車；仍須確認有票。`;
    }
    if (o.departBy && w.start >= toMinutes(o.departBy)) {
      return { level: 'no', label: '✕ 現在不要去了', reason: `已到 ${o.departBy} 建議出發截止；今晚休息較值得。` };
    }
    let closingSlack = Infinity;
    for (const s of (o.steps || [])) {
      if (s.close) closingSlack = Math.min(closingSlack, toMinutes(s.close) - w.start - s.end);
      if ((s.open && w.start + (s.start || 0) < toMinutes(s.open)) ||
          (s.close && w.start + s.end > toMinutes(s.close))) {
        return { level: 'no', label: '✕ 不建議', reason: `${s.name} 的預估到訪時段超出已查核營業時間${s.close ? '（' + s.close + ' 關閉）' : ''}。不要只看總剩餘時間。` };
      }
    }
    const spare = w.available - need;
    if (spare < 0) return { level: 'no', label: '✕ 不建議', reason: `扣除緩衝後還差 ${Math.ceil(-spare)} 分鐘。${o.rest ? '' : '請縮短活動或改選更近的方案。'}` };
    if (spare < 15 || closingSlack < 10) return { level: 'tight', label: '△ 可以但會趕', reason: `${suffix}做完約餘 ${Math.floor(spare)} 分鐘額外餘裕。${closingSlack < 10 ? '到訪已接近關門，若開始收攤立即改短線。' : '一旦排隊或塞車就縮短活動。'}` };
    if (o.caution) return { level: 'tight', label: '△ 時間夠・先確認', reason: `${suffix}時間上仍有約 ${Math.floor(spare)} 分鐘餘裕；現場條件未確認前不要當成已可成行。` };
    return { level: 'yes', label: '✓ 可以・值得去', reason: `${suffix}做完仍有約 ${Math.floor(spare)} 分鐘餘裕，另保留你設定的 ${w.buffer} 分緩衝。` };
  }
  // Exposed for the build-time boundary checks; the browser uses these same functions.
  if (typeof module !== 'undefined' && module.exports) module.exports = { toMinutes, windowResult, evaluateOption };
  if (typeof document === 'undefined') return;

  function londonClock() {
    const parts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/London', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
    const p = Object.fromEntries(parts.map(x => [x.type, x.value]));
    return { date: `${p.year}-${p.month}-${p.day}`, time: `${p.hour}:${p.minute}` };
  }
  function dayOffset(a, b) { return Math.round((Date.parse(a + 'T12:00:00Z') - Date.parse(b + 'T12:00:00Z')) / 86400000); }
  const clock = londonClock();
  const trip = document.body.dataset;
  const tripDay = Math.min(Number(trip.tripDays), Math.max(1, dayOffset(clock.date, trip.tripStart) + 1));
  function setDayLinks(n) {
    document.querySelectorAll('[data-today]').forEach(link => {
      const kind = link.dataset.today, target = kind === 'schedule' ? n : Math.min(Number(trip.lastFree), Math.max(Number(trip.firstFree), n));
      link.href = `day-${target}.html` + (kind === 'schedule' ? '' : `?mode=${kind === 'night' ? 'night' : target === 7 ? 'airport' : 'day'}#free-time`);
    });
  }
  setDayLinks(tripDay);
  const todayNote = document.querySelector('.today-note');
  const homeDay = document.querySelector('[data-home-day]');
  if (homeDay) {
    const requestedDay = Number(new URLSearchParams(location.search).get('day'));
    function selectHomeDay(n, chosen) {
      homeDay.value = String(n); setDayLinks(n);
      document.querySelectorAll('[data-day-preview]').forEach(card => { card.hidden = Number(card.dataset.dayPreview) !== n; });
      const inTrip = clock.date >= trip.tripStart && clock.date <= trip.tripEnd;
      todayNote.textContent = chosen ? `正在查看 D${n}。` : inTrip ? `英國現在 ${clock.time}・今天 D${n}。` : clock.date < trip.tripStart ? '出發前先看 D1，也可在上方選其他日期。' : '旅程已結束，可以選日期回看攻略。';
      if (n === 1 || n === 8) todayNote.textContent += ` 當天沒有自由活動，試算入口先帶你看 D${n === 1 ? 2 : 7}。`;
    }
    selectHomeDay(requestedDay >= 1 && requestedDay <= 8 && Number.isInteger(requestedDay) ? requestedDay : tripDay, requestedDay >= 1 && requestedDay <= 8 && Number.isInteger(requestedDay));
    homeDay.addEventListener('change', () => {
      const n = Number(homeDay.value); selectHomeDay(n, true);
      const url = new URL(location.href); url.searchParams.set('day', String(n)); history.replaceState(null, '', url);
    });
  }
  const daySelect = document.querySelector('[data-day-select]');
  if (daySelect) daySelect.addEventListener('change', () => { location.href = `day-${daySelect.value}.html`; });

  const section = document.querySelector('.free-section');
  if (section) {
    const form = section.querySelector('form'), tabs = [...section.querySelectorAll('[role="tab"]')];
    const infos = [...section.querySelectorAll('[data-mode-info]')], optionLists = [...section.querySelectorAll('[data-mode-options]')];
    const panel = section.querySelector('[role="tabpanel"]'), number = section.querySelector('.result-number'), detail = section.querySelector('.result-detail');
    const note = section.querySelector('.clock-note');
    const states = new Map();
    let active = -1, disabled = false, showUnavailable = false;
    const toggleUnavailable = section.querySelector('#toggle-unavailable');
    const optionSummary = section.querySelector('.option-summary');
    const emptyOptions = section.querySelector('.no-options');
    function filterOptions() {
      const cards = [...optionLists[active].querySelectorAll('[data-option]')];
      const counts = { yes: 0, tight: 0, no: 0 };
      cards.forEach(card => {
        if (card.dataset.level) counts[card.dataset.level]++;
        card.hidden = !showUnavailable && card.dataset.level === 'no';
      });
      optionSummary.textContent = disabled ? '' : cards.some(c => !c.dataset.level) ? '請重新計算，更新可去的方案。' : `${counts.yes} 個可以・${counts.tight} 個較趕／需確認`;
      toggleUnavailable.hidden = disabled || counts.no === 0;
      toggleUnavailable.textContent = showUnavailable ? '收起不建議方案' : `查看 ${counts.no} 個不建議方案及原因`;
      toggleUnavailable.setAttribute('aria-expanded', String(showUnavailable));
      emptyOptions.hidden = disabled || cards.some(c => !c.dataset.level) || counts.yes + counts.tight > 0;
      section.querySelector('.result-legend').hidden = disabled;
    }
    toggleUnavailable.addEventListener('click', () => { showUnavailable = !showUnavailable; filterOptions(); });
    function saveState() {
      if (active >= 0) states.set(active, { now: form.elements.now.value, end: form.elements.end.value, nowDay: form.elements.nowDay.value, endDay: form.elements.endDay.value, buffer: form.elements.buffer.value, note: note.textContent });
    }
    function calculate(event) {
      if (event) event.preventDefault();
      if (disabled) {
        number.textContent = '—'; detail.textContent = '本時段未安排自由活動，請切換其他時段。'; filterOptions();
        return;
      }
      const w = windowResult(form.elements.now.value, form.elements.end.value, form.elements.nowDay.value, form.elements.endDay.value, form.elements.buffer.value);
      number.textContent = w.valid ? `${w.available} 分鐘` : '請檢查';
      detail.textContent = !w.valid ? w.error : w.raw <= 0 ? '集合時間已到或已過；不會自動當成明天。' : `原有 ${w.raw} 分鐘 − 額外緩衝 ${w.buffer} 分鐘。${w.raw > 720 ? '時段超過 12 小時，請再確認日期是否選對。' : ''}`;
      const windowStart = toMinutes(JSON.parse(infos[active].dataset.window).start);
      if (w.valid && w.start < windowStart) detail.textContent += ' 早於推估起點：只有領隊已放行、且你已輸入正式集合時間才可採用結果。';
      const cards = [...optionLists[active].querySelectorAll('[data-option]')];
      cards.forEach(card => {
        const r = evaluateOption(JSON.parse(card.dataset.option), w);
        card.dataset.level = r.level;
        const verdict = card.querySelector('.verdict'); verdict.textContent = r.label; verdict.className = 'verdict ' + r.level;
        card.querySelector('.option-reason').textContent = r.reason;
        card.querySelector('.buffer-label').textContent = w.valid ? w.buffer : '—';
      });
      filterOptions();
      saveState();
    }
    function setMode(index, fromUser) {
      saveState(); active = index; showUnavailable = false;
      tabs.forEach((t, j) => { t.setAttribute('aria-selected', String(j === index)); t.tabIndex = j === index ? 0 : -1; });
      infos.forEach((x, j) => { x.hidden = j !== index; });
      optionLists.forEach((x, j) => { x.hidden = j !== index; });
      panel.setAttribute('aria-labelledby', tabs[index].id);
      const win = JSON.parse(infos[index].dataset.window);
      disabled = win.disabled;
      form.hidden = disabled;
      const s = states.get(index);
      form.elements.now.value = s ? s.now : win.start;
      form.elements.end.value = s ? s.end : win.end;
      form.elements.nowDay.value = s ? s.nowDay : '0';
      form.elements.endDay.value = s ? s.endDay : '0';
      form.elements.buffer.value = s ? s.buffer : win.buffer;
      note.textContent = s ? s.note : '先用推估時段試算；領隊公布後，請改填集合時間。以下皆為英國時間。';
      if (!s && clock.date === section.dataset.date && !disabled) {
        form.elements.now.value = clock.time;
        note.textContent = `已帶入英國 ${clock.date} ${clock.time}；集合時間仍是推估，請以領隊通知替換。`;
      }
      calculate();
      if (fromUser) {
        const url = new URL(location.href); url.searchParams.set('mode', tabs[index].dataset.kind);
        history.replaceState(null, '', url);
      }
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => setMode(index, true));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
        else if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = tabs.length - 1;
        if (next !== undefined) { event.preventDefault(); setMode(next, true); tabs[next].focus(); }
      });
    });
    form.addEventListener('submit', calculate);
    function markDirty() {
      number.textContent = '待重算';
      detail.textContent = '時間已變更，請按「重新計算」更新結果。';
      optionLists[active].querySelectorAll('.option-card').forEach(card => {
        delete card.dataset.level;
        const verdict = card.querySelector('.verdict'); verdict.textContent = '待重新計算'; verdict.className = 'verdict pending';
        card.querySelector('.option-reason').textContent = '請用更新後的時間重新計算。';
      });
      filterOptions();
    }
    form.addEventListener('input', markDirty);
    form.addEventListener('change', markDirty);
    section.querySelector('#use-now').addEventListener('click', () => {
      const c = londonClock(), offset = dayOffset(c.date, section.dataset.date);
      if (offset < 0 || offset > 1) { note.textContent = `英國現在 ${c.date} ${c.time}，不是這一天；保留試算欄位，請手動填入情境時間。`; return; }
      form.elements.now.value = c.time; form.elements.nowDay.value = String(offset);
      note.textContent = `已帶入英國 ${c.date} ${c.time}；請確認結束日期與領隊集合時間。`; calculate();
    });
    document.querySelectorAll('[data-free-link]').forEach(link => link.addEventListener('click', event => {
      const next = tabs.findIndex(t => t.dataset.kind === link.dataset.freeLink);
      if (next < 0) return;
      event.preventDefault(); setMode(next, true);
      location.hash = 'free-time'; section.scrollIntoView({ block: 'start' });
    }));
    const requested = new URLSearchParams(location.search).get('mode');
    const initial = tabs.findIndex(t => t.dataset.kind === requested);
    setMode(initial < 0 ? 0 : initial, false);
  }
  function revealAnchor() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (target && target.tagName === 'DETAILS') { target.open = true; requestAnimationFrame(() => target.scrollIntoView({ block: 'start' })); }
  }
  revealAnchor();
  window.addEventListener('hashchange', revealAnchor);
  document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', () => setTimeout(revealAnchor, 0)));
  const checks = [...document.querySelectorAll('[data-check]')];
  if (checks.length) {
    const key = 'ian-uk-checklist-2026', count = document.getElementById('check-count'), storageNote = document.getElementById('storage-note');
    let checked = {};
    try { checked = JSON.parse(localStorage.getItem(key) || '{}'); if (!checked || typeof checked !== 'object' || Array.isArray(checked)) checked = {}; }
    catch (_) { storageNote.textContent = '目前無法讀取本機儲存；仍可暫時勾選，離開後可能不保留。'; }
    const update = () => { const done = checks.filter(c => c.checked).length; count.textContent = done; document.getElementById('check-progress').value = done; };
    checks.forEach(c => {
      c.checked = checked[c.dataset.check] === true;
      c.addEventListener('change', () => {
        checked[c.dataset.check] = c.checked; update();
        try { localStorage.setItem(key, JSON.stringify(checked)); }
        catch (_) { storageNote.textContent = '這台裝置無法儲存勾選，請改用截圖。'; }
      });
    });
    update();
  }
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const target = document.getElementById(button.dataset.copy);
    const status = button.parentElement.querySelector('.copy-result');
    try {
      await navigator.clipboard.writeText(target.textContent.trim());
      status.textContent = button.dataset.copy === 'site-link' ? '已複製網站連結，可以貼到團員群組。' : '已複製英文，也可以直接出示這頁。';
    } catch (_) {
      status.textContent = '請長按上方文字複製，或直接把這頁給對方看。';
    }
  }));
})(typeof globalThis !== 'undefined' ? globalThis : this);

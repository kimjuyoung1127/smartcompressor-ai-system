const root = document.documentElement;
    const themeBtn = document.getElementById('theme-toggle');
    themeBtn?.addEventListener('click', () => {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      document.documentElement.setAttribute('data-theme', isLight ? 'dark' : 'light');
      themeBtn.setAttribute('aria-pressed', String(!isLight));
    });

    // Confidence slider sync
    const cSlider = document.getElementById('confidence');
    const cNum = document.getElementById('confidence-num');
    cSlider?.addEventListener('input', () => { cNum.value = cSlider.value; markDirty(); });
    cNum?.addEventListener('input', () => { cSlider.value = cNum.value; markDirty(); });

    // Label button active state
    const labelGrid = document.getElementById('label-grid');
    let currentLabel = 'normal';
    labelGrid?.addEventListener('click', (e) => {
      const btn = e.target.closest('.label-btn');
      if(!btn) return;
      labelGrid.querySelectorAll('.label-btn').forEach(b => { b.dataset.active = 'false'; b.setAttribute('aria-pressed','false'); });
      btn.dataset.active = 'true'; btn.setAttribute('aria-pressed','true');
      currentLabel = btn.dataset.label;
      markDirty();
    });

    // Autosave indicator (UI only)
    const dot = document.getElementById('autosave-dot');
    let autosaveTimer;
    function markDirty(){
      dot.dataset.state = 'dirty';
      clearTimeout(autosaveTimer);
      autosaveTimer = setTimeout(()=>{ dot.dataset.state = 'saved'; }, 1200);
    }



    // Keyboard shortcuts (UI-layer only; audio wiring will be in external JS)
    document.addEventListener('keydown', (e)=>{
      if(['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
      if(e.code==='Digit1' || e.code==='Digit2' || e.code==='Digit3' || e.code==='Digit4'){
        const map = {Digit1:'normal', Digit2:'warning', Digit3:'critical', Digit4:'unknown'};
        const label = map[e.code];
        const target = [...document.querySelectorAll('.label-btn')].find(b=>b.dataset.label===label);
        if(target){ target.click(); }
      }
    });
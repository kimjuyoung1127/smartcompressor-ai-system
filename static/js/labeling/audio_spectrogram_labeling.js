document.addEventListener('DOMContentLoaded', () => {
  // ---------------- Globals and State ----------------
  let wavesurfer;
  let spectrogram;
  let annotorious;
  let currentAudioId = null;
  let currentAnnotations = [];
  let autosaveTimer;

  // ---------------- DOM Elements ----------------
  const dom = {
    playBtn: document.getElementById('play-btn'),
    backwardBtn: document.getElementById('backward'),
    forwardBtn: document.getElementById('forward'),
    loopBtn: document.getElementById('loop-btn'),
    zoomInBtn: document.getElementById('zoom-in'),
    zoomOutBtn: document.getElementById('zoom-out'),
    playbackSpeedSelect: document.getElementById('playback-speed'),
    timeIndicator: document.getElementById('t-ind'),
    freqIndicator: document.getElementById('f-ind'),
    timeCursor: document.getElementById('time-cursor'),
    queueList: document.getElementById('queue'),
    labelGrid: document.getElementById('label-grid'),
    confidenceSlider: document.getElementById('confidence'),
    confidenceNum: document.getElementById('confidence-num'),
    notesArea: document.getElementById('notes'),
    saveBtn: document.getElementById('save-btn'),
    nextBtn: document.getElementById('next-btn'),
    undoBtn: document.getElementById('undo-btn'),
    redoBtn: document.getElementById('redo-btn'),
    autosaveDot: document.getElementById('autosave-dot'),
  };

  // ---------------- Auth Helper ----------------
  function getAuthHeaders() {
    if (window.authManager && window.authManager.currentUser) {
      const user = window.authManager.currentUser;
      return {
        'X-User-ID': user.id || '1', // Fallback for safety
        'X-User-Role': user.role || 'labeler', // Fallback for safety
      };
    }
    console.warn('AuthManager not found or user not logged in. Using default headers for testing.');
    // Return default headers for testing if authManager is not available
    return {
      'X-User-ID': '1',
      'X-User-Role': 'labeler',
    };
  }

  // ---------------- Wavesurfer & Plugins Init ----------------
  function initWavesurfer() {
    if (wavesurfer) wavesurfer.destroy();

    wavesurfer = WaveSurfer.create({
      container: '#waveform',
      waveColor: '#9aa0a6',
      progressColor: '#8a5cfe',
      cursorColor: 'transparent', // We use a custom cursor
      barWidth: 3,
      barRadius: 3,
      height: 120,
      responsive: true,
    });

    const wsTimeline = WaveSurfer.Timeline.create({ container: '#timeline' });

    spectrogram = WaveSurfer.Spectrogram.create({
      wavesurfer: wavesurfer,
      container: '#spectrogram',
      labels: true,
      colorMap: 'viridis',
      fftSamples: 1024,
    });

    wavesurfer.on('timeupdate', (currentTime) => updateIndicators(currentTime));
    wavesurfer.on('play', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>');
    wavesurfer.on('pause', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-play"></i>');
    wavesurfer.on('finish', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-play"></i>');

    // Initialize Annotorious once the spectrogram canvas is ready
    spectrogram.on('ready', initAnnotorious);
  }

  // ---------------- Annotorious Init ----------------
  function initAnnotorious() {
    if (annotorious) annotorious.destroy();

    const specCanvas = document.querySelector('#spectrogram canvas');
    if (!specCanvas) {
      console.error('Spectrogram canvas not found!');
      return;
    }

    annotorious = Annotorious.init({
      image: specCanvas,
      widgets: [
        {
          widget: 'TAG',
          vocabulary: ['normal', 'warning', 'critical', 'unknown']
        }
      ]
    });

    // Bind annotation events
    annotorious.on('createAnnotation', handleAnnotationChange);
    annotorious.on('updateAnnotation', handleAnnotationChange);
    annotorious.on('deleteAnnotation', handleAnnotationChange);

    // Restore annotations if any
    annotorious.setAnnotations(currentAnnotations);
  }

  // ---------------- Event Handlers & Logic ----------------

  function updateIndicators(currentTime) {
    const duration = wavesurfer.getDuration();
    dom.timeIndicator.textContent = `${formatTime(currentTime)} / ${formatTime(duration)}`;
    const cursorPercentage = (currentTime / duration) * 100;
    dom.timeCursor.style.left = `${cursorPercentage}%`;
  }

  function handleAnnotationChange() {
    currentAnnotations = annotorious.getAnnotations();
    markDirty();
  }

  function markDirty() {
    dom.autosaveDot.dataset.state = 'dirty';
    clearTimeout(autosaveTimer);
    autosaveTimer = setTimeout(autosave, 3000);
  }

  function autosave() {
    console.log('Auto-saving to localStorage...');
    const state = {
      annotations: currentAnnotations,
      label: getCurrentLabel(),
      confidence: dom.confidenceSlider.value,
      notes: dom.notesArea.value,
    };
    localStorage.setItem(`audio-label-state-${currentAudioId}`, JSON.stringify(state));
    dom.autosaveDot.dataset.state = 'saved';
  }

  async function loadAudio(file) {
    if (!file) return;
    currentAudioId = file.id;

    // Reset state
    if (annotorious) annotorious.clearAnnotations();
    currentAnnotations = [];

    // Load from localStorage if exists
    const savedState = localStorage.getItem(`audio-label-state-${currentAudioId}`);
    if (savedState) {
      const state = JSON.parse(savedState);
      currentAnnotations = state.annotations || [];
      dom.notesArea.value = state.notes || '';
      dom.confidenceSlider.value = state.confidence || 90;
      dom.confidenceNum.value = state.confidence || 90;
      setActiveLabel(state.label || 'normal');
    } else {
      // Reset to default
      dom.notesArea.value = '';
      dom.confidenceSlider.value = 90;
      dom.confidenceNum.value = 90;
      setActiveLabel('normal');
    }

    try {
      // First, fetch the peaks data
      const peaksResponse = await fetch(file.peaks_url, { headers: getAuthHeaders() });
      if (!peaksResponse.ok) throw new Error('Failed to load peaks data');
      const peaksData = await peaksResponse.json();

      // Now load the audio with the fetched peaks
      wavesurfer.load(file.url, peaksData.data);

    } catch (error) {
        console.error('Error loading audio or peaks:', error);
        // If peaks fail, load audio anyway
        wavesurfer.load(file.url);
    }
    
    // Update queue UI
    document.querySelectorAll('#queue .file-item').forEach(item => {
        item.classList.toggle('active', item.dataset.id == currentAudioId);
    });
  }

  // ---------------- API & Data Loading ----------------

  async function fetchQueue() {
    try {
      const response = await fetch('/api/labeling/queue', { headers: getAuthHeaders() });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const queue = await response.json();
      
      // Keep track of the full queue data
      window.labelingQueue = queue;

      renderQueue(queue);
      
      // Load the first unprocessed item
      const firstToProcess = queue.find(item => !item.is_processed);
      if (firstToProcess) {
        loadAudio(firstToProcess);
      } else {
        console.log("No items to process in the queue.");
        // Handle empty queue case - maybe show a message
      }

    } catch (error) {
      console.error('Failed to fetch queue:', error);
      // Display an error to the user
      dom.queueList.innerHTML = `<li style="color: var(--danger);">Failed to load queue.</li>`;
    }
  }

  function renderQueue(queue) {
    dom.queueList.innerHTML = queue.map(item => `
      <li class="file-item" data-id="${item.id}" role="option">
        <div class="file-rows">
          <div class="file-name">${item.file_name}</div>
          <span class="status-badge ${item.is_processed ? 'processed' : 'not-processed'}">
            ${item.is_processed ? '완료' : '처리필요'}
          </span>
        </div>
      </li>`
    ).join('');
    
    dom.queueList.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('click', () => {
            const fileId = parseInt(item.dataset.id, 10);
            // Use the globally stored queue data
            const fileToLoad = window.labelingQueue.find(f => f.id === fileId);
            loadAudio(fileToLoad);
        });
    });
  }

  async function saveAndNext() {
    if (!currentAudioId) return;

    const payload = {
      audio_file_id: currentAudioId,
      label: getCurrentLabel(),
      confidence: parseInt(dom.confidenceSlider.value, 10),
      notes: dom.notesArea.value,
      annotations: currentAnnotations.map(anno => {
        const [x, y, w, h] = anno.target.selector.value.replace('xywh=pixel:', '').split(',').map(parseFloat);
        return {
          time_start: pixelToTime(x),
          time_end: pixelToTime(x + w),
          freq_min: pixelToFreq(y + h),
          freq_max: pixelToFreq(y),
          label: anno.body.length > 0 ? anno.body[0].value : 'unknown'
        };
      })
    };

    console.log('Saving data:', JSON.stringify(payload, null, 2));

    try {
      const response = await fetch('/api/labeling/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Save failed');
      }
      
      console.log('Save successful.');
      localStorage.removeItem(`audio-label-state-${currentAudioId}`); // Clear saved state
      
      // Mark as processed in the UI
      const savedItem = dom.queueList.querySelector(`[data-id="${currentAudioId}"]`);
      if(savedItem) {
          const badge = savedItem.querySelector('.status-badge');
          badge.classList.remove('not-processed');
          badge.classList.add('processed');
          badge.textContent = '완료';
      }

      // Load next file
      const currentIdx = window.labelingQueue.findIndex(item => item.id == currentAudioId);
      const nextItem = window.labelingQueue[currentIdx + 1];
      if (nextItem) {
        loadAudio(nextItem);
      } else {
        alert('Queue complete!');
      }

    } catch (error) {
      console.error('Failed to save labels:', error);
      alert(`저장에 실패했습니다: ${error.message}`);
    }
  }

  // ---------------- UI Bindings ----------------
  dom.playBtn.addEventListener('click', () => wavesurfer.playPause());
  dom.backwardBtn.addEventListener('click', () => wavesurfer.skip(-0.1));
  dom.forwardBtn.addEventListener('click', () => wavesurfer.skip(0.1));
  dom.zoomInBtn.addEventListener('click', () => wavesurfer.zoom(wavesurfer.getCurrentTime(), wavesurfer.getScroll() * 1.2));
  dom.zoomOutBtn.addEventListener('click', () => wavesurfer.zoom(wavesurfer.getCurrentTime(), wavesurfer.getScroll() * 0.8));
  dom.playbackSpeedSelect.addEventListener('change', (e) => wavesurfer.setPlaybackRate(parseFloat(e.target.value)));
  dom.saveBtn.addEventListener('click', saveAndNext);
  dom.nextBtn.addEventListener('click', saveAndNext);

  // ---------------- Helpers ----------------
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const dec = Math.floor((seconds - Math.floor(seconds)) * 10);
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${dec}`;
  }

  function getCurrentLabel() {
    return dom.labelGrid.querySelector('.label-btn[data-active="true"]').dataset.label;
  }

  function setActiveLabel(label) {
    dom.labelGrid.querySelectorAll('.label-btn').forEach(btn => {
      const isActive = btn.dataset.label === label;
      btn.dataset.active = isActive;
      btn.setAttribute('aria-pressed', isActive);
    });
  }

  function pixelToTime(pixel) {
    const duration = wavesurfer.getDuration();
    return (pixel / spectrogram.width) * duration;
  }

  function pixelToFreq(pixel) {
    const freqRange = spectrogram.options.labels ? spectrogram.options.frequencyMax : wavesurfer.options.sampleRate / 2;
    return freqRange * (1 - (pixel / spectrogram.height));
  }

  // ---------------- Keyboard Shortcuts ----------------
  document.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    const keyMap = {
      'Space': () => { e.preventDefault(); wavesurfer.playPause(); },
      'ArrowLeft': () => wavesurfer.skip(-0.1),
      'ArrowRight': () => wavesurfer.skip(0.1),
      'KeyL': () => dom.loopBtn.click(),
    };

    if (keyMap[e.code]) keyMap[e.code]();
  });

  // ---------------- Initial Load ----------------
  initWavesurfer();
  fetchQueue();
});
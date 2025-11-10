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
    refreshBtn: document.getElementById('refresh-btn'),
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

    // Initialize WaveSurfer with plugins as options
    wavesurfer = WaveSurfer.create({
      container: '#waveform',
      waveColor: '#9aa0a6',
      progressColor: '#8a5cfe',
      cursorColor: 'transparent', // We use a custom cursor
      barWidth: 3,
      barRadius: 3,
      height: 120,
      responsive: true,
      plugins: [
        // Timeline plugin
        WaveSurfer.timeline.create({
          container: '#timeline',
        }),
        // Spectrogram plugin
        WaveSurfer.spectrogram.create({
          container: '#spectrogram',
          labels: true,
          fftSamples: 1024,
        })
      ]
    });

    // The spectrogram plugin instance is the second plugin in the array
    if (wavesurfer && wavesurfer.plugins) {
      spectrogram = wavesurfer.plugins[1];
    }
    
    wavesurfer.on('timeupdate', (currentTime) => updateIndicators(currentTime));
    wavesurfer.on('play', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>');
    wavesurfer.on('pause', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-play"></i>');
    wavesurfer.on('finish', () => dom.playBtn.innerHTML = '<i class="fa-solid fa-play"></i>');

    // Initialize Annotorious once the spectrogram canvas is ready
    wavesurfer.on('decode', initAnnotorious);
    wavesurfer.on('ready', initAnnotorious);
  }

  // ---------------- Annotorious Init ----------------
  function initAnnotorious() {
    if (annotorious) annotorious.destroy();

    // Adding small delay to ensure canvas is rendered
    setTimeout(() => {
      const specCanvas = document.querySelector('#spectrogram canvas');
      if (!specCanvas) {
        console.error('Spectrogram canvas not found! Trying again in 500ms...');
        // Try again after a short delay
        setTimeout(() => {
          const canvasRetry = document.querySelector('#spectrogram canvas');
          if (canvasRetry) {
            initializeAnnotoriousOnCanvas(canvasRetry);
          } else {
            console.error('Spectrogram canvas still not found after retry!');
          }
        }, 500);
        return;
      }
      
      initializeAnnotoriousOnCanvas(specCanvas);
    }, 100);
  }
  
  function initializeAnnotoriousOnCanvas(canvas) {
    try {
      annotorious = Annotorious.init({
        image: canvas,
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
    } catch (error) {
      console.error('Error initializing Annotorious:', error);
    }
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

  // Function to delete a file
  async function deleteFile(fileId, fileName) {
    if (!confirm(`정말로 "${fileName}" 파일을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/labeling/audio/${fileId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '삭제에 실패했습니다');
      }

      // Remove from the local queue list
      window.labelingQueue = window.labelingQueue.filter(item => item.id !== fileId);
      
      // Refresh the UI
      renderQueue(window.labelingQueue);
      
      // If the currently loaded file was deleted, load the next one
      if (currentAudioId === fileId) {
        const nextItem = window.labelingQueue[0]; // Load first available
        if (nextItem) {
          loadAudio(nextItem);
        } else {
          // No files left, reset the view
          if (wavesurfer) {
            wavesurfer.load(''); // Clear current audio
          }
          currentAudioId = null;
        }
      }
      
      console.log(`File ${fileId} deleted successfully`);
      showNotification(`${fileName} 파일이 삭제되었습니다.`, 'success');

    } catch (error) {
      console.error('Failed to delete file:', error);
      showNotification(`파일 삭제 실패: ${error.message}`, 'error');
    }
  }

  function renderQueue(queue) {
    dom.queueList.innerHTML = queue.map(item => `
      <li class="file-item" data-id="${item.id}" role="option">
        <div class="file-rows">
          <div class="file-name">${item.file_name}</div>
          <div>
            <span class="status-badge ${item.is_processed ? 'processed' : 'not-processed'}">
              ${item.is_processed ? '완료' : '처리필요'}
            </span>
            <button class="delete-btn" data-id="${item.id}" title="삭제">
              <i class="fa-solid fa-trash"></i>
            </button>
          </div>
        </div>
      </li>`
    ).join('');
    
    // Add click event to file items to load audio
    dom.queueList.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('click', (e) => {
            // If the click was on the delete button, don't load the file
            if (e.target.closest('.delete-btn')) {
                return;
            }
            
            const fileId = parseInt(item.dataset.id, 10);
            // Use the globally stored queue data
            const fileToLoad = window.labelingQueue.find(f => f.id === fileId);
            loadAudio(fileToLoad);
        });
    });
    
    // Add click event to delete buttons
    dom.queueList.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent triggering the file load click event
            const fileId = parseInt(button.dataset.id, 10);
            const fileItem = button.closest('.file-item');
            const fileName = fileItem.querySelector('.file-name').textContent;
            deleteFile(fileId, fileName);
        });
    });
    
    // Update the queue metrics in the header
    updateQueueMetrics(queue);
  }

  function updateQueueMetrics(queue) {
    const totalFiles = queue.length;
    const completedFiles = queue.filter(item => item.is_processed).length;
    
    document.getElementById('m-queue').textContent = totalFiles;
    document.getElementById('m-done-today').textContent = completedFiles;
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
  dom.refreshBtn?.addEventListener('click', fetchQueue);

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

  // ---------------- File Upload Functionality ----------------
  const uploadBtn = document.getElementById('upload-btn');
  const fileUpload = document.getElementById('file-upload');
  
  uploadBtn?.addEventListener('click', () => {
    fileUpload.click(); // Trigger the hidden file input
  });

  fileUpload?.addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length === 0) return;
    
    // Show a confirmation dialog for multiple files
    if (files.length > 1) {
      const confirmMsg = `정말 ${files.length}개의 파일을 업로드 하시겠습니까?`;
      if (!confirm(confirmMsg)) return;
    }
    
    // Process each file
    for (const file of files) {
      if (!file.type.startsWith('audio/')) {
        alert(`${file.name}은(는) 오디오 파일이 아닙니다.`);
        continue;
      }
      
      await uploadFile(file);
    }
    
    // Reset the file input
    fileUpload.value = '';
    
    // Refresh the queue to show the newly uploaded files
    await fetchQueue();
  });

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append('audio_file', file);
    formData.append('original_filename', file.name);
    
    try {
      const response = await fetch('/api/labeling/upload', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok) {
        console.log(`File ${file.name} uploaded successfully:`, result);
        // Optionally show a success notification
        showNotification(`${file.name} 파일이 성공적으로 업로드되었습니다.`, 'success');
      } else {
        console.error(`Error uploading ${file.name}:`, result.error);
        showNotification(`${file.name} 업로드 실패: ${result.error}`, 'error');
      }
    } catch (error) {
      console.error(`Exception uploading ${file.name}:`, error);
      showNotification(`${file.name} 업로드 중 오류 발생`, 'error');
    }
  }
  
  function showNotification(message, type = 'info') {
    // Simple notification system - could be enhanced with a proper notification library
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      padding: '12px 20px',
      borderRadius: '8px',
      color: 'white',
      zIndex: '10000',
      maxWidth: '400px',
      wordWrap: 'break-word'
    });
    
    // Set background color based on type
    switch(type) {
      case 'success':
        notification.style.backgroundColor = '#48bb78';
        break;
      case 'error':
        notification.style.backgroundColor = '#ef4444';
        break;
      case 'warning':
        notification.style.backgroundColor = '#ed8936';
        break;
      default:
        notification.style.backgroundColor = '#38bdf8';
    }
    
    document.body.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
  }

  // ---------------- Initial Load ----------------
  initWavesurfer();
  fetchQueue();
  
  // Periodically refresh the queue every 30 seconds to keep it updated
  setInterval(fetchQueue, 30000);
});
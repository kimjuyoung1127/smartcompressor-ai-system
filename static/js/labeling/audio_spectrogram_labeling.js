// Audio Spectrogram Labeling Tool JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize wavesurfer
    const wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'rgb(75, 192, 192)',
        progressColor: 'rgba(75, 192, 192, 0.5)',
        cursorColor: '#fff',
        cursorWidth: 2,
        barWidth: 3,
        barRadius: 3,
        barGap: 2,
        responsive: true,
        height: 150,
        normalize: true
    });

    // Initialize Annotorious
    const annotorious = Annotorious.init({
        image: 'spectrogram-img'
    });

    // DOM elements
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const loopBtn = document.getElementById('loop-btn');
    const playbackSpeedSelect = document.getElementById('playback-speed');
    const timeCursor = document.getElementById('time-cursor');
    const confidenceSlider = document.getElementById('confidence-slider');
    const confidenceValue = document.getElementById('confidence-value');
    const saveBtn = document.getElementById('save-btn');
    const resetBtn = document.getElementById('reset-btn');
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    const notesTextarea = document.getElementById('notes');
    const labelButtons = document.querySelectorAll('.label-btn');
    
    // State variables
    let currentLabel = 'normal';
    let currentAudioFileId = null;
    let isPlaying = false;
    let currentPlayTime = 0;

    // Update confidence value display
    confidenceSlider.addEventListener('input', function() {
        confidenceValue.textContent = this.value;
    });

    // Set up label selection
    labelButtons.forEach(button => {
        button.addEventListener('click', function() {
            labelButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentLabel = this.dataset.label;
        });
    });

    // Load a sample audio file
    function loadSampleAudio() {
        wavesurfer.load('https://wavesurfer-js.org/example/media/elanor-donate.mp3');
    }
    
    // Initialize with sample audio
    loadSampleAudio();

    // Play/Pause functionality
    playBtn.addEventListener('click', function() {
        wavesurfer.playPause();
        isPlaying = wavesurfer.isPlaying();
        
        // Update play button icon
        if (isPlaying) {
            playBtn.innerHTML = '<i class="fas fa-pause"></i>';
        } else {
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    });

    // Previous 0.1 second
    prevBtn.addEventListener('click', function() {
        wavesurfer.skip(-0.1);
    });

    // Next 0.1 second
    nextBtn.addEventListener('click', function() {
        wavesurfer.skip(0.1);
    });

    // Set playback speed
    playbackSpeedSelect.addEventListener('change', function() {
        wavesurfer.setPlaybackRate(parseFloat(this.value));
    });

    // Update time cursor position based on playback time
    wavesurfer.on('timeupdate', function(time) {
        currentPlayTime = time;
        updateCursorPosition(time);
    });

    // Update cursor position based on audio time
    function updateCursorPosition(time) {
        const spectrogramContainer = document.getElementById('spectrogram-img');
        if (!spectrogramContainer) return;
        
        const containerWidth = spectrogramContainer.offsetWidth;
        const relativePosition = time / wavesurfer.getDuration();
        const position = relativePosition * containerWidth;
        
        timeCursor.style.left = `${position}px`;
    }

    // Handle window resize to update cursor position
    window.addEventListener('resize', function() {
        updateCursorPosition(currentPlayTime);
    });

    // File selection in the queue
    const fileItems = document.querySelectorAll('.file-item');
    fileItems.forEach(item => {
        item.addEventListener('click', function() {
            fileItems.forEach(file => file.classList.remove('active'));
            this.classList.add('active');
            
            // Here would be the code to load the selected file
            // For demo purposes, we're just changing the image source
            const fileName = this.querySelector('.file-name').textContent;
            document.getElementById('spectrogram-img').src = `https://placehold.co/800x300/1a1c23/ffffff?text=${encodeURIComponent(fileName)}`;
            
            // Reset annotation state when new file is loaded
            resetAnnotations();
        });
    });

    // Reset annotations
    function resetAnnotations() {
        annotorious.clearAnnotations();
        notesTextarea.value = '';
        confidenceSlider.value = 90;
        confidenceValue.textContent = '90';
        labelButtons[0].classList.add('active'); // Select normal as default
        labelButtons.forEach((btn, index) => {
            if (index !== 0) btn.classList.remove('active');
        });
        currentLabel = 'normal';
    }

    // Reset button functionality
    resetBtn.addEventListener('click', resetAnnotations);

    // Save button functionality
    saveBtn.addEventListener('click', function() {
        // Get annotations
        const annotations = annotorious.getAnnotations();
        
        // Prepare the labeling data
        const labelingData = {
            audio_file_id: currentAudioFileId,
            label: currentLabel,
            confidence: parseInt(confidenceSlider.value),
            notes: notesTextarea.value,
            metadata: {
                regions: [],
                boxes: annotations.map(annotation => {
                    // Convert annotation to required format
                    const bounds = annotation.shapes[0].value;
                    return {
                        type: 'box',
                        time: {
                            start: currentPlayTime,  // This would need to be calculated from coordinates
                            end: currentPlayTime + 0.5  // Example time range
                        },
                        freq: {
                            min: 100,  // This would need to be calculated from coordinates
                            max: 1000  // Example frequency range
                        },
                        label: currentLabel
                    };
                }),
                ui_state: {
                    zoom: 1.0,
                    playbackRate: parseFloat(playbackSpeedSelect.value)
                }
            }
        };

        // In a real implementation, this would send the data to the backend
        console.log('Saving labeling data:', labelingData);
        
        // Show confirmation
        alert('라벨링 데이터가 저장되었습니다!');
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Space to play/pause
        if (e.code === 'Space') {
            e.preventDefault();
            wavesurfer.playPause();
            isPlaying = wavesurfer.isPlaying();
            
            if (isPlaying) {
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            } else {
                playBtn.innerHTML = '<i class="fas fa-play"></i>';
            }
        }
        
        // Arrow keys for navigation
        else if (e.code === 'ArrowLeft') {
            if (e.shiftKey) {
                // 1 second jump backward
                wavesurfer.skip(-1);
            } else {
                // 0.1 second jump backward
                wavesurfer.skip(-0.1);
            }
        }
        
        else if (e.code === 'ArrowRight') {
            if (e.shiftKey) {
                // 1 second jump forward
                wavesurfer.skip(1);
            } else {
                // 0.1 second jump forward
                wavesurfer.skip(0.1);
            }
        }
        
        // Number keys for label selection
        else if (e.code === 'Digit1') {
            labelButtons.forEach(btn => btn.classList.remove('active'));
            labelButtons[0].classList.add('active');
            currentLabel = 'normal';
        }
        
        else if (e.code === 'Digit2') {
            labelButtons.forEach(btn => btn.classList.remove('active'));
            labelButtons[1].classList.add('active');
            currentLabel = 'warning';
        }
        
        else if (e.code === 'Digit3') {
            labelButtons.forEach(btn => btn.classList.remove('active'));
            labelButtons[2].classList.add('active');
            currentLabel = 'critical';
        }
        
        else if (e.code === 'Digit4') {
            labelButtons.forEach(btn => btn.classList.remove('active'));
            labelButtons[3].classList.add('active');
            currentLabel = 'unknown';
        }
        
        // 'L' key for loop
        else if (e.code === 'KeyL') {
            // Toggle loop functionality
            console.log('Loop toggle functionality would be implemented here');
        }
    });

    // Auto-save functionality (with debounce)
    let autoSaveTimeout;
    function scheduleAutoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            console.log('Auto-saving current labeling state...');
            
            // Save to localStorage
            const currentState = {
                label: currentLabel,
                confidence: confidenceSlider.value,
                notes: notesTextarea.value,
                annotations: annotorious.getAnnotations()
            };
            
            localStorage.setItem('audioLabelingState', JSON.stringify(currentState));
        }, 3000); // Save after 3 seconds of inactivity
    }

    // Trigger auto-save when certain actions occur
    annotorious.on('createAnnotation', scheduleAutoSave);
    annotorious.on('updateAnnotation', scheduleAutoSave);
    annotorious.on('deleteAnnotation', scheduleAutoSave);
    
    confidenceSlider.addEventListener('change', scheduleAutoSave);
    notesTextarea.addEventListener('input', scheduleAutoSave);

    // Load any previously saved state
    function loadSavedState() {
        const savedState = localStorage.getItem('audioLabelingState');
        if (savedState) {
            try {
                const state = JSON.parse(savedState);
                
                // Restore UI state
                if (state.label) {
                    labelButtons.forEach(btn => {
                        btn.classList.remove('active');
                        if (btn.dataset.label === state.label) {
                            btn.classList.add('active');
                            currentLabel = state.label;
                        }
                    });
                }
                
                if (state.confidence) {
                    confidenceSlider.value = state.confidence;
                    confidenceValue.textContent = state.confidence;
                }
                
                if (state.notes) {
                    notesTextarea.value = state.notes;
                }
                
                // Note: Annotations will not be restored automatically from localStorage
                // because they are tied to the specific image, which may have changed
            } catch (e) {
                console.error('Error loading saved state:', e);
            }
        }
    }

    // Load saved state when ready
    setTimeout(loadSavedState, 1000);

    // Region functionality for loop
    let region = null;
    loopBtn.addEventListener('click', function() {
        if (region) {
            // Remove existing region
            region.remove();
            region = null;
            loopBtn.innerHTML = '<i class="fas fa-repeat"></i>';
        } else {
            // Create a new region
            const currentTime = wavesurfer.getCurrentTime();
            const duration = wavesurfer.getDuration();
            
            // Create region for a 2-second window starting from current time
            const startTime = currentTime;
            const endTime = Math.min(currentTime + 2, duration);
            
            region = wavesurfer.addRegion({
                start: startTime,
                end: endTime,
                color: 'rgba(255, 0, 0, 0.2)',
                drag: true,
                resize: true
            });
            
            // On region playback end, loop back to start
            region.on('out', () => {
                wavesurfer.seekTo(region.start / duration);
            });
            
            loopBtn.innerHTML = '<i class="fas fa-stop"></i>';
        }
    });
});
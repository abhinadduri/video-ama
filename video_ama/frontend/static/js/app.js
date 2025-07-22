// Video AMA Frontend JavaScript

class VideoAMA {
    constructor() {
        this.videoPath = '';
        this.isVideoProcessed = false;
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.elements = {
            videoFileInput: document.getElementById('videoFile'),
            uploadBtn: document.getElementById('uploadBtn'),
            fileInfo: document.getElementById('fileInfo'),
            videoContainer: document.getElementById('videoContainer'),
            videoPlayer: document.getElementById('videoPlayer'),
            videoStatus: document.getElementById('videoStatus'),
            chatMessages: document.getElementById('chatMessages'),
            questionInput: document.getElementById('questionInput'),
            askBtn: document.getElementById('askBtn'),
            loadingOverlay: document.getElementById('loadingOverlay')
        };
    }

    attachEventListeners() {
        this.elements.uploadBtn.addEventListener('click', () => this.processVideo());
        this.elements.askBtn.addEventListener('click', () => this.askQuestion());
        
        this.elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.elements.askBtn.disabled) {
                this.askQuestion();
            }
        });

        this.elements.videoFileInput.addEventListener('change', (e) => {
            this.handleFileSelection();
        });
    }

    handleFileSelection() {
        const file = this.elements.videoFileInput.files[0];
        
        if (file) {
            // Show file info
            const fileSize = (file.size / (1024 * 1024)).toFixed(1);
            this.elements.fileInfo.textContent = `Selected: ${file.name} (${fileSize} MB)`;
            this.elements.uploadBtn.disabled = false;
            this.selectedFile = file;
        } else {
            this.elements.fileInfo.textContent = '';
            this.elements.uploadBtn.disabled = true;
            this.selectedFile = null;
        }
    }

    async processVideo() {
        if (!this.selectedFile) {
            this.showError('Please select a video file');
            return;
        }

        this.showLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('video_file', this.selectedFile);

            const response = await fetch('/api/upload-video', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.status === 'success') {
                this.isVideoProcessed = true;
                this.setupVideoPlayer();
                this.enableChat();
                this.addSystemMessage(`Video processed successfully! Found ${result.transcript_length} segments.`);
            } else {
                throw new Error(result.message || 'Failed to process video');
            }

        } catch (error) {
            console.error('Error processing video:', error);
            this.showError(`Failed to process video: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    setupVideoPlayer() {
        // Set up the video player with the processed video
        this.elements.videoPlayer.src = '/api/video';
        this.elements.videoContainer.style.display = 'flex';
        this.elements.videoStatus.textContent = 'Video ready - Ask questions below!';
    }

    enableChat() {
        this.elements.questionInput.disabled = false;
        this.elements.askBtn.disabled = false;
        this.elements.questionInput.placeholder = 'Ask a question about the video...';
        this.elements.questionInput.focus();
    }

    async askQuestion() {
        const question = this.elements.questionInput.value.trim();
        
        if (!question) {
            return;
        }

        if (!this.isVideoProcessed) {
            this.showError('Please process a video first');
            return;
        }

        // Add user message to chat
        this.addUserMessage(question);
        this.elements.questionInput.value = '';
        this.elements.askBtn.disabled = true;

        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.addAssistantMessage(result.answer, result.timestamps);

        } catch (error) {
            console.error('Error asking question:', error);
            this.addAssistantMessage(`Sorry, I encountered an error: ${error.message}`);
        } finally {
            this.elements.askBtn.disabled = false;
            this.elements.questionInput.focus();
        }
    }

    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `<p><strong>You:</strong> ${this.escapeHtml(message)}</p>`;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addAssistantMessage(message, timestamps = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        let content = `<p><strong>Assistant:</strong> ${this.escapeHtml(message)}</p>`;
        
        if (timestamps && timestamps.length > 0) {
            content += '<div class="timestamps">';
            timestamps.forEach(timestamp => {
                const timeStr = this.formatTimestamp(timestamp.start);
                content += `<button class="timestamp-link" onclick="videoAMA.seekToTime(${timestamp.start})">${timeStr}</button>`;
            });
            content += '</div>';
        }
        
        messageDiv.innerHTML = content;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.innerHTML = `<p>${this.escapeHtml(message)}</p>`;
        this.elements.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    seekToTime(seconds) {
        if (this.elements.videoPlayer) {
            this.elements.videoPlayer.currentTime = seconds;
            this.elements.videoPlayer.play();
        }
    }

    formatTimestamp(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    showLoading(show) {
        this.elements.loadingOverlay.style.display = show ? 'flex' : 'none';
        this.elements.uploadBtn.disabled = show;
    }

    showError(message) {
        this.addSystemMessage(`Error: ${message}`);
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application
const videoAMA = new VideoAMA();
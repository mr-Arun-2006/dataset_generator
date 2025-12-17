// ============================================
// TRADING DATASET GENERATOR - JAVASCRIPT
// API Integration & UI Logic
// ============================================

const API_BASE_URL = 'http://localhost:5000/api';

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeFormHandlers();
    initializeUploadArea();
    checkAPIHealth();
    loadDatasets();

    // Auto-refresh datasets every 30 seconds when on datasets tab
    setInterval(() => {
        const datasetsTab = document.getElementById('datasets');
        if (datasetsTab.classList.contains('active')) {
            loadDatasets();
        }
    }, 30000);
});

// ============================================
// TAB NAVIGATION
// ============================================

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;

            // Update buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Update content
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            document.getElementById(targetTab).classList.add('active');

            // Load data for specific tabs
            if (targetTab === 'datasets') {
                loadDatasets();
            }
        });
    });
}

// ============================================
// FORM HANDLERS
// ============================================

function initializeFormHandlers() {
    const datasetSize = document.getElementById('datasetSize');
    const balanceCategories = document.getElementById('balanceCategories');
    const pineWeight = document.getElementById('pineWeight');
    const priceWeight = document.getElementById('priceWeight');
    const generateBtn = document.getElementById('generateBtn');

    // Update stats when size changes
    datasetSize.addEventListener('input', updateStats);

    // Toggle weight controls
    balanceCategories.addEventListener('change', (e) => {
        const weightControls = document.getElementById('weightControls');
        weightControls.style.display = e.target.checked ? 'none' : 'block';
        updateStats();
    });

    // Update weight values
    pineWeight.addEventListener('input', (e) => {
        document.getElementById('pineWeightValue').textContent = e.target.value + '%';
        updateStats();
    });

    priceWeight.addEventListener('input', (e) => {
        document.getElementById('priceWeightValue').textContent = e.target.value + '%';
        updateStats();
    });

    // Generate button
    generateBtn.addEventListener('click', generateDataset);

    // Initial stats update
    updateStats();
}

function updateStats() {
    const size = parseInt(document.getElementById('datasetSize').value);
    const balanced = document.getElementById('balanceCategories').checked;

    let pineWeight, priceWeight, instWeight;

    if (balanced) {
        pineWeight = priceWeight = instWeight = 33.33;
    } else {
        pineWeight = parseInt(document.getElementById('pineWeight').value);
        priceWeight = parseInt(document.getElementById('priceWeight').value);
        instWeight = 100 - pineWeight - priceWeight;
        document.getElementById('instWeightValue').textContent = instWeight + '%';
    }

    document.getElementById('totalSamples').textContent = size;
    document.getElementById('pineSamples').textContent = Math.floor(size * pineWeight / 100);
    document.getElementById('priceSamples').textContent = Math.floor(size * priceWeight / 100);
    document.getElementById('instSamples').textContent = Math.floor(size * instWeight / 100);
}

// ============================================
// API HEALTH CHECK
// ============================================

async function checkAPIHealth() {
    const statusIndicator = document.getElementById('apiStatus');
    const statusText = statusIndicator.querySelector('.status-text');

    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            throw new Error('API unhealthy');
        }
    } catch (error) {
        statusIndicator.classList.add('error');
        statusText.textContent = 'Disconnected';
        showToast('Cannot connect to API. Make sure the backend is running.', 'error');
    }
}

// ============================================
// GENERATE DATASET
// ============================================

async function generateDataset() {
    const generateBtn = document.getElementById('generateBtn');
    const progressCard = document.getElementById('progressCard');
    const resultCard = document.getElementById('resultCard');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    // Get configuration
    const config = {
        size: parseInt(document.getElementById('datasetSize').value),
        seed: parseInt(document.getElementById('seedValue').value),
        balance: document.getElementById('balanceCategories').checked,
        filename: document.getElementById('filename').value
    };

    if (!config.balance) {
        config.pine_weight = parseInt(document.getElementById('pineWeight').value);
        config.price_weight = parseInt(document.getElementById('priceWeight').value);
        config.inst_weight = 100 - config.pine_weight - config.price_weight;
    }

    // Show progress
    generateBtn.disabled = true;
    progressCard.style.display = 'block';
    resultCard.style.display = 'none';
    progressFill.style.width = '0%';
    progressText.textContent = 'Generating dataset...';

    // Simulate progress (since we don't have real-time updates)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
        }
    }, 200);

    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        clearInterval(progressInterval);

        if (data.success) {
            // Complete progress
            progressFill.style.width = '100%';
            progressText.textContent = 'Complete!';

            setTimeout(() => {
                progressCard.style.display = 'none';
                resultCard.style.display = 'block';

                // Show results
                const resultDetails = document.getElementById('resultDetails');
                resultDetails.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <strong>Filename:</strong> ${data.filename}
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Samples Generated:</strong> ${data.samples_generated}
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Distribution:</strong><br>
                        • PineScript: ${data.distribution.pinescript}<br>
                        • Price Action: ${data.distribution.price_action}<br>
                        • Institutional: ${data.distribution.institutional}
                    </div>
                    <div>
                        <strong>Seed Used:</strong> ${data.seed_used}
                    </div>
                `;

                showToast('Dataset generated successfully!', 'success');
                loadDatasets(); // Refresh datasets list
            }, 500);
        } else {
            throw new Error(data.error || 'Generation failed');
        }
    } catch (error) {
        clearInterval(progressInterval);
        progressCard.style.display = 'none';
        showToast('Error generating dataset: ' + error.message, 'error');
    } finally {
        generateBtn.disabled = false;
    }
}

// ============================================
// PREVIEW SAMPLES
// ============================================

async function previewSample(category) {
    const previewId = `preview${category.charAt(0).toUpperCase() + category.slice(1).replace('_', '')}`;
    const previewElement = document.getElementById(previewId);

    previewElement.innerHTML = '<div style="text-align: center; padding: 2rem; color: #718096;">Loading...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/preview/${category}`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        let html = `
            <div class="preview-label">Instruction</div>
            <div class="preview-code">${escapeHtml(data.instruction)}</div>
            
            <div class="preview-label">Response</div>
            <div class="preview-code">${escapeHtml(data.response)}</div>
            
            <div class="preview-label">Metadata</div>
            <div class="preview-code">
Pattern Type: ${data.pattern_type}
${data.timeframe ? 'Timeframe: ' + data.timeframe : ''}
${data.metadata ? '\n' + JSON.stringify(data.metadata, null, 2) : ''}
            </div>
        `;

        previewElement.innerHTML = html;
    } catch (error) {
        previewElement.innerHTML = `<div style="color: #f56565; padding: 1rem;">Error: ${error.message}</div>`;
    }
}

async function previewOHLC() {
    const previewElement = document.getElementById('previewOHLC');

    previewElement.innerHTML = '<div style="text-align: center; padding: 2rem; color: #718096;">Loading...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/preview/ohlc?pattern=breakout&num_bars=10`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        let html = `
            <div class="preview-label">Pattern: ${data.pattern}</div>
            <div class="preview-code">`;

        data.bars.forEach((bar, i) => {
            html += `Bar ${i + 1}: O=${bar.open.toFixed(2)} H=${bar.high.toFixed(2)} L=${bar.low.toFixed(2)} C=${bar.close.toFixed(2)} V=${bar.volume}\n`;
        });

        html += `</div>`;

        previewElement.innerHTML = html;
    } catch (error) {
        previewElement.innerHTML = `<div style="color: #f56565; padding: 1rem;">Error: ${error.message}</div>`;
    }
}

// ============================================
// DATASETS LIST
// ============================================

async function loadDatasets() {
    const datasetsList = document.getElementById('datasetsList');

    datasetsList.innerHTML = '<div class="loading-state">Loading datasets...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/datasets`);
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        if (data.datasets.length === 0) {
            datasetsList.innerHTML = '<div class="empty-state">No datasets found. Generate one to get started!</div>';
            return;
        }

        let html = '';
        data.datasets.forEach(dataset => {
            const createdDate = new Date(dataset.created).toLocaleString();

            html += `
                <div class="dataset-item">
                    <div class="dataset-info">
                        <h4>${dataset.name}</h4>
                        <div class="dataset-meta">
                            <span>📊 ${dataset.samples} samples</span>
                            <span>💾 ${dataset.size_mb} MB</span>
                            <span>📅 ${createdDate}</span>
                        </div>
                    </div>
                    <div class="dataset-actions">
                        <button class="btn btn-secondary" onclick="downloadDataset('${dataset.name}')">
                            <span class="btn-icon">⬇️</span>
                            Download
                        </button>
                    </div>
                </div>
            `;
        });

        datasetsList.innerHTML = html;
    } catch (error) {
        datasetsList.innerHTML = `<div class="empty-state" style="color: #f56565;">Error loading datasets: ${error.message}</div>`;
    }
}

function downloadDataset(filename) {
    window.open(`${API_BASE_URL}/datasets/${filename}`, '_blank');
    showToast('Downloading ' + filename, 'info');
}

// ============================================
// FILE UPLOAD & VALIDATION
// ============================================

function initializeUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

async function handleFileUpload(file) {
    if (!file.name.endsWith('.jsonl')) {
        showToast('Please upload a .jsonl file', 'error');
        return;
    }

    const validationResult = document.getElementById('validationResult');
    validationResult.style.display = 'block';
    validationResult.className = 'validation-result';
    validationResult.innerHTML = '<div style="text-align: center; padding: 2rem;">Validating...</div>';

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/validate`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        if (data.valid) {
            validationResult.classList.add('success');
            validationResult.innerHTML = `
                <div class="validation-summary">✓ Validation Successful</div>
                <div>All ${data.valid_count} samples are valid!</div>
            `;
            showToast('Dataset is valid!', 'success');
        } else {
            validationResult.classList.add('error');

            let errorHtml = `
                <div class="validation-summary">✗ Validation Failed</div>
                <div style="margin-bottom: 1rem;">
                    Valid: ${data.valid_count} | Errors: ${data.error_count}
                </div>
            `;

            if (data.errors.length > 0) {
                errorHtml += '<div class="error-list">';
                data.errors.forEach(err => {
                    errorHtml += `<div class="error-item">Line ${err.line}: ${escapeHtml(err.error)}</div>`;
                });
                errorHtml += '</div>';
            }

            validationResult.innerHTML = errorHtml;
            showToast('Dataset validation failed', 'error');
        }
    } catch (error) {
        validationResult.classList.add('error');
        validationResult.innerHTML = `
            <div class="validation-summary">✗ Error</div>
            <div>${escapeHtml(error.message)}</div>
        `;
        showToast('Validation error: ' + error.message, 'error');
    }
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

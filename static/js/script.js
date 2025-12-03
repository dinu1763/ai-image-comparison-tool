// Global variables
let currentResult = null;
let currentImagePaths = {
    image1: null,
    image2: null
};
let currentInputMode = 'upload'; // 'upload' or 'viewport'
let urlPairCount = 1; // Track number of URL pairs

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupImageUpload(1);
    setupImageUpload(2);
    setupFormSubmit();
    setupModeButtons();
    setupThemeToggle();
});

// Setup mode toggle buttons
function setupModeButtons() {
    const uploadBtn = document.getElementById('uploadModeBtn');
    const viewportBtn = document.getElementById('viewportModeBtn');

    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            switchInputMode('upload');
        });
    }

    if (viewportBtn) {
        viewportBtn.addEventListener('click', function() {
            switchInputMode('viewport');
        });
    }
}

// Switch between upload and viewport input modes
function switchInputMode(mode) {
    currentInputMode = mode;

    const uploadMode = document.getElementById('uploadMode');
    const viewportMode = document.getElementById('viewportMode');
    const uploadBtn = document.querySelector('.toggle-btn[data-mode="upload"]');
    const viewportBtn = document.querySelector('.toggle-btn[data-mode="viewport"]');

    // Hide all modes
    uploadMode.style.display = 'none';
    viewportMode.style.display = 'none';

    // Remove active class from all buttons
    uploadBtn.classList.remove('active');
    viewportBtn.classList.remove('active');

    if (mode === 'upload') {
        uploadMode.style.display = 'grid';
        uploadBtn.classList.add('active');

        // Clear viewport inputs - reset to single pair
        const container = document.getElementById('urlPairsContainer');
        container.innerHTML = `
            <div class="url-pair-wrapper" data-pair-index="0">
                <div class="url-pair-header">
                    <span class="pair-number">Comparison #1</span>
                    <button type="button" class="remove-pair-btn" onclick="removeUrlPair(0)" style="display: none;">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
                <div class="viewport-url-inputs">
                    <div class="viewport-url-group">
                        <label>
                            <i class="fas fa-globe"></i> Website 1 URL
                        </label>
                        <input type="url" class="url-input viewport-url-1" placeholder="https://example.com" required>
                    </div>

                    <div class="vs-divider">
                        <span>VS</span>
                    </div>

                    <div class="viewport-url-group">
                        <label>
                            <i class="fas fa-globe"></i> Website 2 URL
                        </label>
                        <input type="url" class="url-input viewport-url-2" placeholder="https://example.org" required>
                    </div>
                </div>
            </div>
        `;
        urlPairCount = 1;
    } else if (mode === 'viewport') {
        viewportMode.style.display = 'block';
        viewportBtn.classList.add('active');

        // Clear upload inputs
        removeImage(1);
        removeImage(2);
    }

    // Clear previous results
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

// Setup image upload for drag and drop
function setupImageUpload(imageNumber) {
    const uploadArea = document.getElementById(`uploadArea${imageNumber}`);
    const fileInput = document.getElementById(`image${imageNumber}`);
    const preview = document.getElementById(`preview${imageNumber}`);
    const previewImg = document.getElementById(`previewImg${imageNumber}`);

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0], imageNumber, false); // false = don't update file input
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#764ba2';
        uploadArea.style.background = '#f0f2ff';
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#f8f9ff';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#f8f9ff';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0], imageNumber, true); // true = update file input for drag-drop
        }
    });
}

// Handle file selection
function handleFileSelect(file, imageNumber, updateFileInput = true) {
    if (!file) return;

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (PNG, JPG, GIF, BMP, WEBP)');
        return;
    }

    // Validate file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }

    // Update file input only for drag-and-drop (not for normal file input selection)
    if (updateFileInput) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        document.getElementById(`image${imageNumber}`).files = dataTransfer.files;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById(`previewImg${imageNumber}`).src = e.target.result;
        document.getElementById(`uploadArea${imageNumber}`).style.display = 'none';
        document.getElementById(`preview${imageNumber}`).style.display = 'block';
    };
    reader.readAsDataURL(file);
}

// Remove image
function removeImage(imageNumber) {
    document.getElementById(`image${imageNumber}`).value = '';
    document.getElementById(`uploadArea${imageNumber}`).style.display = 'block';
    document.getElementById(`preview${imageNumber}`).style.display = 'none';
    document.getElementById(`previewImg${imageNumber}`).src = '';
}

// Setup form submission
function setupFormSubmit() {
    const form = document.getElementById('comparisonForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate inputs based on mode
        if (currentInputMode === 'upload') {
            const image1 = document.getElementById('image1').files[0];
            const image2 = document.getElementById('image2').files[0];

            if (!image1 || !image2) {
                alert('Please select both images');
                return;
            }
        } else if (currentInputMode === 'viewport') {
            // Validate URL pairs
            const urlPairs = collectUrlPairs();
            
            if (urlPairs.length === 0) {
                alert('Please enter at least one pair of website URLs for viewport comparison');
                return;
            }
            
            // Check if any pair has empty URLs
            const pairWrappers = document.querySelectorAll('.url-pair-wrapper');
            let hasEmptyUrls = false;
            
            pairWrappers.forEach((wrapper, index) => {
                const url1 = wrapper.querySelector('.viewport-url-1').value.trim();
                const url2 = wrapper.querySelector('.viewport-url-2').value.trim();
                
                if (url1 || url2) { // If either field has content
                    if (!url1 || !url2) { // But not both
                        hasEmptyUrls = true;
                        alert(`Please enter both URLs for Comparison #${index + 1}`);
                    }
                }
            });
            
            if (hasEmptyUrls) {
                return;
            }
        }

        // Hide previous results/errors
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';

        // Show loading with appropriate message
        const loadingDiv = document.getElementById('loading');
        const loadingText = loadingDiv.querySelector('p');

        if (currentInputMode === 'viewport') {
            loadingText.textContent = 'Performing viewport-by-viewport comparison... This may take 2-5 minutes depending on page length.';
        } else {
            loadingText.textContent = 'Analyzing images...';
        }

        loadingDiv.style.display = 'block';
        document.getElementById('compareBtn').disabled = true;

        // Handle viewport comparison separately
        if (currentInputMode === 'viewport') {
            await handleViewportComparison(form);
            return;
        }

        // Prepare form data for regular comparison
        const formData = new FormData(form);

        // Add input mode to form data
        formData.append('input_mode', currentInputMode);

        try {
            // Send request
            const response = await fetch('/compare', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            // Hide loading
            document.getElementById('loading').style.display = 'none';
            document.getElementById('compareBtn').disabled = false;

            if (result.success) {
                // Show results
                displayResults(result);
            } else {
                // Show error
                displayError(result.error);
            }

        } catch (error) {
            // Hide loading
            document.getElementById('loading').style.display = 'none';
            document.getElementById('compareBtn').disabled = false;

            // Show error
            displayError('An error occurred while processing your request. Please try again.');
            console.error('Error:', error);
        }
    });
}

// Display results
function displayResults(result) {
    currentResult = result;

    // Store image paths for PDF generation
    currentImagePaths.image1 = result.image1;
    currentImagePaths.image2 = result.image2;

    // Set analysis text
    document.getElementById('analysisText').textContent = result.analysis;

    // Set metadata
    document.getElementById('modelUsed').textContent = result.model_used;
    document.getElementById('tokensUsed').textContent = result.tokens_used.total;
    document.getElementById('comparisonTypeUsed').textContent =
        result.comparison_type.charAt(0).toUpperCase() + result.comparison_type.slice(1);

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Display error
function displayError(errorMessage) {
    document.getElementById('errorMessage').textContent = errorMessage;
    document.getElementById('errorSection').style.display = 'block';
    
    // Scroll to error
    document.getElementById('errorSection').scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
    });
}

// Download results as PDF
async function downloadPDF() {
    if (!currentResult) {
        alert('No results to download');
        return;
    }

    try {
        // Show loading state
        const pdfButton = event.target.closest('.download-btn');
        const originalText = pdfButton.innerHTML;
        pdfButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
        pdfButton.disabled = true;

        // Prepare data for PDF generation
        const pdfData = {
            result: currentResult,
            image1_path: currentImagePaths.image1,
            image2_path: currentImagePaths.image2
        };

        // Send request to generate PDF
        const response = await fetch('/download-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pdfData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate PDF');
        }

        // Get the PDF blob
        const blob = await response.blob();

        // Create download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `image_comparison_report_${new Date().getTime()}.pdf`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(url);

        // Restore button state
        pdfButton.innerHTML = originalText;
        pdfButton.disabled = false;

    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Failed to generate PDF: ' + error.message);

        // Restore button state
        const pdfButton = event.target.closest('.download-btn');
        pdfButton.innerHTML = '<i class="fas fa-file-pdf"></i> Download PDF Report';
        pdfButton.disabled = false;
    }
}

// Handle viewport comparison
async function handleViewportComparison(form) {
    try {
        // Collect all URL pairs
        const urlPairs = collectUrlPairs();
        
        if (urlPairs.length === 0) {
            alert('Please enter at least one pair of URLs for comparison');
            document.getElementById('loading').style.display = 'none';
            document.getElementById('compareBtn').disabled = false;
            return;
        }

        // Get common settings
        const viewportSize = document.getElementById('viewportComparisonSize').value;
        const waitTime = 3; // Default wait time
        const comparisonType = document.getElementById('viewportComparisonType').value;
        const model = document.getElementById('model').value;

        const loadingDiv = document.getElementById('loading');
        const loadingText = loadingDiv.querySelector('p');

        // Process each URL pair sequentially
        const results = [];
        for (let i = 0; i < urlPairs.length; i++) {
            const pair = urlPairs[i];
            
            // Update loading message
            loadingText.textContent = `Processing comparison ${i + 1} of ${urlPairs.length}: ${pair.website1_url} vs ${pair.website2_url}`;

            // Prepare form data
            const formData = new FormData();
            formData.append('website1_url', pair.website1_url);
            formData.append('website2_url', pair.website2_url);
            formData.append('viewport_size', viewportSize);
            formData.append('wait_time', waitTime);
            formData.append('comparison_type', comparisonType);
            formData.append('model', model);

            try {
                // Send request to viewport comparison endpoint
                const response = await fetch('/compare-viewports', {
                    method: 'POST',
                    body: formData
                });

                console.log(`Comparison ${i + 1} response status:`, response.status);

                const result = await response.json();
                console.log(`Comparison ${i + 1} response data:`, result);

                if (result.success) {
                    results.push({
                        success: true,
                        pairIndex: i + 1,
                        url1: pair.website1_url,
                        url2: pair.website2_url,
                        data: result
                    });
                } else {
                    results.push({
                        success: false,
                        pairIndex: i + 1,
                        url1: pair.website1_url,
                        url2: pair.website2_url,
                        error: result.error
                    });
                }
            } catch (error) {
                console.error(`Error in comparison ${i + 1}:`, error);
                results.push({
                    success: false,
                    pairIndex: i + 1,
                    url1: pair.website1_url,
                    url2: pair.website2_url,
                    error: error.message
                });
            }
        }

        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('compareBtn').disabled = false;

        // Display batch results
        displayBatchViewportResults(results);

    } catch (error) {
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('compareBtn').disabled = false;

        // Show error
        const errorMsg = `An error occurred during viewport comparison: ${error.message}. Check console for details.`;
        showError(errorMsg);
        console.error('Error in handleViewportComparison:', error);
        console.error('Error stack:', error.stack);
    }
}

// Helper function to show error (renamed to avoid conflict with variable name)
function showError(message) {
    displayError(message);
}

// Display viewport comparison results
function displayViewportResults(result) {
    try {
        console.log('Displaying viewport results:', result);

        const resultsSection = document.getElementById('resultsSection');
        const analysisDiv = document.getElementById('analysisResult');
        const analysisText = document.getElementById('analysisText');

        if (!resultsSection || !analysisDiv) {
            console.error('Required DOM elements not found');
            console.error('resultsSection:', resultsSection);
            console.error('analysisDiv:', analysisDiv);
            throw new Error('Required DOM elements not found');
        }

        // Clear the regular analysis text (used for image comparison)
        if (analysisText) {
            analysisText.innerHTML = '';
        }

        // Create viewport results HTML
        const summary = result.summary;

        if (!summary) {
            console.error('Summary not found in result');
            throw new Error('Summary not found in result');
        }

        // Extract domain names from URLs
        let domain1, domain2;
        try {
            domain1 = new URL(summary.url1).hostname;
            domain2 = new URL(summary.url2).hostname;
        } catch (e) {
            console.error('Error parsing URLs:', e);
            domain1 = summary.url1 || 'Website 1';
            domain2 = summary.url2 || 'Website 2';
        }

        let html = `
            <div class="viewport-results">
                <h2><i class="fas fa-layer-group"></i> Viewport Comparison Complete</h2>

                <div class="viewport-summary">
                    <h3>Summary</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <span class="summary-label">Website 1:</span>
                            <span class="summary-value">${domain1}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Website 2:</span>
                            <span class="summary-value">${domain2}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Viewport Size:</span>
                            <span class="summary-value">${summary.viewport_size} (${summary.viewport_dimensions.width}x${summary.viewport_dimensions.height})</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Total Viewports:</span>
                            <span class="summary-value">${summary.total_viewports}</span>
                        </div>
        `;

        html += `
                        <div class="summary-item">
                            <span class="summary-label">Differences Detected:</span>
                            <span class="summary-value">${summary.total_differences}</span>
                        </div>
        `;

        if (summary.average_ssim !== null && summary.average_ssim !== undefined) {
            const similarityPct = (summary.average_ssim * 100).toFixed(2);
            html += `
                        <div class="summary-item">
                            <span class="summary-label">Average Similarity:</span>
                            <span class="summary-value">${similarityPct}%</span>
                        </div>
            `;
        }

        html += `
                    </div>
                </div>

                <div class="viewport-download">
                    <p><i class="fas fa-file-pdf"></i> A comprehensive PDF report has been generated with all viewport comparisons.</p>
                    <a href="/download-viewport-report/${result.pdf_filename}" class="download-btn" download>
                        <i class="fas fa-download"></i> Download Full Report
                    </a>
                </div>

                <div class="viewport-message">
                    <i class="fas fa-check-circle"></i>
                    <p>${result.message}</p>
                </div>
            </div>
        `;

        analysisDiv.innerHTML = html;
        resultsSection.style.display = 'block';

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        console.log('Viewport results displayed successfully');

    } catch (error) {
        console.error('Error in displayViewportResults:', error);
        console.error('Error stack:', error.stack);
        console.error('Result object:', result);

        // Re-throw to be caught by caller
        throw new Error(`Failed to display viewport results: ${error.message}`);
    }
}

// Display batch viewport comparison results
function displayBatchViewportResults(results) {
    try {
        console.log('Displaying batch viewport results:', results);

        const resultsSection = document.getElementById('resultsSection');
        const analysisDiv = document.getElementById('analysisResult');
        const analysisText = document.getElementById('analysisText');

        if (!resultsSection || !analysisDiv) {
            console.error('Required DOM elements not found');
            throw new Error('Required DOM elements not found');
        }

        // Clear previous content
        if (analysisText) {
            analysisText.innerHTML = '';
        }
        analysisDiv.innerHTML = '';

        // Create batch results summary
        const successCount = results.filter(r => r.success).length;
        const failCount = results.length - successCount;

        let batchHtml = `
            <div class="viewport-results">
                <h2><i class="fas fa-layer-group"></i> Batch Viewport Comparison Results</h2>
                
                <div class="viewport-summary">
                    <h3>Batch Summary</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <span class="summary-label">Total Comparisons</span>
                            <span class="summary-value">${results.length}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Successful</span>
                            <span class="summary-value" style="color: #4ade80;">${successCount}</span>
                        </div>
                        <div class="summary-item">
                            <span class="summary-label">Failed</span>
                            <span class="summary-value" style="color: #f87171;">${failCount}</span>
                        </div>
                    </div>
                </div>
        `;

        // Display each comparison result
        results.forEach((result, index) => {
            if (result.success) {
                const summary = result.data.summary;
                const domain1 = extractDomain(result.url1);
                const domain2 = extractDomain(result.url2);

                batchHtml += `
                    <div class="viewport-comparison-result">
                        <div class="comparison-header">
                            <h3>
                                <i class="fas fa-check-circle" style="color: #4ade80;"></i>
                                Comparison #${result.pairIndex}: ${domain1} vs ${domain2}
                            </h3>
                            <button class="download-btn" onclick="downloadViewportPDF('${summary.pdf_filename}')">
                                <i class="fas fa-file-pdf"></i> Download PDF Report
                            </button>
                        </div>
                        
                        <div class="viewport-summary">
                            <div class="summary-grid">
                                <div class="summary-item">
                                    <span class="summary-label">Total Viewports</span>
                                    <span class="summary-value">${summary.total_viewports}</span>
                                </div>
                                <div class="summary-item">
                                    <span class="summary-label">Differences Found</span>
                                    <span class="summary-value">${summary.total_differences}</span>
                                </div>
                                ${summary.average_ssim ? `
                                <div class="summary-item">
                                    <span class="summary-label">Average Similarity</span>
                                    <span class="summary-value">${(summary.average_ssim * 100).toFixed(2)}%</span>
                                </div>
                                ` : ''}
                                <div class="summary-item">
                                    <span class="summary-label">Viewport Size</span>
                                    <span class="summary-value">${summary.viewport_size}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                batchHtml += `
                    <div class="viewport-comparison-result error">
                        <div class="comparison-header">
                            <h3>
                                <i class="fas fa-exclamation-circle" style="color: #f87171;"></i>
                                Comparison #${result.pairIndex}: ${extractDomain(result.url1)} vs ${extractDomain(result.url2)}
                            </h3>
                        </div>
                        <div class="error-content">
                            <p><strong>Error:</strong> ${result.error}</p>
                        </div>
                    </div>
                `;
            }
        });

        batchHtml += '</div>';
        analysisDiv.innerHTML = batchHtml;

        // Show results section
        resultsSection.style.display = 'block';

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        console.log('Batch viewport results displayed successfully');

    } catch (error) {
        console.error('Error in displayBatchViewportResults:', error);
        throw new Error(`Failed to display batch viewport results: ${error.message}`);
    }
}

function extractDomain(url) {
    try {
        const urlObj = new URL(url);
        return urlObj.hostname;
    } catch (e) {
        return url;
    }
}

// ============================================
// Theme Toggle Functionality
// ============================================

function setupThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // Load saved theme from localStorage or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);

    // Toggle theme on button click
    themeToggle.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const currentTheme = body.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);

        // Add animation effect
        themeToggle.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            themeToggle.style.transform = 'rotate(0deg)';
        }, 300);
    });
}

function setTheme(theme) {
    const body = document.body;

    // Set theme attribute
    body.setAttribute('data-theme', theme);

    // Save to localStorage
    localStorage.setItem('theme', theme);

    // Log theme change
    console.log(`Theme changed to: ${theme}`);
}

// ============================================
// URL Pair Management for Batch Comparison
// ============================================

function addUrlPair() {
    const container = document.getElementById('urlPairsContainer');
    const existingPairs = document.querySelectorAll('.url-pair-wrapper');
    const newIndex = existingPairs.length; // Use current count as index

    const pairHtml = `
        <div class="url-pair-wrapper" data-pair-index="${newIndex}">
            <div class="url-pair-header">
                <span class="pair-number">Comparison #${newIndex + 1}</span>
                <button type="button" class="remove-pair-btn" onclick="removeUrlPair(${newIndex})">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
            <div class="viewport-url-inputs">
                <div class="viewport-url-group">
                    <label>
                        <i class="fas fa-globe"></i> Website 1 URL
                    </label>
                    <input type="url" class="url-input viewport-url-1" placeholder="https://example.com" required>
                </div>

                <div class="vs-divider">
                    <span>VS</span>
                </div>

                <div class="viewport-url-group">
                    <label>
                        <i class="fas fa-globe"></i> Website 2 URL
                    </label>
                    <input type="url" class="url-input viewport-url-2" placeholder="https://example.org" required>
                </div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', pairHtml);
    updateRemoveButtons();
}

function removeUrlPair(index) {
    const pairWrapper = document.querySelector(`.url-pair-wrapper[data-pair-index="${index}"]`);
    if (pairWrapper) {
        pairWrapper.remove();
        updatePairIndices();
        updateRemoveButtons();
    }
}

function updatePairIndices() {
    const pairs = document.querySelectorAll('.url-pair-wrapper');
    pairs.forEach((pair, index) => {
        // Update data attribute
        pair.setAttribute('data-pair-index', index);
        
        // Update display number
        const numberSpan = pair.querySelector('.pair-number');
        if (numberSpan) {
            numberSpan.textContent = `Comparison #${index + 1}`;
        }
        
        // Update remove button onclick
        const removeBtn = pair.querySelector('.remove-pair-btn');
        if (removeBtn) {
            removeBtn.setAttribute('onclick', `removeUrlPair(${index})`);
        }
    });
}

function updatePairNumbers() {
    // Kept for backward compatibility, calls the new function
    updatePairIndices();
}

function updateRemoveButtons() {
    const pairs = document.querySelectorAll('.url-pair-wrapper');
    const removeButtons = document.querySelectorAll('.remove-pair-btn');
    
    // Show remove buttons only if there's more than one pair
    removeButtons.forEach(btn => {
        btn.style.display = pairs.length > 1 ? 'flex' : 'none';
    });
}

function collectUrlPairs() {
    const pairs = [];
    const pairWrappers = document.querySelectorAll('.url-pair-wrapper');
    
    pairWrappers.forEach((wrapper, index) => {
        const url1 = wrapper.querySelector('.viewport-url-1').value.trim();
        const url2 = wrapper.querySelector('.viewport-url-2').value.trim();
        
        if (url1 && url2) {
            pairs.push({
                website1_url: url1,
                website2_url: url2,
                index: index
            });
        }
    });
    
    return pairs;
}

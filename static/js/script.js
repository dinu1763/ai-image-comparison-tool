// Global variables
let currentResult = null;
let currentImagePaths = {
    image1: null,
    image2: null
};
let currentInputMode = 'upload'; // 'upload' or 'screenshot'

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupImageUpload(1);
    setupImageUpload(2);
    setupFormSubmit();
});

// Switch between upload and screenshot input modes
function switchInputMode(mode) {
    currentInputMode = mode;

    const uploadMode = document.getElementById('uploadMode');
    const screenshotMode = document.getElementById('screenshotMode');
    const uploadBtn = document.querySelector('.toggle-btn[data-mode="upload"]');
    const screenshotBtn = document.querySelector('.toggle-btn[data-mode="screenshot"]');

    // Hide all modes
    uploadMode.style.display = 'none';
    screenshotMode.style.display = 'none';

    // Remove active class from all buttons
    uploadBtn.classList.remove('active');
    screenshotBtn.classList.remove('active');

    if (mode === 'upload') {
        uploadMode.style.display = 'grid';
        uploadBtn.classList.add('active');

        // Clear screenshot inputs
        document.getElementById('website1Url').value = '';
        document.getElementById('website2Url').value = '';
    } else if (mode === 'screenshot') {
        screenshotMode.style.display = 'block';
        screenshotBtn.classList.add('active');

        // Clear upload inputs
        removeImage(1);
        removeImage(2);
    }
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
        handleFileSelect(e.target.files[0], imageNumber);
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
            handleFileSelect(files[0], imageNumber);
        }
    });
}

// Handle file selection
function handleFileSelect(file, imageNumber) {
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

    // Update file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    document.getElementById(`image${imageNumber}`).files = dataTransfer.files;

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
        } else if (currentInputMode === 'screenshot') {
            const website1 = document.getElementById('website1Url').value.trim();
            const website2 = document.getElementById('website2Url').value.trim();

            if (!website1 || !website2) {
                alert('Please enter both website URLs');
                return;
            }
        }

        // Hide previous results/errors
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('errorSection').style.display = 'none';

        // Show loading with appropriate message
        const loadingDiv = document.getElementById('loading');
        const loadingText = loadingDiv.querySelector('p');

        if (currentInputMode === 'screenshot') {
            loadingText.textContent = 'Capturing website screenshots and analyzing... This may take 30-60 seconds.';
        } else {
            loadingText.textContent = 'Analyzing images...';
        }

        loadingDiv.style.display = 'block';
        document.getElementById('compareBtn').disabled = true;

        // Prepare form data
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


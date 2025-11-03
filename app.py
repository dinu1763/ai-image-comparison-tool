"""
Flask Web Application for Image Comparison Tool
"""

import os
import json
import io
import requests
import mimetypes
import re
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from image_comparison_tool import ImageComparisonTool
# from screenshot_tool import WebsiteScreenshotTool  # Screenshot feature removed
from viewport_comparison_tool import ViewportComparisonTool
from viewport_report_generator import ViewportReportGenerator
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the comparison tool
# API key will be loaded from environment variable
try:
    comparison_tool = ImageComparisonTool()
except ValueError as e:
    print(f"Warning: {e}")
    comparison_tool = None


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/compare', methods=['POST'])
def compare_images():
    """Handle image comparison request - supports both file uploads and URLs"""

    # Check if comparison tool is initialized
    if comparison_tool is None:
        return jsonify({
            'success': False,
            'error': 'API key not configured. Please set GEMINI_API_KEY environment variable.'
        }), 500

    try:
        # Handle file upload mode only (screenshot mode removed)
        input_mode = request.form.get('input_mode', 'upload')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        filepath1 = None
        filepath2 = None

        # Screenshot mode has been removed - only upload mode is supported
        # if input_mode == 'screenshot':
        #     [Screenshot handling code removed]

        # Handle file upload mode
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both images are required'
            }), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        # Check if files are selected
        if image1.filename == '' or image2.filename == '':
            return jsonify({
                'success': False,
                'error': 'Please select both images'
            }), 400

        # Validate file types
        if not (allowed_file(image1.filename) and allowed_file(image2.filename)):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, BMP, WEBP'
            }), 400

        # Save uploaded files
        filename1 = secure_filename(f"{timestamp}_1_{image1.filename}")
        filename2 = secure_filename(f"{timestamp}_2_{image2.filename}")

        filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
        filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], filename2)

        image1.save(filepath1)
        image2.save(filepath2)

        # Get comparison parameters
        comparison_type = request.form.get('comparison_type', 'general')
        custom_prompt = request.form.get('custom_prompt', '')
        model = request.form.get('model', 'gemini-2.5-flash')

        # Perform comparison
        result = comparison_tool.compare_images(
            image1_path=filepath1,
            image2_path=filepath2,
            comparison_type=comparison_type,
            custom_prompt=custom_prompt if custom_prompt else None,
            model=model
        )

        # Add image paths to result for PDF generation
        result['image1'] = filepath1
        result['image2'] = filepath2

        # Clean up uploaded files (optional - comment out if you want to keep them)
        # os.remove(filepath1)
        # os.remove(filepath2)

        return jsonify(result)

    except Exception as e:
        # Clean up files if they were created
        if filepath1 and os.path.exists(filepath1):
            os.remove(filepath1)
        if filepath2 and os.path.exists(filepath2):
            os.remove(filepath2)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/models', methods=['GET'])
def get_models():
    """Get available models"""
    models = [
        {'value': 'gemini-2.5-flash', 'name': 'Gemini 2.5 Flash (Fast & Efficient)'},
        {'value': 'gemini-2.5-pro', 'name': 'Gemini 2.5 Pro (Most Capable)'},
        {'value': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash'},
    ]
    return jsonify(models)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    api_configured = comparison_tool is not None
    return jsonify({
        'status': 'healthy',
        'api_configured': api_configured
    })


@app.route('/compare-viewports', methods=['POST'])
def compare_viewports():
    """Handle viewport-by-viewport website comparison request"""

    # Check if comparison tool is initialized
    if comparison_tool is None:
        return jsonify({
            'success': False,
            'error': 'API key not configured. Please set GEMINI_API_KEY environment variable.'
        }), 500

    try:
        # Get request parameters
        website1_url = request.form.get('website1_url', '').strip()
        website2_url = request.form.get('website2_url', '').strip()

        if not website1_url or not website2_url:
            return jsonify({
                'success': False,
                'error': 'Both website URLs are required'
            }), 400

        # Get comparison settings
        viewport_size = request.form.get('viewport_size', 'desktop')
        wait_time = int(request.form.get('wait_time', '3'))
        comparison_type = request.form.get('comparison_type', 'differences')
        model = request.form.get('model', 'gemini-2.5-flash')

        # Validate parameters
        if viewport_size not in ['desktop', 'tablet', 'mobile']:
            viewport_size = 'desktop'

        if wait_time < 0 or wait_time > 10:
            wait_time = 3

        print(f"Starting viewport comparison:")
        print(f"  URL 1: {website1_url}")
        print(f"  URL 2: {website2_url}")
        print(f"  Viewport: {viewport_size}")
        print(f"  Model: {model}")

        # Create viewport comparison tool
        viewport_tool = ViewportComparisonTool(comparison_tool=comparison_tool)

        # Perform comparison
        result = viewport_tool.compare_websites_by_viewport(
            url1=website1_url,
            url2=website2_url,
            viewport_size=viewport_size,
            wait_time=wait_time,
            comparison_type=comparison_type,
            model=model
        )

        if not result.get('success'):
            return jsonify(result), 500

        # Generate PDF report
        report_generator = ViewportReportGenerator()

        # Generate filename
        filename = report_generator.generate_report_filename(website1_url, website2_url)
        output_path = os.path.join(UPLOAD_FOLDER, filename)

        # Generate report
        pdf_success = report_generator.generate_report(result, output_path)

        if not pdf_success:
            # Clean up temp files
            for temp_file in result.get('temp_files', []):
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

            return jsonify({
                'success': False,
                'error': 'Failed to generate PDF report'
            }), 500

        # Prepare response with summary
        summary = result['summary']
        summary['pdf_filename'] = filename
        summary['pdf_path'] = output_path

        # Clean up temp files
        for temp_file in result.get('temp_files', []):
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

        # Create appropriate message based on whether sections are used
        if 'total_sections' in summary:
            message = f'Comparison complete! {summary["total_viewports"]} viewports analyzed ({summary["total_sections"]} sections total).'
        else:
            message = f'Comparison complete! {summary["total_viewports"]} viewports analyzed.'

        return jsonify({
            'success': True,
            'summary': summary,
            'pdf_filename': filename,
            'message': message
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download-viewport-report/<filename>', methods=['GET'])
def download_viewport_report(filename):
    """Download viewport comparison PDF report"""
    try:
        # Secure the filename
        filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': 'Report file not found'
            }), 404

        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF report"""
    try:
        data = request.get_json()

        if not data or 'result' not in data:
            return jsonify({
                'success': False,
                'error': 'No comparison data provided'
            }), 400

        result = data['result']
        image1_path = data.get('image1_path')
        image2_path = data.get('image2_path')

        # Create PDF in memory
        pdf_buffer = io.BytesIO()

        # Generate PDF
        generate_pdf_report(pdf_buffer, result, image1_path, image2_path)

        # Reset buffer position
        pdf_buffer.seek(0)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'image_comparison_report_{timestamp}.pdf'

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def detect_image_differences(image1_path, image2_path, threshold=30):
    """
    Detect visual differences between two images using multiple algorithms.

    Args:
        image1_path: Path to first image
        image2_path: Path to second image
        threshold: Sensitivity threshold for difference detection (0-100, lower = more sensitive)

    Returns:
        List of difference regions as (x, y, w, h) tuples, or None if detection fails
    """
    try:
        # Load images
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        if img1 is None or img2 is None:
            return None

        # Resize images to same dimensions if different
        if img1.shape != img2.shape:
            # Use the smaller dimensions to avoid upscaling
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            img1 = cv2.resize(img1, (width, height))
            img2 = cv2.resize(img2, (width, height))

        # Convert to grayscale for SSIM
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Compute SSIM
        score, diff = ssim(gray1, gray2, full=True)
        diff = (diff * 255).astype("uint8")

        # Threshold the difference image
        thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY_INV)[1]

        # Find contours of differences
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter and collect significant difference regions
        difference_regions = []
        min_area = 100  # Minimum area to consider as a difference

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                difference_regions.append((x, y, w, h))

        # Merge nearby regions
        merged_regions = merge_nearby_regions(difference_regions, distance_threshold=50)

        return merged_regions if merged_regions else None

    except Exception as e:
        print(f"Error detecting differences: {e}")
        return None


def merge_nearby_regions(regions, distance_threshold=50):
    """
    Merge nearby bounding boxes to reduce clutter.

    Args:
        regions: List of (x, y, w, h) tuples
        distance_threshold: Maximum distance between regions to merge

    Returns:
        List of merged regions
    """
    if not regions:
        return []

    merged = []
    used = set()

    for i, (x1, y1, w1, h1) in enumerate(regions):
        if i in used:
            continue

        # Start with current region
        min_x, min_y = x1, y1
        max_x, max_y = x1 + w1, y1 + h1
        used.add(i)

        # Check for nearby regions to merge
        for j, (x2, y2, w2, h2) in enumerate(regions):
            if j in used:
                continue

            # Calculate distance between regions
            center1_x, center1_y = x1 + w1/2, y1 + h1/2
            center2_x, center2_y = x2 + w2/2, y2 + h2/2
            distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

            if distance < distance_threshold:
                # Merge regions
                min_x = min(min_x, x2)
                min_y = min(min_y, y2)
                max_x = max(max_x, x2 + w2)
                max_y = max(max_y, y2 + h2)
                used.add(j)

        merged.append((min_x, min_y, max_x - min_x, max_y - min_y))

    return merged


def annotate_image_with_differences(image_path, difference_regions, output_format='PNG'):
    """
    Create an annotated version of an image with highlighted difference regions.

    Args:
        image_path: Path to the image to annotate
        difference_regions: List of (x, y, w, h) tuples indicating difference areas
        output_format: Output image format (default: PNG)

    Returns:
        PIL Image object with annotations, or None if annotation fails
    """
    try:
        # Load image
        img = Image.open(image_path)

        # Create a copy for annotation
        annotated = img.copy()

        if not difference_regions:
            return annotated

        # Create drawing context
        draw = ImageDraw.Draw(annotated, 'RGBA')

        # Define highlight colors (semi-transparent red)
        box_color = (255, 0, 0, 100)  # Red with transparency
        border_color = (255, 0, 0, 255)  # Solid red border

        # Draw rectangles around difference regions
        for (x, y, w, h) in difference_regions:
            # Draw filled rectangle with transparency
            draw.rectangle([x, y, x + w, y + h], fill=box_color, outline=border_color, width=3)

        return annotated

    except Exception as e:
        print(f"Error annotating image: {e}")
        return None


def parse_analysis_to_table_data(analysis_text, comparison_type):
    """
    Parse AI analysis text into structured table data.

    Args:
        analysis_text: The AI-generated analysis text
        comparison_type: Type of comparison performed

    Returns:
        List of table rows [header_row, data_rows...]
    """
    table_data = []

    # Split text into lines
    lines = analysis_text.split('\n')

    # Track current section and content
    current_section = None
    current_content = []
    sections = {}

    # Parse the text to extract sections
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this is a numbered section header (e.g., "1. Overall Similarities", "#### 1. Overall")
        section_match = re.match(r'^(?:#{1,4}\s*)?(\d+)\.\s*\*?\*?(.+?)(?:\*\*)?:?\s*$', line)
        if section_match:
            # Save previous section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)

            # Start new section
            current_section = section_match.group(2).strip('*').strip()
            current_content = []
        elif current_section:
            # Add content to current section
            # Skip markdown headers and separators
            if not line.startswith('#') and not line.startswith('---') and not line.startswith('==='):
                current_content.append(line)

    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)

    # If no sections found, try alternative parsing for bullet points
    if not sections:
        current_key = "Analysis"
        current_items = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('---') or line.startswith('==='):
                continue

            # Check for bold headers (e.g., "**Similarities:**")
            bold_match = re.match(r'\*\*(.+?):\*\*', line)
            if bold_match:
                if current_items:
                    sections[current_key] = '\n'.join(current_items)
                current_key = bold_match.group(1)
                current_items = []
            else:
                current_items.append(line)

        if current_items:
            sections[current_key] = '\n'.join(current_items)

    # Create table based on comparison type
    if comparison_type == "responsive":
        # For responsive comparisons, create a detailed table
        table_data.append(['Aspect', 'Analysis'])
        for section_name, content in sections.items():
            # Clean up content
            clean_content = content.replace('*', '').strip()
            if clean_content:
                table_data.append([section_name, clean_content])

    elif comparison_type in ["differences", "similarities"]:
        # For differences/similarities, create a focused table
        table_data.append(['Category', 'Details'])
        for section_name, content in sections.items():
            clean_content = content.replace('*', '').strip()
            if clean_content:
                table_data.append([section_name, clean_content])

    else:
        # For general and detailed comparisons
        table_data.append(['Comparison Aspect', 'Findings'])
        for section_name, content in sections.items():
            clean_content = content.replace('*', '').strip()
            if clean_content:
                table_data.append([section_name, clean_content])

    # If no structured data was found, create a simple single-row table
    if len(table_data) <= 1:
        table_data = [['Analysis Results', analysis_text.replace('*', '').strip()]]

    return table_data


def generate_pdf_report(buffer, result, image1_path=None, image2_path=None):
    """
    Generate a professional PDF report for image comparison

    Args:
        buffer: BytesIO buffer to write PDF to
        result: Comparison result dictionary
        image1_path: Path to first image (optional)
        image2_path: Path to second image (optional)
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Container for PDF elements
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        alignment=TA_LEFT
    )

    # Title
    title = Paragraph("Image Comparison Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))

    # Timestamp
    timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    timestamp_text = Paragraph(f"<i>Generated on {timestamp}</i>", styles['Normal'])
    elements.append(timestamp_text)
    elements.append(Spacer(1, 0.3*inch))

    # Metadata Table
    metadata_heading = Paragraph("Comparison Details", heading_style)
    elements.append(metadata_heading)

    metadata_data = [
        ['Comparison Type:', result.get('comparison_type', 'N/A').title()],
        ['AI Model:', result.get('model_used', 'N/A')],
        ['Tokens Used:', str(result.get('tokens_used', {}).get('total', 'N/A'))],
        ['Status:', 'Success' if result.get('success') else 'Failed']
    ]

    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3*inch))

    # Images Section (if paths provided)
    if image1_path and image2_path and os.path.exists(image1_path) and os.path.exists(image2_path):
        try:
            # Determine if we should detect differences
            comparison_type = result.get('comparison_type', 'general')
            should_detect_differences = comparison_type in ['differences', 'detailed']

            # Detect differences if applicable
            difference_regions = None
            if should_detect_differences:
                difference_regions = detect_image_differences(image1_path, image2_path)

            # --- ORIGINAL IMAGES SECTION ---
            original_heading = Paragraph("Original Images", heading_style)
            elements.append(original_heading)
            elements.append(Spacer(1, 0.1*inch))

            # Load original images
            img1_orig = Image.open(image1_path)
            img2_orig = Image.open(image2_path)

            # Enhanced dimensions for better quality (increased from 2.8x2.5 to 3.5x3.5)
            max_width = 3.5 * inch
            max_height = 3.5 * inch

            # Calculate actual dimensions maintaining aspect ratio
            def calculate_dimensions(img, max_w, max_h):
                """Calculate dimensions maintaining aspect ratio"""
                aspect = img.width / img.height
                if aspect > 1:  # Wider than tall
                    width = min(max_w, img.width / 72)  # Convert pixels to inches (72 DPI)
                    height = width / aspect
                    if height > max_h:
                        height = max_h
                        width = height * aspect
                else:  # Taller than wide
                    height = min(max_h, img.height / 72)
                    width = height * aspect
                    if width > max_w:
                        width = max_w
                        height = width / aspect
                return width, height

            # Resize images maintaining aspect ratio with high quality
            img1_copy = img1_orig.copy()
            img2_copy = img2_orig.copy()

            # Use higher resolution for better quality (3x instead of 2x)
            img1_copy.thumbnail((int(max_width * 3), int(max_height * 3)), Image.Resampling.LANCZOS)
            img2_copy.thumbnail((int(max_width * 3), int(max_height * 3)), Image.Resampling.LANCZOS)

            # Add white border for better visual separation
            def add_border(img, border_size=10, border_color='white'):
                """Add a border around the image"""
                bordered = Image.new('RGB',
                                    (img.width + 2*border_size, img.height + 2*border_size),
                                    border_color)
                bordered.paste(img, (border_size, border_size))
                return bordered

            img1_bordered = add_border(img1_copy)
            img2_bordered = add_border(img2_copy)

            # Save to temporary buffers with high quality
            img1_buffer = io.BytesIO()
            img2_buffer = io.BytesIO()
            img1_bordered.save(img1_buffer, format='PNG', optimize=False, quality=95)
            img2_bordered.save(img2_buffer, format='PNG', optimize=False, quality=95)
            img1_buffer.seek(0)
            img2_buffer.seek(0)

            # Calculate display dimensions
            w1, h1 = calculate_dimensions(img1_bordered, max_width, max_height)
            w2, h2 = calculate_dimensions(img2_bordered, max_width, max_height)

            # Create ReportLab images with calculated dimensions
            rl_img1 = RLImage(img1_buffer, width=w1, height=h1)
            rl_img2 = RLImage(img2_buffer, width=w2, height=h2)

            # Create table with images side by side
            image_table = Table([[rl_img1, rl_img2]], colWidths=[3.7*inch, 3.7*inch])
            image_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9ff')),
            ]))

            elements.append(image_table)

            # Image labels
            labels_data = [['Image 1', 'Image 2']]
            labels_table = Table(labels_data, colWidths=[3.7*inch, 3.7*inch])
            labels_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))

            elements.append(labels_table)
            elements.append(Spacer(1, 0.4*inch))

            # --- ANNOTATED IMAGES SECTION (if differences detected) ---
            if difference_regions:
                annotated_heading = Paragraph("Differences Highlighted", heading_style)
                elements.append(annotated_heading)
                elements.append(Spacer(1, 0.1*inch))

                # Create annotated versions
                img1_annotated = annotate_image_with_differences(image1_path, difference_regions)
                img2_annotated = annotate_image_with_differences(image2_path, difference_regions)

                if img1_annotated and img2_annotated:
                    # Resize annotated images
                    img1_ann_copy = img1_annotated.copy()
                    img2_ann_copy = img2_annotated.copy()

                    img1_ann_copy.thumbnail((int(max_width * 3), int(max_height * 3)), Image.Resampling.LANCZOS)
                    img2_ann_copy.thumbnail((int(max_width * 3), int(max_height * 3)), Image.Resampling.LANCZOS)

                    # Add borders
                    img1_ann_bordered = add_border(img1_ann_copy)
                    img2_ann_bordered = add_border(img2_ann_copy)

                    # Save to buffers
                    img1_ann_buffer = io.BytesIO()
                    img2_ann_buffer = io.BytesIO()
                    img1_ann_bordered.save(img1_ann_buffer, format='PNG', optimize=False, quality=95)
                    img2_ann_bordered.save(img2_ann_buffer, format='PNG', optimize=False, quality=95)
                    img1_ann_buffer.seek(0)
                    img2_ann_buffer.seek(0)

                    # Calculate dimensions
                    w1_ann, h1_ann = calculate_dimensions(img1_ann_bordered, max_width, max_height)
                    w2_ann, h2_ann = calculate_dimensions(img2_ann_bordered, max_width, max_height)

                    # Create ReportLab images
                    rl_img1_ann = RLImage(img1_ann_buffer, width=w1_ann, height=h1_ann)
                    rl_img2_ann = RLImage(img2_ann_buffer, width=w2_ann, height=h2_ann)

                    # Create table
                    ann_image_table = Table([[rl_img1_ann, rl_img2_ann]], colWidths=[3.7*inch, 3.7*inch])
                    ann_image_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 5),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff5f5')),  # Light red tint
                    ]))

                    elements.append(ann_image_table)

                    # Labels
                    ann_labels_data = [['Image 1 (Annotated)', 'Image 2 (Annotated)']]
                    ann_labels_table = Table(ann_labels_data, colWidths=[3.7*inch, 3.7*inch])
                    ann_labels_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 5),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#d32f2f')),  # Red text
                    ]))

                    elements.append(ann_labels_table)

                    # Add note about differences
                    diff_count = len(difference_regions)
                    diff_note = Paragraph(
                        f"<i>Found {diff_count} difference region{'s' if diff_count != 1 else ''} highlighted in red.</i>",
                        styles['Normal']
                    )
                    elements.append(Spacer(1, 0.1*inch))
                    elements.append(diff_note)

            elements.append(Spacer(1, 0.3*inch))

        except Exception as e:
            error_text = Paragraph(f"<i>Could not load images: {str(e)}</i>", styles['Normal'])
            elements.append(error_text)
            elements.append(Spacer(1, 0.2*inch))

    # Analysis Section
    analysis_heading = Paragraph("AI Analysis", heading_style)
    elements.append(analysis_heading)
    elements.append(Spacer(1, 0.1*inch))

    # Format analysis text as table
    analysis_text = result.get('analysis', 'No analysis available')
    comparison_type = result.get('comparison_type', 'general')

    # Parse analysis into table data
    table_data = parse_analysis_to_table_data(analysis_text, comparison_type)

    # Create custom style for table cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['BodyText'],
        fontSize=9,
        leading=12,
        spaceAfter=6,
        alignment=TA_LEFT
    )

    # Convert table data to Paragraphs for better text wrapping
    formatted_table_data = []
    for i, row in enumerate(table_data):
        formatted_row = []
        for j, cell in enumerate(row):
            # Escape special characters
            cell_escaped = str(cell).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Use bold for headers
            if i == 0:
                cell_para = Paragraph(f"<b>{cell_escaped}</b>", cell_style)
            else:
                cell_para = Paragraph(cell_escaped, cell_style)
            formatted_row.append(cell_para)
        formatted_table_data.append(formatted_row)

    # Calculate column widths based on number of columns
    num_cols = len(table_data[0]) if table_data else 2
    if num_cols == 2:
        col_widths = [2*inch, 4.5*inch]
    else:
        available_width = 6.5*inch
        col_widths = [available_width / num_cols] * num_cols

    # Create analysis table with professional styling
    analysis_table = Table(formatted_table_data, colWidths=col_widths, repeatRows=1)

    # Define alternating row colors for better readability
    table_style_commands = [
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        # Data rows styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),

        # Borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#667eea')),

        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]

    # Add alternating row colors for data rows
    for i in range(1, len(formatted_table_data)):
        if i % 2 == 0:
            table_style_commands.append(
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9ff'))
            )
        else:
            table_style_commands.append(
                ('BACKGROUND', (0, i), (-1, i), colors.white)
            )

    analysis_table.setStyle(TableStyle(table_style_commands))
    elements.append(analysis_table)
    elements.append(Spacer(1, 0.3*inch))

    # Token Usage Details
    if 'tokens_used' in result:
        tokens_heading = Paragraph("Token Usage Details", heading_style)
        elements.append(tokens_heading)

        tokens = result['tokens_used']
        tokens_data = [
            ['Prompt Tokens:', str(tokens.get('prompt', 'N/A'))],
            ['Completion Tokens:', str(tokens.get('completion', 'N/A'))],
            ['Total Tokens:', str(tokens.get('total', 'N/A'))]
        ]

        tokens_table = Table(tokens_data, colWidths=[2*inch, 4*inch])
        tokens_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(tokens_table)

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = Paragraph(
        "<i>Generated by Image Comparison Tool - Powered by Google Gemini AI</i>",
        styles['Normal']
    )
    elements.append(footer_text)

    # Build PDF
    doc.build(elements)

    return buffer


if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("\n" + "="*80)
        print("WARNING: GEMINI_API_KEY environment variable is not set!")
        print("Please set it before using the application:")
        print("  Windows: set GEMINI_API_KEY=your-api-key-here")
        print("  Linux/Mac: export GEMINI_API_KEY=your-api-key-here")
        print("="*80 + "\n")
    
    print("\n" + "="*80)
    print("Image Comparison Tool - Web UI")
    print("="*80)
    print("Starting server at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


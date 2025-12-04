# Adobe Visual QA Tool

A comprehensive AI-powered quality assurance tool for comparing Adobe stage and production environments. Uses Google Gemini Vision API to perform detailed visual analysis, detect differences, and generate professional PDF reports. Perfect for QA teams validating website deployments and updates.

## Features

### 🔍 Batch Viewport Comparison
- **Multiple URL Pairs**: Add unlimited URL pairs for sequential comparison
- **Dynamic Management**: Easily add/remove comparison pairs with intuitive UI
- **Automated Processing**: Processes each pair one by one with progress updates
- **Individual Reports**: Generates separate PDF reports for each comparison

### 📊 Comprehensive Analysis
- **Viewport-by-Viewport**: Compare websites viewport-by-viewport from top to bottom
- **AI-Powered Insights**: Detailed bullet-point analysis of visual differences
- **Visual Highlights**: Automatically highlights difference regions in red
- **SSIM Scores**: Structural Similarity Index metrics for each viewport
- **Full-Page Coverage**: Captures and analyzes entire page length

### 📄 Professional PDF Reports
- **Large, Clear Images**: Full-width screenshots displayed vertically for maximum visibility
- **Detailed Analysis**: AI-generated bullet points explaining each difference
- **Organized Layout**: Clean, professional report structure
- **Custom Naming**: PDF filenames based on actual URLs for easy identification
- **Summary Statistics**: Overall comparison metrics and findings

### 🎯 Smart Features
- **Modal Detection**: Automatically detects and closes promotional popups
- **Viewport Sizes**: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
- **Comparison Types**: Differences, similarities, general, or detailed analysis
- **Sequential Processing**: Handles multiple comparisons without manual intervention

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
```bash
# On Windows
set GEMINI_API_KEY=your-api-key-here

# On Linux/Mac
export GEMINI_API_KEY=your-api-key-here
```

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Start the web application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Quick Start

### Web Interface

1. **Access the Tool**: Open `http://localhost:5000` in your browser

2. **Switch to Viewport Mode**: Click the "Viewport Comparison" button

3. **Add URL Pairs**:
   - Enter first URL pair (e.g., production vs stage)
   - Click "+ Add Another URL Pair" to add more comparisons
   - Remove any pair using the "Remove" button

4. **Configure Settings**:
   - Select viewport size (Desktop/Tablet/Mobile)
   - Choose analysis type (Find Differences recommended)
   - Select AI model (Gemini 2.5 Flash for speed)

5. **Start Comparison**: Click "Compare Images"

6. **Download Reports**: Each comparison generates a downloadable PDF report

### URL Naming Format

**For Production vs Stage Comparisons:**
```
Website 1 URL: https://www.adobe.com/products/photoshop.html
Website 2 URL: https://stage.adobe.com/products/photoshop.html

PDF Filename: adobe_com_products_photoshop_html_20251204.pdf
```

The tool automatically:
- Removes "www." prefix
- Converts the path to underscore format
- Adds today's date
- Uses the first URL for naming

## Comparison Types

### 1. Find Differences (`differences`) ⭐ Recommended
Focuses specifically on identifying all visual differences between environments.
- Ideal for QA validation
- Highlights layout changes
- Detects missing elements
- Color and styling differences

### 2. Find Similarities (`similarities`)
Highlights common elements and shared characteristics.
- Verifies consistent branding
- Checks preserved functionality
- Confirms unchanged sections

### 3. General Comparison (`general`)
Provides a comprehensive overview of both sites.
- Overall design assessment
- High-level differences and similarities
- Composition analysis

### 4. Detailed Analysis (`detailed`)
Extremely thorough analysis with technical details.
- Pixel-level differences
- Color palette analysis
- Element positioning
- Recommendations

## PDF Report Features

### Large, Clear Screenshots
- **7-inch width** images for maximum visibility
- **Vertical layout** - one screenshot after another
- **Full-width display** utilizing entire page
- **High resolution** for detailed inspection

### Detailed Analysis Sections
Each viewport comparison includes:
- **Screenshot labels** matching URL format (e.g., `adobe_com_products`)
- **Visual difference highlights** with red overlay boxes
- **AI-generated bullet points** explaining each difference
- **SSIM scores** showing similarity percentage
- **Viewport position** and scroll information

### Smart Formatting
- **URL display**: Full URLs shown in report header
- **Filename convention**: `domain_path_date.pdf`
- **Organized structure**: Summary page followed by viewport comparisons
- **Metadata**: Timestamps, viewport dimensions, model used

## Modal Popup Handling

The tool automatically handles promotional popups:

1. **Detection**: Checks for modals with `id="modal-hash"` after page load
2. **3-Second Wait**: Allows time for delayed modals to appear
3. **Auto-Close**: Attempts to close using:
   - Close button click (`.dialog-close`)
   - ESC key press (fallback)
4. **Silent Continue**: Proceeds if no modal found

**Supported Popups:**
- Adobe Creative Cloud promotions
- Black Friday/Cyber Monday offers
- Other delayed modal dialogs

## Use Cases

### 1. Pre-Production Validation
Compare stage and production before deployment:
```
URL 1: https://www.adobe.com/products/photoshop.html
URL 2: https://stage.adobe.com/products/photoshop.html
```

### 2. A/B Testing
Compare different versions or experiments:
```
URL 1: https://www.adobe.com/variant-a
URL 2: https://www.adobe.com/variant-b
```

### 3. Responsive Design QA
Test across different viewport sizes:
- Desktop: Full layout validation
- Tablet: Mid-size breakpoint checks
- Mobile: Touch-optimized interface

### 4. Batch QA Workflows
Add multiple pages for comprehensive testing:
- Homepage comparison
- Product page validation
- Checkout flow testing
- Footer/header consistency

### 5. Cross-Environment Testing
Compare different deployment environments:
- Development vs Stage
- Stage vs Production
- Production vs Backup

## Python API Usage

### Basic Viewport Comparison
```python
from image_comparison_tool import ImageComparisonTool
from viewport_comparison_tool import ViewportComparisonTool
from viewport_report_generator import ViewportReportGenerator

# Initialize
comparison_tool = ImageComparisonTool()
viewport_tool = ViewportComparisonTool(comparison_tool=comparison_tool)

# Perform comparison
result = viewport_tool.compare_websites_by_viewport(
    url1="https://www.adobe.com/products",
    url2="https://stage.adobe.com/products",
    viewport_size='desktop',
    wait_time=3,
    comparison_type='differences',
    model='gemini-2.5-flash'
)

# Generate PDF report
if result['success']:
    report_gen = ViewportReportGenerator()
    filename = report_gen.generate_report_filename(
        result['summary']['url1'],
        result['summary']['url2']
    )
    report_gen.generate_report(result, f'uploads/{filename}')
    print(f"Report saved: {filename}")
```

### Custom Image Comparison
```python
from image_comparison_tool import ImageComparisonTool

tool = ImageComparisonTool()

result = tool.compare_images(
    image1_path="screenshot1.png",
    image2_path="screenshot2.png",
    comparison_type="differences",
    model="gemini-2.5-flash"
)

if result["success"]:
    print(result["analysis"])
```

## Supported Viewport Sizes

| Size | Dimensions | Use Case |
|------|-----------|----------|
| Desktop | 1920×1080 | Standard desktop layouts |
| Tablet | 768×1024 | iPad and tablet devices |
| Mobile | 375×667 | iPhone and mobile phones |

## AI Models Available

| Model | Speed | Quality | Use Case |
|-------|-------|---------|----------|
| Gemini 2.5 Flash | ⚡ Fast | ⭐⭐⭐ Good | Default, recommended |
| Gemini 2.5 Pro | 🐢 Slower | ⭐⭐⭐⭐⭐ Best | Maximum accuracy |
| Gemini 2.0 Flash | ⚡⚡ Fastest | ⭐⭐ Basic | Quick checks |

## Technical Details

### Architecture
- **Backend**: Python Flask web server
- **Browser Automation**: Selenium with Chrome WebDriver
- **AI Analysis**: Google Gemini Vision API
- **PDF Generation**: ReportLab library
- **Image Processing**: Pillow, OpenCV, scikit-image

### Image Comparison
- **SSIM Calculation**: Structural Similarity Index
- **Difference Detection**: Contour-based region detection
- **Threshold**: Configurable sensitivity (default: 30)
- **Minimum Area**: 100px² for difference regions

### Report Generation
- **Page Size**: US Letter (8.5" × 11")
- **Margins**: 0.75 inches all sides
- **Image Width**: 7.0 inches (nearly full page)
- **Image Height**: Up to 9.0 inches per screenshot
- **Font**: Helvetica family

## Troubleshooting

### API Key Issues
```
Error: API key not configured
```
**Solution**: Set the `GEMINI_API_KEY` environment variable

### Chrome Driver Issues
```
Error: Failed to setup WebDriver
```
**Solution**: The tool auto-downloads ChromeDriver, ensure internet connection

### Modal Not Closing
```
Warning: Could not close modal
```
**Solution**: Modal detection failed, but comparison continues. Check console for details.

### PDF Generation Failed
```
Error: Failed to generate PDF report
```
**Solution**: Check disk space and write permissions in `uploads/` folder

### Page Load Timeout
```
Warning: Page load timeout
```
**Solution**: Increase wait_time or check website availability

## Requirements

- Python 3.8+
- Google Gemini API key
- Chrome browser (for Selenium)
- Internet connection
- 2GB+ RAM recommended
- Disk space for screenshots and PDFs

## FAQ

**Q: Can I compare more than 2 URL pairs at once?**
A: Yes! Use the "+ Add Another URL Pair" button to add unlimited pairs. They'll be processed sequentially.

**Q: How long does each comparison take?**
A: Typically 2-5 minutes per URL pair, depending on page length and complexity.

**Q: What happens if a modal popup appears?**
A: The tool automatically detects and closes modals with `id="modal-hash"` after a 3-second wait.

**Q: Can I compare different environments?**
A: Yes! Compare any two URLs - production/stage, A/B variants, or completely different sites.

**Q: Where are the PDF reports saved?**
A: Reports are saved in the `uploads/` folder with names based on the URLs compared.

**Q: Can I use this for mobile testing?**
A: Yes! Select "Mobile (375x667)" viewport size to test mobile layouts.

## Cost Considerations

Google Gemini API pricing:
- **Gemini 2.5 Flash**: Most cost-effective for QA workflows
- **Token usage**: Displayed in reports
- **Image resolution**: High-detail analysis uses more tokens
- **Batch processing**: Consider API rate limits

## License

MIT License - Free for personal and commercial use.

## Contributing

Contributions welcome! Submit issues or pull requests on GitHub.

## Acknowledgments

- Built with Google Gemini Vision API
- Inspired by Adobe Firefly design system
- Chrome DevTools Protocol for browser automation

---

**Adobe Visual QA Tool** - Automated visual quality assurance for stage and production environments

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key:
```bash
# On Windows
set GEMINI_API_KEY=your-api-key-here

# On Linux/Mac
export GEMINI_API_KEY=your-api-key-here
```

Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Quick Start

### Command Line Usage

Basic comparison:
```bash
python image_comparison_tool.py image1.jpg image2.jpg
```

Find differences:
```bash
python image_comparison_tool.py image1.jpg image2.jpg -t differences
```

Detailed analysis with output file:
```bash
python image_comparison_tool.py image1.jpg image2.jpg -t detailed -o results.json
```

Custom prompt:
```bash
python image_comparison_tool.py product1.jpg product2.jpg -p "Which product image is more appealing for marketing?"
```

### Python API Usage

```python
from image_comparison_tool import ImageComparisonTool

# Initialize the tool
tool = ImageComparisonTool()

# Compare images
result = tool.compare_images(
    image1_path="image1.jpg",
    image2_path="image2.jpg",
    comparison_type="differences"
)

# Display results
if result["success"]:
    print(result["analysis"])
    
    # Save to file
    tool.save_result(result, "comparison_results.json")
```

## Comparison Types

### 1. General (`general`)
Provides a comprehensive overview including similarities, differences, visual elements, colors, and composition.

```bash
python image_comparison_tool.py img1.jpg img2.jpg -t general
```

### 2. Differences (`differences`)
Focuses specifically on identifying all differences between the images.

```bash
python image_comparison_tool.py before.jpg after.jpg -t differences
```

### 3. Similarities (`similarities`)
Highlights common elements, patterns, and shared characteristics.

```bash
python image_comparison_tool.py design1.png design2.png -t similarities
```

### 4. Detailed (`detailed`)
Provides an extremely thorough analysis including pixel-level differences, color palettes, object detection, and recommendations.

```bash
python image_comparison_tool.py photo1.jpg photo2.jpg -t detailed
```

## Command Line Options

```
usage: image_comparison_tool.py [-h] [-t {general,differences,similarities,detailed}] 
                                [-p PROMPT] [-o OUTPUT] [-m MODEL] [-k API_KEY]
                                image1 image2

positional arguments:
  image1                Path to the first image
  image2                Path to the second image

optional arguments:
  -h, --help            Show this help message and exit
  -t, --type            Type of comparison (default: general)
  -p, --prompt          Custom prompt for comparison
  -o, --output          Output JSON file path to save results
  -m, --model           OpenAI model to use (default: gpt-4o)
  -k, --api-key         OpenAI API key
```

## Use Cases

### 1. Quality Assurance
Compare original vs processed images to ensure quality:
```python
result = tool.compare_images(
    "original.jpg",
    "compressed.jpg",
    custom_prompt="Analyze the quality differences and identify any compression artifacts."
)
```

### 2. Design Review
Compare design iterations:
```python
result = tool.compare_images(
    "design_v1.png",
    "design_v2.png",
    comparison_type="differences"
)
```

### 3. Product Photography
Evaluate product images for e-commerce:
```python
result = tool.compare_images(
    "product_photo1.jpg",
    "product_photo2.jpg",
    custom_prompt="Which image is better for e-commerce? Consider lighting, composition, and appeal."
)
```

### 4. Before/After Analysis
Document changes or improvements:
```python
result = tool.compare_images(
    "before_renovation.jpg",
    "after_renovation.jpg",
    comparison_type="differences"
)
```

### 5. A/B Testing
Compare variations for marketing materials:
```python
result = tool.compare_images(
    "ad_variant_a.png",
    "ad_variant_b.png",
    custom_prompt="Which ad is more likely to drive engagement? Analyze visual hierarchy and appeal."
)
```

### 6. Viewport-by-Viewport Website Comparison
Compare two websites comprehensively across all viewport positions:
```python
from viewport_comparison_tool import ViewportComparisonTool
from viewport_report_generator import ViewportReportGenerator

# Initialize tools
viewport_tool = ViewportComparisonTool(comparison_tool=tool)

# Perform comparison
result = viewport_tool.compare_websites_by_viewport(
    url1="https://example.com",
    url2="https://example.org",
    viewport_size='desktop',
    comparison_type='differences'
)

# Generate PDF report
if result['success']:
    report_gen = ViewportReportGenerator()
    report_gen.generate_report(result, 'comparison_report.pdf')
```

**Use Cases:**
- Responsive design testing across different viewport sizes
- A/B testing of website redesigns
- Quality assurance for website updates
- Competitive analysis
- Cross-browser rendering comparison

[See full documentation →](VIEWPORT_COMPARISON_GUIDE.md)

## Example Output

```json
{
  "success": true,
  "comparison_type": "differences",
  "image1": "image1.jpg",
  "image2": "image2.jpg",
  "analysis": "The two images show several key differences:\n\n1. Color Scheme: Image 1 uses warmer tones...",
  "model_used": "gpt-4o",
  "tokens_used": {
    "prompt": 1250,
    "completion": 450,
    "total": 1700
  }
}
```

## Advanced Examples

See `example_usage.py` for more detailed examples including:
- Basic comparisons
- Finding specific differences
- Custom prompts
- Detailed analysis
- Batch processing multiple image pairs
- Direct API key usage

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)

## Screenshots

### Web Interface
- Clean, modern UI with Adobe Firefly-inspired design
- Dark/Light theme toggle
- Real-time progress updates during batch processing
- Download buttons for each generated report

### PDF Report Sample
- Full-width screenshots with clear labels
- Visual difference highlights in red
- Detailed AI analysis in bullet points
- Professional summary statistics

## Changelog

### v2.0 - December 2025
- ✨ Rebranded to "Adobe Visual QA Tool"
- ✨ Added batch URL pair comparison
- ✨ Implemented dynamic URL pair management (add/remove)
- ✨ Enhanced PDF image sizes (7" × 9" for maximum visibility)
- ✨ Vertical screenshot layout for better clarity
- ✨ Auto-detection and closing of modal popups
- ✨ Custom PDF filename format based on URLs
- ✨ Improved AI analysis display with clear bullet points
- 🐛 Fixed URL pair numbering to stay sequential
- 🐛 Enhanced fallback handling for missing AI analysis

### v1.0 - Initial Release
- Basic viewport comparison
- PDF report generation
- Multi-viewport support

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection

## License

MIT License - feel free to use this tool for personal or commercial projects.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Acknowledgments

Built with OpenAI's GPT-4 Vision API for advanced image understanding and comparison.


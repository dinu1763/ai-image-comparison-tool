# AI-Powered Image Comparison Tool

A comprehensive Python tool that uses Google Gemini Vision API to compare images and websites with detailed AI-powered analysis. Features include image comparison, website screenshot comparison, and viewport-by-viewport website analysis.

## Features

### Image Comparison
- 🔍 **Multiple Comparison Types**: General, differences, similarities, and detailed analysis
- 🎨 **Custom Prompts**: Use your own prompts for specific comparison needs
- 💾 **Save Results**: Export comparison results to JSON format
- 📊 **Technical Metrics**: SSIM scores and difference region detection
- 🎯 **High Detail Analysis**: Uses high-resolution image analysis for accurate results

### Website Comparison
- 📸 **Screenshot Capture**: Automatically capture full-page or viewport screenshots
- 🖥️ **Multiple Viewports**: Desktop, Tablet, and Mobile viewport sizes
- 🌐 **URL-based Comparison**: Compare websites directly without manual screenshots

### **NEW: Viewport-by-Viewport Comparison**
- 📑 **Comprehensive Analysis**: Compare websites viewport-by-viewport from top to bottom
- 📄 **PDF Reports**: Generate professional PDF reports with all comparisons
- 🎯 **Visual Highlights**: Automatically highlight difference regions
- 📊 **Detailed Metrics**: SSIM scores and AI analysis for each viewport
- 🔄 **Synchronized Scrolling**: Ensures accurate position-matched comparisons

[See detailed documentation →](VIEWPORT_COMPARISON_GUIDE.md)

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

## Models Available

- `gpt-4o` (default) - Latest and most capable model
- `gpt-4o-mini` - Faster and more cost-effective
- `gpt-4-turbo` - Previous generation high-performance model

## Cost Considerations

The tool uses OpenAI's Vision API which has associated costs:
- Token usage is displayed after each comparison
- Use `gpt-4o-mini` for cost-effective analysis
- Consider image resolution (high detail uses more tokens)

## Troubleshooting

### API Key Issues
```
Error: OpenAI API key not found
```
**Solution**: Set the `OPENAI_API_KEY` environment variable or pass it with `-k` flag

### Image Not Found
```
FileNotFoundError: Image 1 not found
```
**Solution**: Check that the image path is correct and the file exists

### Rate Limits
```
Error: Rate limit exceeded
```
**Solution**: Wait a moment and try again, or upgrade your OpenAI API plan

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


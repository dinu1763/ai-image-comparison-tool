# Section-Based Viewport Comparison - Implementation Summary

## Overview

The viewport comparison feature has been successfully modified to capture **3 separate screenshots per viewport** instead of 1. Each viewport is now divided into 3 equal horizontal sections, and each section is analyzed independently.

## What Changed

### Previous Behavior
- Captured 1 screenshot per viewport (full viewport height, e.g., 1080px for desktop)
- If a page had 10 viewports, it would capture 10 screenshots total

### New Behavior
- Divides each viewport into 3 equal horizontal sections
- Captures 3 separate screenshots per viewport (top, middle, bottom sections)
- Each section is analyzed independently with AI and SSIM
- If a page has 10 viewports, it now captures **30 screenshots** (10 × 3 sections)

## Technical Implementation

### 1. New Screenshot Capture Method

**File:** `viewport_comparison_tool.py`

Added a new method `_capture_viewport_section()` that:
- Takes a full viewport screenshot
- Crops it to a specific section based on offset and height
- Returns the cropped section as a PIL Image

```python
def _capture_viewport_section(self, driver, section_height, section_offset):
    """
    Capture a specific section of the viewport
    
    Args:
        driver: Selenium WebDriver instance
        section_height: Height of the section to capture
        section_offset: Vertical offset from top of viewport (0 for top section)
    
    Returns:
        PIL Image of the section
    """
```

### 2. Modified Comparison Loop

**File:** `viewport_comparison_tool.py`

The main comparison loop now:
1. Calculates section height: `section_height = viewport_height // 3`
2. For each viewport position:
   - Scrolls to the viewport position
   - Loops through 3 sections (0, 1, 2)
   - For each section:
     - Captures section screenshot from both websites
     - Runs SSIM analysis
     - Detects difference regions
     - Performs AI analysis
     - Stores section data

### 3. Updated Data Structure

Each section now stores:
- `section_number`: Global section counter (1, 2, 3, 4, ...)
- `viewport_number`: Which viewport this section belongs to
- `section_within_viewport`: Position within viewport (1, 2, or 3)
- `total_sections`: Total number of sections analyzed
- `scroll_position`: Viewport scroll position
- `section_offset`: Offset within the viewport (0, 360px, 720px for 1080px viewport)
- `section_dimensions`: Width and height of the section
- All other existing fields (screenshots, SSIM, AI analysis, etc.)

### 4. Updated Summary Information

**File:** `viewport_comparison_tool.py`

The summary now includes:
- `section_height`: Height of each section in pixels
- `sections_per_viewport`: Always 3
- `total_viewports`: Number of viewports (unchanged)
- `total_sections`: Total number of sections analyzed (viewports × 3)

### 5. PDF Report Updates

**File:** `viewport_report_generator.py`

Updated to handle section-based data:
- Summary page shows section information (section height, sections per viewport, total sections)
- Each comparison page shows:
  - "Section X of Y" instead of "Viewport X of Y"
  - "Viewport N - Section M/3" to show which viewport and section
  - Both scroll position and section offset
- Backward compatible with old viewport-based data

### 6. Web UI Updates

**File:** `static/js/script.js`

Updated the results display to show:
- Sections per viewport
- Total sections analyzed
- Updated success message to include section count

**File:** `app.py`

Updated the success message to show both viewports and sections:
- "Comparison complete! X viewports analyzed (Y sections total)."

## Example Output

### For a page with 10 viewports (desktop 1920x1080):

**Previous:**
- 10 screenshots captured
- 10 comparisons performed
- PDF with 10 comparison pages

**New:**
- 30 screenshots captured (10 viewports × 3 sections)
- 30 comparisons performed
- PDF with 30 comparison pages
- Each section is 360px tall (1080 ÷ 3)

### Console Output Example:

```
Will capture 10 viewport(s) with 3 sections each
Total sections to analyze: 30
Section height: 360px

Processing viewport 1/10 (scroll: 0px)...
  Capturing section 1/3 (offset: 0px)...
    Running AI analysis for section 1...
    SSIM Score: 0.9950
    Differences detected: 1
  Capturing section 2/3 (offset: 360px)...
    Running AI analysis for section 2...
    SSIM Score: 0.9831
    Differences detected: 2
  Capturing section 3/3 (offset: 720px)...
    Running AI analysis for section 3...
    SSIM Score: 0.9876
    Differences detected: 1

Processing viewport 2/10 (scroll: 1080px)...
  ...
```

## Files Modified

1. **viewport_comparison_tool.py**
   - Added `_capture_viewport_section()` method
   - Modified main comparison loop to capture 3 sections per viewport
   - Updated data structure to track sections
   - Updated summary to include section information

2. **viewport_report_generator.py**
   - Updated summary page to show section metrics
   - Modified comparison page to display section information
   - Added backward compatibility for old viewport-based data

3. **static/js/script.js**
   - Updated results display to show section information
   - Added conditional display for section metrics

4. **app.py**
   - Updated success message to include section count

## Testing

To test the new feature:

1. Start the Flask application:
   ```powershell
   python app.py
   ```

2. Navigate to the Viewport Comparison tab

3. Enter two website URLs (e.g., staging vs production)

4. Click "Compare Viewports"

5. Check the console output to see section-by-section progress

6. Download the PDF report to see all sections analyzed

## Benefits

1. **More Granular Analysis**: Detects differences in specific parts of the viewport
2. **Better Coverage**: Ensures no part of the page is missed
3. **Detailed Reports**: PDF shows exactly where in each viewport differences occur
4. **Same Scroll Behavior**: Still scrolls by full viewport height, maintaining page context
5. **Independent Analysis**: Each section gets its own AI analysis and SSIM score

## Backward Compatibility

The PDF report generator includes backward compatibility checks:
- Detects if data is section-based or old viewport-based
- Handles both formats correctly
- Old reports will still work if regenerated

## Performance Considerations

- **More API Calls**: 3× more AI analysis calls (if using AI comparison)
- **More Processing Time**: 3× longer to complete comparison
- **Larger PDF Files**: More pages in the report
- **More Temporary Files**: 3× more screenshot files (cleaned up after PDF generation)

For a typical comparison that previously took 5 minutes, expect approximately 15 minutes with the new section-based approach.


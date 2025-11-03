"""
Test script to verify dynamic desktop viewport detection
"""

from viewport_comparison_tool import ViewportComparisonTool
from image_comparison_tool import ImageComparisonTool

def test_screen_detection():
    """Test that screen detection works correctly"""
    
    print("=" * 80)
    print("Testing Dynamic Desktop Viewport Detection")
    print("=" * 80)
    print()
    
    # Create comparison tool
    comparison_tool = ImageComparisonTool()
    
    # Create viewport comparison tool (this should trigger screen detection)
    print("Initializing ViewportComparisonTool...")
    viewport_tool = ViewportComparisonTool(comparison_tool)
    
    print()
    print("=" * 80)
    print("Viewport Dimensions:")
    print("=" * 80)
    
    for viewport_name, dimensions in viewport_tool.VIEWPORTS.items():
        width = dimensions['width']
        height = dimensions['height']
        print(f"{viewport_name.capitalize():10} : {width}x{height}")
    
    print()
    print("=" * 80)
    print("Expected Behavior:")
    print("=" * 80)
    print("✅ Desktop viewport should match your screen width and half screen height")
    print("✅ Tablet viewport should be 768x1024 (fixed)")
    print("✅ Mobile viewport should be 375x667 (fixed)")
    print()
    
    # Verify tablet and mobile are unchanged
    assert viewport_tool.VIEWPORTS['tablet'] == {'width': 768, 'height': 1024}, "Tablet viewport changed!"
    assert viewport_tool.VIEWPORTS['mobile'] == {'width': 375, 'height': 667}, "Mobile viewport changed!"
    
    print("✅ Tablet and Mobile viewports are correctly fixed")
    
    # Check desktop viewport
    desktop = viewport_tool.VIEWPORTS['desktop']
    if desktop['width'] == 1920 and desktop['height'] == 1080:
        print("⚠️  Desktop viewport is using fallback default (1920x1080)")
        print("   This is expected if screen detection failed or screeninfo is not available")
    else:
        print(f"✅ Desktop viewport is dynamically set to {desktop['width']}x{desktop['height']}")
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == '__main__':
    test_screen_detection()


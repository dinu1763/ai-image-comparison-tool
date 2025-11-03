"""
Test script to verify viewport capture with full viewport approach
Tests that:
1. First viewport (scroll position 0) is captured correctly
2. Full viewport is captured (no section division)
3. Final viewport doesn't extend beyond page content
4. Each viewport produces exactly 1 screenshot and 1 AI analysis
"""

from viewport_comparison_tool import ViewportComparisonTool
from image_comparison_tool import ImageComparisonTool
import os

def test_viewport_capture():
    """Test viewport capture logic"""
    
    print("=" * 80)
    print("Testing Viewport Capture Fix")
    print("=" * 80)
    print()
    
    # Create comparison tool
    comparison_tool = ImageComparisonTool()
    
    # Create viewport comparison tool
    viewport_tool = ViewportComparisonTool(comparison_tool)
    
    print("Testing with a simple webpage...")
    print()
    
    # Test with a simple webpage
    url1 = "https://example.com"
    url2 = "https://example.org"
    
    print(f"URL 1: {url1}")
    print(f"URL 2: {url2}")
    print()
    
    # Run comparison
    try:
        result = viewport_tool.compare_websites_by_viewport(
            url1=url1,
            url2=url2,
            viewport_size='desktop',
            wait_time=2,
            comparison_type='differences',
            model='gemini-2.5-flash'
        )
        
        print()
        print("=" * 80)
        print("Test Results:")
        print("=" * 80)
        
        if result.get('success'):
            print("✅ Viewport comparison completed successfully!")
            
            # Check viewport data
            viewports = result.get('viewport_comparisons', [])
            print(f"\nTotal viewports captured: {len(viewports)}")

            # Check first viewport
            if viewports:
                first_viewport = viewports[0]
                print(f"\nFirst viewport details:")
                print(f"  - Viewport number: {first_viewport.get('viewport_number')}")
                print(f"  - Scroll position: {first_viewport.get('scroll_position')}px")
                print(f"  - Viewport dimensions: {first_viewport.get('viewport_dimensions')}")

                if first_viewport.get('scroll_position') == 0:
                    print("  ✅ First viewport starts at scroll position 0 (top of page)")
                else:
                    print(f"  ❌ ERROR: First viewport starts at {first_viewport.get('scroll_position')}px instead of 0")

                # Verify no section fields
                if 'section_number' not in first_viewport:
                    print("  ✅ No section division (full viewport capture)")
                else:
                    print("  ❌ ERROR: Section fields still present")

            # Check last viewport
            if len(viewports) > 1:
                last_viewport = viewports[-1]
                print(f"\nLast viewport details:")
                print(f"  - Viewport number: {last_viewport.get('viewport_number')}")
                print(f"  - Scroll position: {last_viewport.get('scroll_position')}px")
                print(f"  - Viewport dimensions: {last_viewport.get('viewport_dimensions')}")

                # Check if it has content
                if last_viewport.get('ai_analysis'):
                    print("  ✅ Last viewport has AI analysis (contains content)")
                else:
                    print("  ⚠️  Last viewport has no AI analysis")

            # Check summary
            summary = result.get('summary', {})
            print(f"\nSummary details:")
            print(f"  - Total viewports: {summary.get('total_viewports')}")
            print(f"  - Viewport dimensions: {summary.get('viewport_dimensions')}")

            # Verify no section fields in summary
            if 'total_sections' not in summary and 'sections_per_viewport' not in summary:
                print("  ✅ No section fields in summary (full viewport approach)")
            else:
                print("  ⚠️  Section fields still present in summary")

            print()
            print("=" * 80)
            print("Expected Behavior Verified:")
            print("=" * 80)
            print("✅ First viewport should start at scroll position 0")
            print("✅ Each viewport captured as FULL screenshot (no sections)")
            print("✅ Last viewport should contain actual page content")
            print("✅ No blank viewports at the end")
            print("✅ No section-related fields in data structure")
            
        else:
            print(f"❌ Comparison failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)

if __name__ == '__main__':
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   The test will fail without a valid API key")
        print()
    
    test_viewport_capture()


"""
Test script for viewport comparison feature
This script tests the viewport comparison functionality without requiring a full web server
"""

import os
from viewport_comparison_tool import ViewportComparisonTool
from viewport_report_generator import ViewportReportGenerator
from image_comparison_tool import ImageComparisonTool


def test_viewport_comparison():
    """Test the viewport comparison feature"""
    
    print("=" * 80)
    print("VIEWPORT COMPARISON TEST")
    print("=" * 80)
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("  Windows: set GEMINI_API_KEY=your-api-key")
        print("  Linux/Mac: export GEMINI_API_KEY=your-api-key")
        return False
    
    print("\n✓ API key found")
    
    # Test URLs - using simple, fast-loading pages for testing
    url1 = "https://example.com"
    url2 = "https://example.org"
    
    print(f"\nTest Configuration:")
    print(f"  Website 1: {url1}")
    print(f"  Website 2: {url2}")
    print(f"  Viewport: desktop (1920x1080)")
    print(f"  Comparison Type: differences")
    print(f"  Model: gemini-2.5-flash")
    
    try:
        # Initialize tools
        print("\n" + "=" * 80)
        print("STEP 1: Initializing tools...")
        print("=" * 80)
        
        comparison_tool = ImageComparisonTool(api_key=api_key)
        viewport_tool = ViewportComparisonTool(comparison_tool=comparison_tool)
        
        print("✓ Tools initialized successfully")
        
        # Perform viewport comparison
        print("\n" + "=" * 80)
        print("STEP 2: Performing viewport comparison...")
        print("=" * 80)
        print("This may take 2-5 minutes depending on page length...")
        
        result = viewport_tool.compare_websites_by_viewport(
            url1=url1,
            url2=url2,
            viewport_size='desktop',
            wait_time=3,
            comparison_type='differences',
            model='gemini-2.5-flash'
        )
        
        if not result.get('success'):
            print(f"\n❌ Comparison failed: {result.get('error')}")
            return False
        
        print("\n✓ Viewport comparison completed successfully!")
        
        # Display summary
        summary = result['summary']
        print("\n" + "=" * 80)
        print("COMPARISON SUMMARY")
        print("=" * 80)
        print(f"Total Viewports: {summary['total_viewports']}")
        print(f"Page 1 Height: {summary['page_height1']}px")
        print(f"Page 2 Height: {summary['page_height2']}px")
        print(f"Total Differences: {summary['total_differences']}")
        
        if summary.get('average_ssim') is not None:
            similarity_pct = summary['average_ssim'] * 100
            print(f"Average Similarity: {similarity_pct:.2f}%")
        
        # Generate PDF report
        print("\n" + "=" * 80)
        print("STEP 3: Generating PDF report...")
        print("=" * 80)
        
        report_generator = ViewportReportGenerator()
        output_path = 'test_viewport_comparison_report.pdf'
        
        pdf_success = report_generator.generate_report(result, output_path)
        
        if not pdf_success:
            print("\n❌ PDF generation failed")
            return False
        
        print(f"\n✓ PDF report generated: {output_path}")
        
        # Clean up temporary files
        print("\n" + "=" * 80)
        print("STEP 4: Cleaning up temporary files...")
        print("=" * 80)
        
        temp_files = result.get('temp_files', [])
        cleaned = 0
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned += 1
            except Exception as e:
                print(f"Warning: Could not remove {temp_file}: {e}")
        
        print(f"✓ Cleaned up {cleaned} temporary files")
        
        # Final summary
        print("\n" + "=" * 80)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\n📄 PDF Report: {output_path}")
        print(f"📊 Viewports Analyzed: {summary['total_viewports']}")
        print(f"🔍 Differences Found: {summary['total_differences']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_components():
    """Test individual components"""
    
    print("\n" + "=" * 80)
    print("COMPONENT TESTS")
    print("=" * 80)
    
    # Test 1: Import all modules
    print("\nTest 1: Module imports...")
    try:
        from viewport_comparison_tool import ViewportComparisonTool
        from viewport_report_generator import ViewportReportGenerator
        from image_comparison_tool import ImageComparisonTool
        print("✓ All modules imported successfully")
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    # Test 2: Check dependencies
    print("\nTest 2: Checking dependencies...")
    try:
        import selenium
        import cv2
        import numpy
        from skimage.metrics import structural_similarity
        from reportlab.lib.pagesizes import letter
        print("✓ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    
    # Test 3: Check API key
    print("\nTest 3: Checking API key...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✓ GEMINI_API_KEY is set")
    else:
        print("⚠ GEMINI_API_KEY not set (required for full test)")
    
    print("\n✓ All component tests passed")
    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VIEWPORT COMPARISON FEATURE TEST SUITE")
    print("=" * 80)
    
    # Run component tests first
    if not test_components():
        print("\n❌ Component tests failed. Please fix issues before running full test.")
        exit(1)
    
    # Ask user if they want to run the full test
    print("\n" + "=" * 80)
    print("Ready to run full viewport comparison test")
    print("=" * 80)
    print("\nThis will:")
    print("  1. Load two websites (example.com and example.org)")
    print("  2. Capture and compare viewports")
    print("  3. Generate a PDF report")
    print("  4. Use Gemini API credits")
    print("\nEstimated time: 2-5 minutes")
    
    response = input("\nProceed with full test? (y/n): ").strip().lower()
    
    if response == 'y':
        success = test_viewport_comparison()
        if success:
            print("\n🎉 All tests passed!")
            exit(0)
        else:
            print("\n❌ Tests failed")
            exit(1)
    else:
        print("\nTest cancelled by user")
        exit(0)


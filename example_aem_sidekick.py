"""
Example: Using the Visual QA Tool with AEM Sidekick Extension

This example demonstrates how to use the viewport comparison tool
with Chrome extension support for AEM-based websites.
"""

from viewport_comparison_tool import ViewportComparisonTool
from image_comparison_tool import ImageComparisonTool
import os

# Configuration
EXTENSION_PATH = r"C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension-id\version"
USER_EMAIL = "dineshkumar@adobe.com"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Example URLs requiring AEM Sidekick
URL1 = "https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off"
URL2 = "https://www.adobe.com/products/firefly/features/ai-art-generator"

def main():
    """
    Run viewport comparison with AEM Sidekick extension support
    """
    
    print("=" * 70)
    print("Visual QA Tool - AEM Sidekick Extension Example")
    print("=" * 70)
    print()
    
    # Initialize tools
    print("Initializing comparison tools...")
    comparison_tool = ImageComparisonTool(api_key=GEMINI_API_KEY)
    
    # Create viewport comparison tool with extension support
    viewport_tool = ViewportComparisonTool(
        comparison_tool=comparison_tool,
        extension_path=EXTENSION_PATH,
        user_email=USER_EMAIL
    )
    
    print(f"✓ Comparison tool initialized")
    print(f"✓ Extension path: {EXTENSION_PATH}")
    print(f"✓ User email: {USER_EMAIL}")
    print()
    
    # Run comparison
    print("Starting viewport comparison...")
    print(f"  URL 1: {URL1}")
    print(f"  URL 2: {URL2}")
    print()
    
    result = viewport_tool.compare_websites_by_viewport(
        url1=URL1,
        url2=URL2,
        viewport_size='desktop',
        wait_time=3,
        comparison_type='differences',
        model='gemini-3-flash-preview'
    )
    
    # Display results
    print()
    print("=" * 70)
    print("Comparison Results")
    print("=" * 70)
    
    if result.get('success'):
        summary = result['summary']
        print(f"✓ Comparison completed successfully!")
        print()
        print(f"Total Viewports Analyzed: {summary.get('total_viewports', 'N/A')}")
        print(f"Total Sections: {summary.get('total_sections', 'N/A')}")
        print(f"Average SSIM Score: {summary.get('average_ssim', 'N/A')}")
        print()
        
        # Viewport details
        if 'viewports' in result:
            print("Viewport-by-Viewport Analysis:")
            for i, viewport in enumerate(result['viewports'], 1):
                print(f"\n  Viewport {i}:")
                print(f"    Position: {viewport.get('scroll_position', 'N/A')}px")
                print(f"    SSIM Score: {viewport.get('ssim_score', 'N/A')}")
                
                if 'analysis' in viewport:
                    analysis_preview = viewport['analysis'][:200] + "..." if len(viewport['analysis']) > 200 else viewport['analysis']
                    print(f"    Analysis: {analysis_preview}")
    else:
        print(f"✗ Comparison failed: {result.get('error', 'Unknown error')}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    # Validate configuration
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set it using: set GEMINI_API_KEY=your-api-key")
        exit(1)
    
    if not os.path.exists(EXTENSION_PATH) and "extension-id" not in EXTENSION_PATH:
        print("WARNING: Extension path may not be configured correctly")
        print(f"Current path: {EXTENSION_PATH}")
        print()
        print("Please update EXTENSION_PATH variable with actual extension location:")
        print("1. Go to chrome://extensions/")
        print("2. Find AEM Sidekick extension")
        print("3. Note the extension ID and version")
        print("4. Update EXTENSION_PATH in this script")
        print()
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            exit(0)
    
    # Run comparison
    main()

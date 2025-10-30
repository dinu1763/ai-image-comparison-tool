"""
Quick test script for image comparison with API key included
"""

from image_comparison_tool import ImageComparisonTool

# Your Gemini API key
API_KEY = "AIzaSyDIO_8C7YMWjXMbpPzemtjTOqeWH9UGT_A"

def test_comparison():
    """Test the image comparison tool"""
    
    # Initialize the tool with your API key
    tool = ImageComparisonTool(api_key=API_KEY)
    
    # Replace these with your actual image paths
    image1_path = r".\Screenshot 2025-10-28 115838.png"
    image2_path = r".\Screenshot 2025-10-28 154250.png"
    
    print("Starting image comparison...")
    print(f"Image 1: {image1_path}")
    print(f"Image 2: {image2_path}")
    print("-" * 80)
    
    # Compare images
    result = tool.compare_images(
        image1_path=image1_path,
        image2_path=image2_path,
        comparison_type="general"  # Options: general, differences, similarities, detailed
    )
    
    # Display results
    if result["success"]:
        print("\n✓ COMPARISON SUCCESSFUL!\n")
        print("=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        print(result["analysis"])
        print("\n" + "=" * 80)
        print(f"Model used: {result['model_used']}")
        print(f"Tokens used: {result['tokens_used']['total']}")
        print("=" * 80)
        
        # Optionally save to file
        tool.save_result(result, "comparison_result.json")
        print("\n✓ Results saved to: comparison_result.json")
    else:
        print(f"\n✗ ERROR: {result['error']}")
        print("\nPlease check:")
        print("1. Image paths are correct")
        print("2. Image files exist")
        print("3. API key is valid")

if __name__ == "__main__":
    test_comparison()


"""
Example usage of the Image Comparison Tool
"""

from image_comparison_tool import ImageComparisonTool
import os

def example_basic_comparison():
    """Example: Basic image comparison"""
    print("Example 1: Basic Image Comparison")
    print("-" * 50)

    # Initialize the tool (make sure GEMINI_API_KEY is set in environment)
    tool = ImageComparisonTool()
    
    # Compare two images
    result = tool.compare_images(
        image1_path="image1.jpg",
        image2_path="image2.jpg",
        comparison_type="general"
    )
    
    if result["success"]:
        print("Analysis:")
        print(result["analysis"])
        print(f"\nTokens used: {result['tokens_used']['total']}")
    else:
        print(f"Error: {result['error']}")


def example_find_differences():
    """Example: Find specific differences between images"""
    print("\nExample 2: Finding Differences")
    print("-" * 50)
    
    tool = ImageComparisonTool()
    
    result = tool.compare_images(
        image1_path="before.jpg",
        image2_path="after.jpg",
        comparison_type="differences"
    )
    
    if result["success"]:
        print("Differences found:")
        print(result["analysis"])
        
        # Save results to file
        tool.save_result(result, "comparison_results.json")


def example_custom_prompt():
    """Example: Using a custom prompt for specific analysis"""
    print("\nExample 3: Custom Prompt")
    print("-" * 50)
    
    tool = ImageComparisonTool()
    
    custom_prompt = """
    Compare these two product images and tell me:
    1. Which one has better lighting?
    2. Which one is more appealing for e-commerce?
    3. What improvements could be made to each image?
    4. Are there any quality issues in either image?
    """
    
    result = tool.compare_images(
        image1_path="product1.jpg",
        image2_path="product2.jpg",
        custom_prompt=custom_prompt
    )
    
    if result["success"]:
        print("Custom Analysis:")
        print(result["analysis"])


def example_detailed_analysis():
    """Example: Detailed comparison with all aspects"""
    print("\nExample 4: Detailed Analysis")
    print("-" * 50)

    tool = ImageComparisonTool()

    result = tool.compare_images(
        image1_path="design_v1.png",
        image2_path="design_v2.png",
        comparison_type="detailed",
        model="gemini-2.5-pro"  # Using the most capable model
    )
    
    if result["success"]:
        print("Detailed Analysis:")
        print(result["analysis"])
        
        # Save to file
        tool.save_result(result, "detailed_comparison.json")


def example_batch_comparison():
    """Example: Compare multiple pairs of images"""
    print("\nExample 5: Batch Comparison")
    print("-" * 50)
    
    tool = ImageComparisonTool()
    
    image_pairs = [
        ("screenshot1.png", "screenshot2.png"),
        ("logo_old.png", "logo_new.png"),
        ("photo_original.jpg", "photo_edited.jpg")
    ]
    
    results = []
    for img1, img2 in image_pairs:
        print(f"\nComparing {img1} vs {img2}...")
        result = tool.compare_images(
            image1_path=img1,
            image2_path=img2,
            comparison_type="differences"
        )
        results.append(result)
        
        if result["success"]:
            print(f"✓ Comparison complete")
        else:
            print(f"✗ Error: {result['error']}")
    
    # Save all results
    import json
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nAll results saved to batch_results.json")


def example_with_api_key():
    """Example: Providing API key directly"""
    print("\nExample 6: Using API Key Directly")
    print("-" * 50)
    
    # You can provide the API key directly instead of using environment variable
    api_key = "AIzaSyDIO_8C7YMWjXMbpPzemtjTOqeWH9UGT_A"  # Replace with your actual API key
    
    tool = ImageComparisonTool(api_key=api_key)
    
    result = tool.compare_images(
        image1_path="image1.jpg",
        image2_path="image2.jpg",
        comparison_type="similarities"
    )
    
    if result["success"]:
        print("Similarities found:")
        print(result["analysis"])


if __name__ == "__main__":
    print("Image Comparison Tool - Example Usage")
    print("=" * 50)
    print("\nNote: Make sure to:")
    print("1. Set your GEMINI_API_KEY environment variable")
    print("2. Have actual image files in the specified paths")
    print("3. Install requirements: pip install -r requirements.txt")
    print("\n" + "=" * 50)
    
    # Uncomment the examples you want to run:
    
    # example_basic_comparison()
    # example_find_differences()
    # example_custom_prompt()
    # example_detailed_analysis()
    # example_batch_comparison()
    # example_with_api_key()
    
    print("\nUncomment the examples in the code to run them!")


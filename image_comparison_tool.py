"""
Image Comparison Tool using LLM (Google Gemini Vision)
This tool compares two images using Google Gemini API and provides detailed analysis.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

try:
    import google.generativeai as genai
    from PIL import Image
except ImportError:
    print("Required libraries not installed. Please run: pip install google-generativeai Pillow")
    exit(1)


class ImageComparisonTool:
    """A tool to compare two images using LLM vision capabilities."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Image Comparison Tool.

        Args:
            api_key: Google Gemini API key. If not provided, will look for GEMINI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google Gemini API key not found. Please provide it as an argument or set GEMINI_API_KEY environment variable."
            )
        genai.configure(api_key=self.api_key)

    def load_image(self, image_path: str) -> Image.Image:
        """
        Load image from file path.

        Args:
            image_path: Path to the image file.

        Returns:
            PIL Image object.
        """
        return Image.open(image_path)
    
    def compare_images(
        self,
        image1_path: str,
        image2_path: str,
        comparison_type: str = "general",
        custom_prompt: Optional[str] = None,
        model: str = "gemini-2.5-flash"
    ) -> Dict[str, Any]:
        """
        Compare two images using Google Gemini Vision.

        Args:
            image1_path: Path to the first image.
            image2_path: Path to the second image.
            comparison_type: Type of comparison - 'general', 'differences', 'similarities', 'detailed'
            custom_prompt: Custom prompt for specific comparison needs.
            model: Gemini model to use (default: gemini-2.5-flash, options: gemini-2.5-pro, gemini-2.0-flash)

        Returns:
            Dictionary containing the comparison results.
        """
        # Validate image paths
        if not Path(image1_path).exists():
            raise FileNotFoundError(f"Image 1 not found: {image1_path}")
        if not Path(image2_path).exists():
            raise FileNotFoundError(f"Image 2 not found: {image2_path}")

        # Load images
        image1 = self.load_image(image1_path)
        image2 = self.load_image(image2_path)

        # Prepare prompt based on comparison type
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self._get_prompt_for_type(comparison_type)

        # Add instruction to analyze both images
        full_prompt = f"{prompt}\n\nImage 1 is the first image, and Image 2 is the second image. Please analyze both carefully."

        # Make API call
        try:
            # Initialize the model
            model_instance = genai.GenerativeModel(model)

            # Generate content with both images
            response = model_instance.generate_content([
                full_prompt,
                image1,
                image2
            ])

            result = {
                "success": True,
                "comparison_type": comparison_type,
                "image1": image1_path,
                "image2": image2_path,
                "analysis": response.text,
                "model_used": model,
                "tokens_used": {
                    "prompt": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "completion": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "total": getattr(response.usage_metadata, 'total_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                }
            }

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image1": image1_path,
                "image2": image2_path
            }
    
    def _get_prompt_for_type(self, comparison_type: str) -> str:
        """
        Get the appropriate prompt based on comparison type.
        
        Args:
            comparison_type: Type of comparison requested.
            
        Returns:
            Formatted prompt string.
        """
        prompts = {
            "general": """
                Compare these two images concisely. Provide ONLY:
                
                **Key Differences:**
                • List 3-5 most important visual differences (be specific and brief)
                
                **Similarities:**
                • List 2-3 main common elements
                
                **Overall Assessment:**
                • One sentence summary of the comparison
                
                Keep each bullet point to 1-2 lines maximum. Be direct and precise.
            """,
            "differences": """
                Identify all differences between these images. Use this exact format:
                
                **Layout & Structure:**
                • List any layout differences (1-2 lines each)
                
                **Visual Elements:**
                • List changes in colors, images, or graphics (1-2 lines each)
                
                **Content:**
                • List text or content changes (1-2 lines each)
                
                **Other Changes:**
                • List any other notable differences (1-2 lines each)
                
                Be specific but concise. If no differences in a category, write "No differences detected."
            """,
            "similarities": """
                Identify similarities between these images. Use this exact format:
                
                **Common Elements:**
                • List 3-5 shared visual elements (1 line each)
                
                **Consistent Features:**
                • List 2-3 matching design aspects (1 line each)
                
                **Overall Similarity:**
                • One sentence assessment
                
                Be brief and specific.
            """,
            "detailed": """
                Provide a detailed comparison using this exact format:
                
                **Critical Differences:**
                • List top 5 most important differences (1-2 lines each)
                
                **Visual Quality:**
                • Compare resolution, clarity, and overall quality (2-3 lines total)
                
                **Design Elements:**
                • Compare layout, colors, typography (2-3 lines total)
                
                **Content Analysis:**
                • Compare text, images, and information presented (2-3 lines total)
                
                **Recommendation:**
                • One clear recommendation or insight (2-3 lines)
                
                Keep each section concise and actionable.
            """,
            "responsive": """
                Please analyze these two website screenshots captured at a specific viewport size (mobile, tablet, or desktop).
                Focus on responsive design and layout differences:

                1. **Layout & Structure:**
                   - How does the page layout differ between the two websites?
                   - Are navigation menus displayed differently (hamburger menu, full menu, etc.)?
                   - How is content organized and stacked vertically?
                   - Are there differences in grid layouts, columns, or content flow?

                2. **Typography & Readability:**
                   - Font sizes and line heights
                   - Text wrapping and paragraph width
                   - Heading hierarchy and emphasis
                   - Readability on the viewport size

                3. **Interactive Elements:**
                   - Button sizes and touch target areas
                   - Form input field sizing
                   - Spacing between clickable elements
                   - Mobile-specific UI patterns (swipe gestures, accordions, etc.)

                4. **Images & Media:**
                   - Image scaling and aspect ratios
                   - Responsive image loading
                   - Video player controls and sizing
                   - Icon sizes and visibility

                5. **Spacing & Whitespace:**
                   - Padding and margins around elements
                   - Content density
                   - Vertical rhythm and spacing consistency

                6. **Mobile-Specific Features:**
                   - Sticky headers or footers
                   - Bottom navigation bars
                   - Pull-to-refresh indicators
                   - Mobile-optimized carousels or sliders

                7. **Performance Indicators:**
                   - Lazy-loaded content visibility
                   - Above-the-fold content differences
                   - Progressive enhancement patterns

                8. **Accessibility & UX:**
                   - Touch-friendly element sizing (minimum 44x44px)
                   - Contrast ratios for readability
                   - Viewport meta tag effects
                   - Orientation-specific layouts

                Provide a comprehensive analysis of how each website adapts to this viewport size,
                highlighting which site provides a better responsive experience and why.
            """
        }

        return prompts.get(comparison_type, prompts["general"])
    
    def save_result(self, result: Dict[str, Any], output_path: str):
        """
        Save comparison result to a JSON file.
        
        Args:
            result: Comparison result dictionary.
            output_path: Path to save the JSON file.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")


def main():
    """Main function to run the image comparison tool from command line."""
    parser = argparse.ArgumentParser(
        description="Compare two images using Google Gemini Vision API"
    )
    parser.add_argument(
        "image1",
        help="Path to the first image"
    )
    parser.add_argument(
        "image2",
        help="Path to the second image"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["general", "differences", "similarities", "detailed"],
        default="general",
        help="Type of comparison to perform (default: general)"
    )
    parser.add_argument(
        "-p", "--prompt",
        help="Custom prompt for comparison"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path to save results"
    )
    parser.add_argument(
        "-m", "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use (default: gemini-2.5-flash, options: gemini-2.5-pro, gemini-2.0-flash)"
    )
    parser.add_argument(
        "-k", "--api-key",
        help="Google Gemini API key (or set GEMINI_API_KEY environment variable)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize the tool
        tool = ImageComparisonTool(api_key=args.api_key)
        
        print(f"Comparing images:")
        print(f"  Image 1: {args.image1}")
        print(f"  Image 2: {args.image2}")
        print(f"  Comparison Type: {args.type}")
        print(f"  Model: {args.model}")
        print("\nAnalyzing images...\n")
        
        # Compare images
        result = tool.compare_images(
            image1_path=args.image1,
            image2_path=args.image2,
            comparison_type=args.type,
            custom_prompt=args.prompt,
            model=args.model
        )
        
        # Display results
        if result["success"]:
            print("=" * 80)
            print("COMPARISON RESULTS")
            print("=" * 80)
            print(result["analysis"])
            print("\n" + "=" * 80)
            print(f"Tokens used: {result['tokens_used']['total']} "
                  f"(prompt: {result['tokens_used']['prompt']}, "
                  f"completion: {result['tokens_used']['completion']})")
            print("=" * 80)
            
            # Save to file if requested
            if args.output:
                tool.save_result(result, args.output)
        else:
            print(f"Error: {result['error']}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())


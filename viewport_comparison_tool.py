"""
Viewport-by-Viewport Website Comparison Tool
Compares two websites by capturing and analyzing each viewport position
"""

import os
import time
import io
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont
import tempfile
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from image_comparison_tool import ImageComparisonTool
from screenshot_tool import WebsiteScreenshotTool

try:
    import cv2
    import numpy as np
    from skimage.metrics import structural_similarity as ssim
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False


class ViewportComparisonTool:
    """Tool for comparing websites viewport-by-viewport"""

    # Viewport presets (tablet and mobile are fixed, desktop is dynamic)
    VIEWPORTS = {
        'desktop': {'width': 1920, 'height': 1080},  # Fallback default
        'tablet': {'width': 768, 'height': 1024},
        'mobile': {'width': 375, 'height': 667}
    }

    # User agent strings
    USER_AGENTS = {
        'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'tablet': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }

    def __init__(self, comparison_tool: Optional[ImageComparisonTool] = None):
        """
        Initialize the viewport comparison tool

        Args:
            comparison_tool: ImageComparisonTool instance for AI analysis
        """
        self.comparison_tool = comparison_tool
        self.screenshot_tool = WebsiteScreenshotTool()

        # Detect and set dynamic desktop viewport dimensions
        self._detect_desktop_viewport()

    def _detect_desktop_viewport(self):
        """
        Detect the current machine's screen resolution and calculate desktop viewport dimensions.
        Desktop viewport height is set to half the screen height.
        Falls back to default 1920x1080 if detection fails.
        """
        try:
            if not SCREENINFO_AVAILABLE:
                print("⚠️  screeninfo library not available. Using default desktop viewport (1920x1080)")
                return

            # Get primary monitor
            monitors = get_monitors()
            if not monitors:
                print("⚠️  No monitors detected. Using default desktop viewport (1920x1080)")
                return

            # Use the primary monitor (first one)
            primary_monitor = monitors[0]
            screen_width = primary_monitor.width
            screen_height = primary_monitor.height

            # Calculate viewport dimensions: width = screen width, height = half screen height
            viewport_width = screen_width
            viewport_height = screen_height // 2  # Integer division for whole pixels

            # Update the desktop viewport
            self.VIEWPORTS['desktop'] = {
                'width': viewport_width,
                'height': viewport_height
            }

            print(f"✅ Desktop viewport auto-detected: {viewport_width}x{viewport_height}")
            print(f"   (Screen resolution: {screen_width}x{screen_height}, using half height)")

        except Exception as e:
            print(f"⚠️  Failed to detect screen resolution: {str(e)}")
            print(f"   Using default desktop viewport (1920x1080)")
            # Keep the default fallback values in VIEWPORTS
        
    def _setup_driver(self, viewport_size='desktop', headless=True):
        """Setup Chrome WebDriver with specified options"""
        try:
            chrome_options = Options()
            
            if headless:
                chrome_options.add_argument('--headless=new')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--ignore-certificate-errors')
            
            # Determine viewport type
            viewport_type = viewport_size if isinstance(viewport_size, str) else 'desktop'
            user_agent = self.USER_AGENTS.get(viewport_type, self.USER_AGENTS['desktop'])
            chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Get viewport dimensions
            if isinstance(viewport_size, str):
                viewport = self.VIEWPORTS.get(viewport_size, self.VIEWPORTS['desktop'])
            else:
                viewport = viewport_size
            
            chrome_options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')
            
            # Setup driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(30)
            
            return driver, viewport
            
        except Exception as e:
            raise Exception(f"Failed to setup WebDriver: {str(e)}")
    
    def _wait_for_page_load(self, driver, wait_time=3):
        """Wait for page to fully load"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            time.sleep(wait_time)
        except TimeoutException:
            print("Warning: Page load timeout, proceeding anyway...")
    
    def _get_page_height(self, driver):
        """Get total scrollable height of the page"""
        return driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight
            );
        """)
    
    def _capture_viewport_screenshot(self, driver):
        """Capture screenshot of current viewport"""
        screenshot_bytes = driver.get_screenshot_as_png()
        return Image.open(io.BytesIO(screenshot_bytes))

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
        # Get full viewport screenshot
        full_screenshot = self._capture_viewport_screenshot(driver)

        # Get viewport dimensions
        viewport_width = driver.execute_script("return window.innerWidth")

        # Crop to the specific section
        # Box format: (left, top, right, bottom)
        box = (0, section_offset, viewport_width, section_offset + section_height)
        section_image = full_screenshot.crop(box)

        return section_image
    
    def _calculate_ssim_score(self, image1_path, image2_path):
        """Calculate SSIM score between two images"""
        if not CV2_AVAILABLE:
            return None
        
        try:
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                return None
            
            # Resize to same dimensions if different
            if img1.shape != img2.shape:
                height = min(img1.shape[0], img2.shape[0])
                width = min(img1.shape[1], img2.shape[1])
                img1 = cv2.resize(img1, (width, height))
                img2 = cv2.resize(img2, (width, height))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate SSIM
            score, _ = ssim(gray1, gray2, full=True)
            return score
            
        except Exception as e:
            print(f"Error calculating SSIM: {e}")
            return None
    
    def _detect_difference_regions(self, image1_path, image2_path, threshold=30):
        """Detect visual difference regions between two images"""
        if not CV2_AVAILABLE:
            return None
        
        try:
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                return None
            
            # Resize to same dimensions
            if img1.shape != img2.shape:
                height = min(img1.shape[0], img2.shape[0])
                width = min(img1.shape[1], img2.shape[1])
                img1 = cv2.resize(img1, (width, height))
                img2 = cv2.resize(img2, (width, height))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Compute SSIM
            score, diff = ssim(gray1, gray2, full=True)
            diff = (diff * 255).astype("uint8")
            
            # Threshold the difference image
            thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY_INV)[1]
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Collect significant regions
            regions = []
            min_area = 100
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append((x, y, w, h))
            
            return regions if regions else None
            
        except Exception as e:
            print(f"Error detecting differences: {e}")
            return None
    
    def _create_difference_highlight_image(self, image1_path, image2_path, regions):
        """Create side-by-side image with difference regions highlighted"""
        try:
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)
            
            # Resize to same dimensions
            if img1.size != img2.size:
                width = min(img1.width, img2.width)
                height = min(img1.height, img2.height)
                img1 = img1.resize((width, height))
                img2 = img2.resize((width, height))
            
            # Create side-by-side image
            total_width = img1.width + img2.width + 20  # 20px gap
            combined = Image.new('RGB', (total_width, img1.height), 'white')
            combined.paste(img1, (0, 0))
            combined.paste(img2, (img1.width + 20, 0))
            
            # Draw difference regions if available
            if regions:
                draw = ImageDraw.Draw(combined)
                for (x, y, w, h) in regions:
                    # Draw on both images
                    draw.rectangle([x, y, x + w, y + h], outline='red', width=3)
                    draw.rectangle([img1.width + 20 + x, y, img1.width + 20 + x + w, y + h], 
                                 outline='red', width=3)
            
            return combined

        except Exception as e:
            print(f"Error creating highlight image: {e}")
            return None

    def compare_websites_by_viewport(
        self,
        url1: str,
        url2: str,
        viewport_size: str = 'desktop',
        wait_time: int = 3,
        comparison_type: str = 'differences',
        model: str = 'gemini-2.5-flash'
    ) -> Dict[str, Any]:
        """
        Compare two websites viewport-by-viewport

        Args:
            url1: First website URL
            url2: Second website URL
            viewport_size: Viewport preset ('desktop', 'tablet', 'mobile')
            wait_time: Wait time after page load (seconds)
            comparison_type: Type of AI comparison ('general', 'differences', 'similarities', 'detailed')
            model: Gemini model to use

        Returns:
            Dictionary containing comparison results for all viewports
        """
        driver1 = None
        driver2 = None
        temp_files = []

        try:
            # Validate URLs
            if not url1.startswith(('http://', 'https://')):
                url1 = 'https://' + url1
            if not url2.startswith(('http://', 'https://')):
                url2 = 'https://' + url2

            print(f"Setting up browsers for viewport comparison...")

            # Setup drivers for both websites
            driver1, viewport = self._setup_driver(viewport_size, headless=True)
            driver2, _ = self._setup_driver(viewport_size, headless=True)

            viewport_height = viewport['height']
            viewport_width = viewport['width']

            print(f"Loading websites...")
            print(f"  Website 1: {url1}")
            print(f"  Website 2: {url2}")

            # Load both pages
            driver1.get(url1)
            driver2.get(url2)

            # Wait for pages to load
            self._wait_for_page_load(driver1, wait_time)
            self._wait_for_page_load(driver2, wait_time)

            # IMPORTANT: Scroll both pages to the top (position 0) before measuring
            # This ensures we start from the very top of the page
            print(f"Resetting scroll position to top of page...")
            driver1.execute_script("window.scrollTo(0, 0)")
            driver2.execute_script("window.scrollTo(0, 0)")
            time.sleep(0.5)  # Wait for scroll to complete

            # Get page heights
            height1 = self._get_page_height(driver1)
            height2 = self._get_page_height(driver2)
            max_height = max(height1, height2)

            print(f"Page heights: Website 1 = {height1}px, Website 2 = {height2}px")

            # Calculate number of captures needed with 50% overlap strategy
            # This ensures complete page coverage without missing any content
            #
            # Strategy: Each capture scrolls down by HALF the viewport height
            # Example: 2000px page, 600px viewport
            #   - Capture 1: scroll 0px, capture 0-600px
            #   - Capture 2: scroll 300px, capture 300-900px (50% overlap)
            #   - Capture 3: scroll 600px, capture 600-1200px (50% overlap)
            #   - etc.
            #
            # Formula: num_captures = ceil((page_height - viewport_height) / (viewport_height / 2)) + 1

            import math

            scroll_step = viewport_height // 2  # Scroll by half viewport height for 50% overlap

            if max_height <= viewport_height:
                # Page fits in one viewport
                num_captures = 1
            else:
                # Calculate captures needed with 50% overlap
                # We need to cover (max_height - viewport_height) additional pixels
                # Each step covers (viewport_height / 2) new pixels
                num_captures = math.ceil((max_height - viewport_height) / scroll_step) + 1

            print(f"Calculated {num_captures} capture(s) needed to cover {max_height}px of content")
            print(f"Using 50% overlap strategy: scroll step = {scroll_step}px, viewport height = {viewport_height}px")
            print(f"Each viewport will be captured as a FULL screenshot (no section division)")
            print(f"\n{'='*80}")
            print(f"Starting viewport-by-viewport comparison from TOP of page (scroll position 0)")
            print(f"With 50% overlap to ensure complete coverage")
            print(f"{'='*80}")

            # Store viewport comparisons
            viewport_comparisons = []

            # Scroll through and compare each viewport with 50% overlap
            for capture_num in range(num_captures):
                # Calculate scroll position: each capture scrolls by half viewport height
                scroll_position = capture_num * scroll_step

                # Validate that we're not scrolling beyond the actual content
                if scroll_position >= max_height:
                    print(f"\n⚠️  Skipping capture {capture_num + 1} - scroll position {scroll_position}px exceeds page height {max_height}px")
                    break

                # Calculate the bottom of this capture
                capture_bottom = scroll_position + viewport_height

                print(f"\nProcessing capture {capture_num + 1}/{num_captures} (scroll: {scroll_position}px, capturing {scroll_position}-{min(capture_bottom, max_height)}px)...")

                # Show overlap information for captures after the first
                if capture_num > 0:
                    overlap_start = scroll_position
                    overlap_end = (capture_num - 1) * scroll_step + viewport_height
                    if overlap_end > scroll_position:
                        print(f"  📊 50% overlap with previous capture: {overlap_start}-{min(overlap_end, max_height)}px")

                # Scroll both pages to the same position
                # Use smooth: false for instant scrolling to ensure accuracy
                driver1.execute_script(f"window.scrollTo({{top: {scroll_position}, left: 0, behavior: 'instant'}})")
                driver2.execute_script(f"window.scrollTo({{top: {scroll_position}, left: 0, behavior: 'instant'}})")

                # Wait for scroll to settle and any lazy-loaded content to appear
                time.sleep(0.8)  # Increased from 0.5 to ensure content loads

                # Verify actual scroll position (some pages may not scroll to exact position)
                actual_scroll1 = driver1.execute_script("return window.pageYOffset || document.documentElement.scrollTop")
                actual_scroll2 = driver2.execute_script("return window.pageYOffset || document.documentElement.scrollTop")

                if abs(actual_scroll1 - scroll_position) > 10 or abs(actual_scroll2 - scroll_position) > 10:
                    print(f"  ⚠️  Warning: Scroll position mismatch. Expected: {scroll_position}px, Actual: Site1={actual_scroll1}px, Site2={actual_scroll2}px")

                # Capture FULL viewport screenshot (no section division)
                print(f"  Capturing full viewport screenshot...")

                # Capture full viewport screenshots
                screenshot1 = self._capture_viewport_screenshot(driver1)
                screenshot2 = self._capture_viewport_screenshot(driver2)

                # Save screenshots to temporary files
                temp_dir = tempfile.gettempdir()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')

                img1_path = os.path.join(temp_dir, f'viewport1_v{capture_num}_{timestamp}.png')
                img2_path = os.path.join(temp_dir, f'viewport2_v{capture_num}_{timestamp}.png')

                screenshot1.save(img1_path)
                screenshot2.save(img2_path)
                temp_files.extend([img1_path, img2_path])

                # Calculate technical metrics
                ssim_score = self._calculate_ssim_score(img1_path, img2_path)
                difference_regions = self._detect_difference_regions(img1_path, img2_path)

                # Create difference highlight image
                highlight_image = None
                highlight_path = None
                if difference_regions:
                    highlight_image = self._create_difference_highlight_image(
                        img1_path, img2_path, difference_regions
                    )
                    if highlight_image:
                        highlight_path = os.path.join(temp_dir, f'highlight_v{capture_num}_{timestamp}.png')
                        highlight_image.save(highlight_path)
                        temp_files.append(highlight_path)

                # Perform AI comparison if available
                ai_analysis = None
                if self.comparison_tool:
                    try:
                        print(f"  Running AI analysis for capture {capture_num + 1}...")

                        # Create custom prompt for concise bullet point format
                        bullet_prompt = f"""Compare these two website screenshots and provide a CONCISE analysis in bullet point format.
Each bullet point should be ONE LINE ONLY (maximum 100 characters).
Focus on the most important differences or similarities.

Format your response as:
• [Brief observation 1]
• [Brief observation 2]
• [Brief observation 3]

Keep it to 3-5 bullet points maximum. Be specific but concise."""

                        result = self.comparison_tool.compare_images(
                            image1_path=img1_path,
                            image2_path=img2_path,
                            comparison_type=comparison_type,
                            custom_prompt=bullet_prompt,
                            model=model
                        )
                        if result.get('success'):
                            ai_analysis = result.get('analysis')
                    except Exception as e:
                        print(f"  AI analysis failed: {e}")
                        ai_analysis = f"AI analysis unavailable: {str(e)}"

                # Store viewport comparison data
                viewport_data = {
                    'viewport_number': capture_num + 1,
                    'total_viewports': num_captures,
                    'scroll_position': scroll_position,
                    'screenshot1_path': img1_path,
                    'screenshot2_path': img2_path,
                    'highlight_path': highlight_path,
                    'ssim_score': ssim_score,
                    'difference_regions': difference_regions,
                    'num_differences': len(difference_regions) if difference_regions else 0,
                    'ai_analysis': ai_analysis,
                    'viewport_dimensions': {'width': viewport_width, 'height': viewport_height}
                }

                viewport_comparisons.append(viewport_data)

                print(f"  SSIM Score: {ssim_score:.4f}" if ssim_score else "  SSIM Score: N/A")
                print(f"  Differences detected: {viewport_data['num_differences']}")

            # Generate summary
            total_differences = sum(vc['num_differences'] for vc in viewport_comparisons)
            avg_ssim = None
            if CV2_AVAILABLE:
                ssim_scores = [vc['ssim_score'] for vc in viewport_comparisons if vc['ssim_score'] is not None]
                if ssim_scores:
                    avg_ssim = sum(ssim_scores) / len(ssim_scores)

            summary = {
                'url1': url1,
                'url2': url2,
                'viewport_size': viewport_size,
                'viewport_dimensions': {'width': viewport_width, 'height': viewport_height},
                'total_viewports': num_captures,
                'scroll_step': scroll_step,
                'overlap_percentage': 50,
                'page_height1': height1,
                'page_height2': height2,
                'total_differences': total_differences,
                'average_ssim': avg_ssim,
                'comparison_type': comparison_type,
                'model_used': model,
                'timestamp': datetime.now().isoformat()
            }

            return {
                'success': True,
                'summary': summary,
                'viewport_comparisons': viewport_comparisons,
                'temp_files': temp_files
            }

        except Exception as e:
            # Clean up temp files on error
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

            return {
                'success': False,
                'error': str(e),
                'temp_files': []
            }

        finally:
            # Close drivers
            if driver1:
                try:
                    driver1.quit()
                except:
                    pass
            if driver2:
                try:
                    driver2.quit()
                except:
                    pass


"""
Website Screenshot Tool
Captures full-page screenshots of websites using Selenium WebDriver
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io


class WebsiteScreenshotTool:
    """Tool for capturing website screenshots"""

    # Viewport presets
    VIEWPORTS = {
        'desktop': {'width': 1920, 'height': 1080},
        'tablet': {'width': 768, 'height': 1024},
        'mobile': {'width': 375, 'height': 667}
    }

    # User agent strings for different devices
    USER_AGENTS = {
        'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'tablet': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    
    def __init__(self):
        """Initialize the screenshot tool"""
        self.driver = None
    
    def _setup_driver(self, viewport_size='desktop', headless=True):
        """
        Setup Chrome WebDriver with specified options

        Args:
            viewport_size: Viewport preset ('desktop', 'tablet', 'mobile') or dict with width/height
            headless: Run browser in headless mode

        Returns:
            WebDriver instance
        """
        try:
            # Chrome options
            chrome_options = Options()

            if headless:
                chrome_options.add_argument('--headless=new')

            # Additional options for better compatibility
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')

            # Determine viewport type
            viewport_type = viewport_size if isinstance(viewport_size, str) else 'desktop'

            # Set appropriate user agent for the viewport
            user_agent = self.USER_AGENTS.get(viewport_type, self.USER_AGENTS['desktop'])
            chrome_options.add_argument(f'user-agent={user_agent}')

            # Get viewport dimensions
            if isinstance(viewport_size, str):
                viewport = self.VIEWPORTS.get(viewport_size, self.VIEWPORTS['desktop'])
            else:
                viewport = viewport_size

            # Set window size
            chrome_options.add_argument(f'--window-size={viewport["width"]},{viewport["height"]}')

            # For mobile/tablet, add mobile emulation settings
            if viewport_type in ['mobile', 'tablet']:
                mobile_emulation = {
                    "deviceMetrics": {
                        "width": viewport["width"],
                        "height": viewport["height"],
                        "pixelRatio": 2.0 if viewport_type == 'mobile' else 1.0
                    },
                    "userAgent": user_agent
                }
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

            # Setup driver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Set page load timeout
            driver.set_page_load_timeout(30)

            # Store viewport type for later use
            driver.viewport_type = viewport_type

            return driver

        except Exception as e:
            raise Exception(f"Failed to setup WebDriver: {str(e)}")
    
    def _wait_for_page_load(self, driver, wait_time=3):
        """
        Wait for page to fully load
        Enhanced for responsive layouts

        Args:
            driver: WebDriver instance
            wait_time: Additional wait time in seconds after page load
        """
        try:
            # Wait for document ready state
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            # For mobile/tablet, give extra time for responsive CSS to apply
            viewport_type = getattr(driver, 'viewport_type', 'desktop')
            if viewport_type in ['mobile', 'tablet']:
                time.sleep(1)  # Extra time for media queries to apply

            # Additional wait for dynamic content
            time.sleep(wait_time)

            # Wait for any pending animations/transitions
            driver.execute_script("""
                return new Promise((resolve) => {
                    if (document.fonts && document.fonts.ready) {
                        document.fonts.ready.then(() => resolve());
                    } else {
                        resolve();
                    }
                });
            """)

        except TimeoutException:
            print("Warning: Page load timeout, proceeding anyway...")
    
    def _trigger_lazy_loading(self, driver):
        """
        Trigger lazy loading by scrolling through the page

        Args:
            driver: WebDriver instance
        """
        # Get initial page height
        last_height = driver.execute_script("return document.body.scrollHeight")

        # Scroll to bottom in steps to trigger lazy loading
        current_position = 0
        viewport_height = driver.execute_script("return window.innerHeight")

        while current_position < last_height:
            # Scroll down by viewport height
            current_position += viewport_height
            driver.execute_script(f"window.scrollTo(0, {current_position})")
            time.sleep(0.3)  # Wait for lazy content to load

            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height > last_height:
                last_height = new_height

        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(0.5)  # Wait for scroll to complete

    def _get_full_page_screenshot(self, driver):
        """
        Capture full page screenshot by scrolling and stitching
        Enhanced for mobile/tablet responsive layouts

        Args:
            driver: WebDriver instance

        Returns:
            PIL Image object
        """
        # Trigger lazy loading first for mobile/tablet
        viewport_type = getattr(driver, 'viewport_type', 'desktop')
        if viewport_type in ['mobile', 'tablet']:
            self._trigger_lazy_loading(driver)

        # Get page dimensions
        # Use max of body.scrollHeight and documentElement.scrollHeight for better accuracy
        total_height = driver.execute_script("""
            return Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
        """)

        total_width = driver.execute_script("""
            return Math.max(
                document.body.scrollWidth,
                document.documentElement.scrollWidth,
                document.body.offsetWidth,
                document.documentElement.offsetWidth,
                document.body.clientWidth,
                document.documentElement.clientWidth
            );
        """)

        viewport_width = driver.execute_script("return window.innerWidth")
        viewport_height = driver.execute_script("return window.innerHeight")

        # For mobile/tablet, ensure we use the viewport width (not total width)
        if viewport_type in ['mobile', 'tablet']:
            total_width = viewport_width

        # For pages that fit in viewport, just take one screenshot
        if total_height <= viewport_height:
            screenshot = driver.get_screenshot_as_png()
            return Image.open(io.BytesIO(screenshot))

        # Calculate number of scrolls needed
        rectangles = []
        i = 0
        while i < total_height:
            ii = i + viewport_height
            if ii > total_height:
                ii = total_height
            rectangles.append((0, i, viewport_width, ii))
            i = ii

        # Create stitched image
        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None

        for rectangle in rectangles:
            if previous is not None:
                driver.execute_script(f"window.scrollTo({rectangle[0]}, {rectangle[1]})")
                # Longer delay for mobile/tablet to allow responsive content to settle
                delay = 0.4 if viewport_type in ['mobile', 'tablet'] else 0.2
                time.sleep(delay)

            screenshot = driver.get_screenshot_as_png()
            screenshot_image = Image.open(io.BytesIO(screenshot))

            if rectangle[1] + viewport_height > total_height:
                offset = (0, total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            stitched_image.paste(screenshot_image, offset)
            previous = rectangle

        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0)")

        return stitched_image
    
    def capture_screenshot(
        self,
        url,
        save_path,
        viewport_size='desktop',
        full_page=True,
        wait_time=3,
        timeout=30
    ):
        """
        Capture screenshot of a website
        
        Args:
            url: Website URL to capture
            save_path: Path to save the screenshot
            viewport_size: Viewport preset or custom dict
            full_page: Capture full page (True) or viewport only (False)
            wait_time: Wait time in seconds before capturing
            timeout: Maximum time to wait for page load
        
        Returns:
            Tuple (success: bool, error_message: str or None)
        """
        driver = None
        
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Setup driver
            driver = self._setup_driver(viewport_size=viewport_size, headless=True)
            
            # Load page
            print(f"Loading {url}...")
            driver.get(url)
            
            # Wait for page to load
            self._wait_for_page_load(driver, wait_time=wait_time)
            
            # Capture screenshot
            print(f"Capturing screenshot...")
            if full_page:
                screenshot_image = self._get_full_page_screenshot(driver)
            else:
                screenshot = driver.get_screenshot_as_png()
                screenshot_image = Image.open(io.BytesIO(screenshot))
            
            # Save screenshot
            screenshot_image.save(save_path, 'PNG')
            print(f"Screenshot saved to {save_path}")
            
            return True, None
            
        except TimeoutException:
            return False, f"Timeout loading page (>{timeout}s). The website may be slow or unresponsive."
        
        except WebDriverException as e:
            error_msg = str(e)
            if 'net::ERR_NAME_NOT_RESOLVED' in error_msg:
                return False, "Website not found. Please check the URL."
            elif 'net::ERR_CONNECTION_REFUSED' in error_msg:
                return False, "Connection refused. The website may be down."
            elif 'net::ERR_CERT' in error_msg:
                return False, "SSL certificate error. The website may have security issues."
            else:
                return False, f"Browser error: {error_msg[:200]}"
        
        except Exception as e:
            return False, f"Error capturing screenshot: {str(e)}"
        
        finally:
            # Clean up driver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def capture_comparison_screenshots(
        self,
        url1,
        url2,
        save_dir,
        viewport_size='desktop',
        full_page=True,
        wait_time=3
    ):
        """
        Capture screenshots of two websites for comparison
        
        Args:
            url1: First website URL
            url2: Second website URL
            save_dir: Directory to save screenshots
            viewport_size: Viewport preset or custom dict
            full_page: Capture full page or viewport only
            wait_time: Wait time before capturing
        
        Returns:
            Tuple (success: bool, filepath1: str, filepath2: str, error_message: str or None)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate filenames
        filename1 = f"screenshot_{timestamp}_1.png"
        filename2 = f"screenshot_{timestamp}_2.png"
        
        filepath1 = os.path.join(save_dir, filename1)
        filepath2 = os.path.join(save_dir, filename2)
        
        # Capture first screenshot
        success1, error1 = self.capture_screenshot(
            url1, filepath1, viewport_size, full_page, wait_time
        )
        
        if not success1:
            return False, None, None, f"Failed to capture screenshot of first website: {error1}"
        
        # Capture second screenshot
        success2, error2 = self.capture_screenshot(
            url2, filepath2, viewport_size, full_page, wait_time
        )
        
        if not success2:
            # Clean up first screenshot
            if os.path.exists(filepath1):
                os.remove(filepath1)
            return False, None, None, f"Failed to capture screenshot of second website: {error2}"
        
        return True, filepath1, filepath2, None


# Convenience function for single screenshot
def capture_website_screenshot(url, save_path, **kwargs):
    """
    Capture a website screenshot
    
    Args:
        url: Website URL
        save_path: Path to save screenshot
        **kwargs: Additional options (viewport_size, full_page, wait_time)
    
    Returns:
        Tuple (success: bool, error_message: str or None)
    """
    tool = WebsiteScreenshotTool()
    return tool.capture_screenshot(url, save_path, **kwargs)


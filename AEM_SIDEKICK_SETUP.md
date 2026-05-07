# AEM Sidekick Extension Setup Guide

## Overview
This guide will help you set up the AEM Sidekick Chrome extension for use with the Visual QA Tool. This is required for comparing certain AEM-based websites like:
- `https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off`

## Step 1: Download AEM Sidekick Extension

### Option A: Install from Chrome Web Store (Recommended)
1. Open Chrome browser
2. Navigate to the Chrome Web Store
3. Search for "AEM Sidekick" or "Adobe Experience Manager Sidekick"
4. Click "Add to Chrome"
5. Click "Add extension" when prompted

### Option B: Download Extension Files Manually
If you need to load an unpacked extension:

1. Download the AEM Sidekick extension from the official Adobe repository or Chrome Web Store
2. If downloading a `.crx` file, you can use it directly
3. If you have the source code, keep it in an unpacked folder

## Step 2: Get Extension Path

### For Unpacked Extension (Developer Mode)
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked" if you have the source folder
4. Note the extension path, typically something like:
   ```
   C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data\Default\Extensions\extension-id\version
   ```

### For Installed Extension
The extension path is typically:
```
C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\[extension-id]\[version]
```

To find the exact path:
1. Go to `chrome://extensions/`
2. Find "AEM Sidekick" extension
3. Click "Details"
4. The extension ID will be in the URL or under the extension name
5. Navigate to the path above, replacing `[extension-id]` with the actual ID

## Step 3: Configure the Visual QA Tool

When using the Viewport Comparison mode:

1. **Extension Path**: Enter the full path to the extension folder, for example:
   ```
   C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\foobar123\1.0.0
   ```
   OR the path to a `.crx` file:
   ```
   C:\path\to\aem-sidekick.crx
   ```

2. **User Email**: Enter your Adobe email address:
   ```
   dineshkumar@adobe.com
   ```

## Step 4: Running Comparisons with AEM Sidekick

1. Fill in the website URLs in the Viewport Comparison section
2. Enter the Extension Path in the "Chrome Extension Support" section
3. Enter your email (dineshkumar@adobe.com) in the User Email field
4. Click "Compare Images"

### What Happens During Authentication

When you start a comparison with extension support:

1. **Browser Opens in Non-Headless Mode**: Extensions require a visible browser window
2. **Authentication Prompt**: The browser will open and you'll have 60 seconds to:
   - Complete any login prompts
   - Interact with the AEM Sidekick extension if needed
   - Wait for the extension to load and authenticate
   - Complete any 2FA/MFA verification
3. **Automatic Continuation**: After authentication, the tool will automatically proceed with the comparison

## Example Configuration

For the URL: `https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off`

**Viewport Comparison Settings:**
- Website 1 URL: `https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off`
- Website 2 URL: (your comparison URL)
- Extension Path: `C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\[your-extension-id]\[version]`
- User Email: `dineshkumar@adobe.com`

## Troubleshooting

### Extension Not Loading
- **Issue**: Extension doesn't appear in the browser
- **Solution**: 
  - Verify the extension path is correct
  - Check that the extension folder contains a `manifest.json` file
  - Try using the full unpacked extension folder path

### Authentication Timeout
- **Issue**: 60 seconds isn't enough time to authenticate
- **Solution**: 
  - Edit `screenshot_tool.py` and increase the timeout:
    ```python
    time.sleep(120)  # Change from 60 to 120 seconds
    ```

### Browser Opens in Headless Mode
- **Issue**: Extension requires visible browser but it's running headless
- **Solution**: This is automatically handled - when an extension path is provided, headless mode is disabled

### Extension Requires Login Every Time
- **Issue**: Having to log in for each comparison
- **Solution**: 
  - Make sure you're using a persistent Chrome user profile
  - Consider using Chrome's built-in profile manager to save credentials

## Advanced: Using Chrome User Profile

To persist login sessions across comparisons, you can configure Chrome to use a specific user profile:

1. Edit `screenshot_tool.py` or `viewport_comparison_tool.py`
2. Add this to the Chrome options:
   ```python
   chrome_options.add_argument('--user-data-dir=C:\\Users\\dineshkumar\\AppData\\Local\\Google\\Chrome\\User Data')
   chrome_options.add_argument('--profile-directory=Default')
   ```

This will use your default Chrome profile with saved logins.

## Security Notes

- Never share your extension paths or user data directories publicly
- Keep your Adobe credentials secure
- The tool only uses your email for authentication display - it doesn't store credentials
- Consider using a dedicated Chrome profile for automated testing

## Support

If you encounter issues:
1. Check the console output for detailed error messages
2. Verify the extension path is accessible
3. Ensure you have the correct permissions for the AEM sites
4. Contact your Adobe administrator for AEM Sidekick access issues

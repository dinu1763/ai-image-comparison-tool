# Quick Reference: AEM Sidekick Extension Usage

## For the URL Example
```
https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off
```

## Quick Setup Steps

### 1. Find Your Extension Path
```powershell
# Default Chrome extension location
C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\
```

Look for the AEM Sidekick extension folder (each extension has a unique ID).

### 2. Enter in Visual QA Tool

In the Viewport Comparison section, under "Chrome Extension Support":

**Extension Path:**
```
C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\[aem-sidekick-id]\[version]
```

**User Email:**
```
dineshkumar@adobe.com
```

### 3. Run Comparison

1. Enter your URLs:
   - Website 1: Your AEM URL requiring the extension
   - Website 2: Comparison URL

2. Click "Compare Images"

3. **Authentication Window Opens:**
   - Browser window appears (non-headless mode required for extensions)
   - You have **60 seconds** to:
     - Complete any login prompts
     - Verify 2FA/MFA if required
     - Wait for extension to load
   
4. **Automatic Processing:**
   - After 60 seconds, comparison proceeds automatically
   - Screenshots captured with extension active
   - PDF report generated

## Expected Behavior

✅ **What Should Happen:**
- Chrome opens with extension loaded
- You see the AEM Sidekick icon in the toolbar
- Extension may prompt for authentication
- Page loads with extension features enabled
- Comparison completes successfully

❌ **Common Issues:**

| Issue | Solution |
|-------|----------|
| Extension not loading | Verify path is correct, check manifest.json exists |
| Headless mode warning | This is expected - extension mode disables headless |
| Authentication timeout | Increase timeout in `screenshot_tool.py` line ~209 |
| Extension requires login each time | Use Chrome user profile persistence (see advanced guide) |

## Authentication Timeout Adjustment

If 60 seconds isn't enough:

Edit `screenshot_tool.py`:
```python
# Line ~209 in _handle_authentication method
time.sleep(60)  # Change to 120 or more
```

Edit `viewport_comparison_tool.py`:
```python
# Same location in _handle_authentication method  
time.sleep(60)  # Change to 120 or more
```

## Example Full Configuration

```
Website 1 URL:
https://main--da-cc--adobecom.aem.page/products/firefly/features/ai-art-generator?georouting=off

Website 2 URL:
https://www.adobe.com/products/firefly/features/ai-art-generator

Extension Path:
C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\cgkobaafjmhoicoopgjloanmcpjmlnko\1.0.0

User Email:
dineshkumar@adobe.com

Viewport: Desktop (1920x1080)
Analysis Type: Find Differences
Model: Gemini 2.5 Flash
```

## Tips

💡 **Tip 1**: Keep your extension updated for best compatibility

💡 **Tip 2**: Use the same Chrome profile each time to avoid repeated logins

💡 **Tip 3**: If authentication fails, increase timeout or manually login in Chrome beforehand

💡 **Tip 4**: Extensions only work in non-headless mode (browser window visible)

💡 **Tip 5**: For batch comparisons, authentication is only required once for the first URL pair

## Troubleshooting Commands

Check if extension exists:
```powershell
dir "C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\"
```

Check for manifest.json:
```powershell
dir "C:\Users\dineshkumar\AppData\Local\Google\Chrome\User Data\Default\Extensions\[extension-id]\[version]\manifest.json"
```

## Support Files

- **Full Setup Guide**: See `AEM_SIDEKICK_SETUP.md`
- **Main README**: See `README.md`
- **Code Reference**: 
  - `screenshot_tool.py` (lines 32-44, 65-88, 202-225)
  - `viewport_comparison_tool.py` (lines 56-72, 114-164, 195-221, 411-416)

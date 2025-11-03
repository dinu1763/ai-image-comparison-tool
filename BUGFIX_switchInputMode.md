# Bug Fix: switchInputMode is not defined

## Issue

**Error Message:**
```
Uncaught ReferenceError: switchInputMode is not defined
    at HTMLButtonElement.onclick ((index):41:129)
```

**Root Cause:**
The HTML template was using inline `onclick` attributes to call the `switchInputMode()` function. When the page loads, the HTML is parsed and rendered before the external JavaScript file (`script.js`) is fully loaded and executed. This creates a race condition where the buttons try to call a function that doesn't exist yet.

## Solution

Replaced inline `onclick` handlers with proper event listeners that are attached after the DOM is fully loaded.

### Changes Made

#### 1. Updated HTML Template (`templates/index.html`)

**Before:**
```html
<button type="button" class="toggle-btn active" data-mode="upload" onclick="switchInputMode('upload')">
    <i class="fas fa-upload"></i> Upload Files
</button>
<button type="button" class="toggle-btn" data-mode="screenshot" onclick="switchInputMode('screenshot')">
    <i class="fas fa-camera"></i> Website Screenshots
</button>
<button type="button" class="toggle-btn" data-mode="viewport" onclick="switchInputMode('viewport')">
    <i class="fas fa-layer-group"></i> Viewport Comparison
</button>
```

**After:**
```html
<button type="button" class="toggle-btn active" data-mode="upload" id="uploadModeBtn">
    <i class="fas fa-upload"></i> Upload Files
</button>
<button type="button" class="toggle-btn" data-mode="screenshot" id="screenshotModeBtn">
    <i class="fas fa-camera"></i> Website Screenshots
</button>
<button type="button" class="toggle-btn" data-mode="viewport" id="viewportModeBtn">
    <i class="fas fa-layer-group"></i> Viewport Comparison
</button>
```

**Changes:**
- Removed `onclick` attributes
- Added unique `id` attributes to each button

#### 2. Updated JavaScript (`static/js/script.js`)

**Added new function:**
```javascript
// Setup mode toggle buttons
function setupModeButtons() {
    const uploadBtn = document.getElementById('uploadModeBtn');
    const screenshotBtn = document.getElementById('screenshotModeBtn');
    const viewportBtn = document.getElementById('viewportModeBtn');
    
    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            switchInputMode('upload');
        });
    }
    
    if (screenshotBtn) {
        screenshotBtn.addEventListener('click', function() {
            switchInputMode('screenshot');
        });
    }
    
    if (viewportBtn) {
        viewportBtn.addEventListener('click', function() {
            switchInputMode('viewport');
        });
    }
}
```

**Updated DOMContentLoaded:**
```javascript
// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupImageUpload(1);
    setupImageUpload(2);
    setupFormSubmit();
    setupModeButtons();  // ← Added this line
});
```

## Why This Fix Works

1. **Proper Loading Order**: Event listeners are attached only after the DOM is fully loaded and the JavaScript file is executed
2. **No Race Condition**: The `DOMContentLoaded` event ensures all elements exist before we try to attach listeners
3. **Null Safety**: The `if` checks ensure we don't try to attach listeners to non-existent elements
4. **Best Practice**: Using event listeners instead of inline handlers is the modern, recommended approach

## Benefits of This Approach

1. **Separation of Concerns**: HTML structure is separate from JavaScript behavior
2. **Better Maintainability**: All event handling logic is in one place (JavaScript file)
3. **No Global Scope Pollution**: Functions don't need to be in the global scope for inline handlers
4. **CSP Friendly**: Compatible with Content Security Policy that disables inline scripts
5. **Easier Testing**: Event listeners can be easily mocked and tested

## Testing

After applying this fix:

1. Refresh the page (hard refresh: Ctrl+F5 or Cmd+Shift+R)
2. Click on each mode button:
   - "Upload Files" button
   - "Website Screenshots" button
   - "Viewport Comparison" button
3. Verify that:
   - No console errors appear
   - The correct input mode is displayed
   - The active button styling changes correctly

## Related Files

- `templates/index.html` (lines 34-44)
- `static/js/script.js` (lines 9-40)

## Prevention

To prevent similar issues in the future:

1. **Avoid inline event handlers** (`onclick`, `onchange`, etc.)
2. **Use event listeners** attached in JavaScript after DOM is ready
3. **Always check for element existence** before attaching listeners
4. **Keep JavaScript in external files** rather than inline `<script>` tags
5. **Use browser DevTools** to check for JavaScript errors during development


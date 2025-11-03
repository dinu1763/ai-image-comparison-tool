# Test Plan: Screenshot Feature Removal

## Quick Test Script

Run these tests to verify the screenshot feature has been successfully removed and the application still works correctly.

---

## Test 1: Visual Inspection

### Steps:
1. Start the Flask application:
   ```powershell
   python app.py
   ```

2. Open browser to `http://localhost:5000`

3. **Check the mode toggle buttons:**
   - ✅ Should see "Upload Files" button
   - ✅ Should see "Viewport Comparison" button
   - ❌ Should NOT see "Website Screenshots" button

4. **Check Upload mode (default):**
   - ✅ Should see two upload areas
   - ✅ Should see comparison options
   - ✅ Should see "Compare Images" button

5. **Click "Viewport Comparison" button:**
   - ✅ Upload areas should hide
   - ✅ Should see two URL input fields
   - ✅ Should see viewport settings
   - ✅ Should see "Compare Viewports" button

6. **Click "Upload Files" button:**
   - ✅ URL inputs should hide
   - ✅ Upload areas should show
   - ✅ Should see comparison options

---

## Test 2: Console Error Check

### Steps:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Refresh the page (Ctrl+F5 or Cmd+Shift+R)

### Expected Results:
- ✅ No errors about missing elements
- ✅ No errors about `website1Url` or `website2Url`
- ✅ No errors about `screenshotMode`
- ✅ No errors about `screenshotBtn`

### Common Errors to Watch For:
```
❌ Cannot read property 'value' of null (website1Url)
❌ Cannot read property 'style' of null (screenshotMode)
❌ Cannot read property 'addEventListener' of null (screenshotBtn)
```

If you see any of these, there are still references to screenshot elements that need to be removed.

---

## Test 3: Upload Mode Functionality

### Steps:
1. Click "Upload Files" button
2. Upload two test images
3. Select comparison type: "General Comparison"
4. Click "Compare Images"

### Expected Results:
- ✅ Loading indicator appears
- ✅ Comparison completes successfully
- ✅ Results display with AI analysis
- ✅ SSIM score shows
- ✅ Difference count shows
- ✅ Download PDF button works
- ✅ No console errors

---

## Test 4: Viewport Mode Functionality

### Steps:
1. Click "Viewport Comparison" button
2. Enter URL 1: `https://www.adobe.com`
3. Enter URL 2: `https://www.stage.adobe.com`
4. Select viewport: "Desktop (1920x1080)"
5. Click "Compare Viewports"

### Expected Results:
- ✅ Loading indicator appears with viewport message
- ✅ Console shows viewport progress
- ✅ Comparison completes successfully
- ✅ Results display with summary
- ✅ Download PDF button works
- ✅ PDF contains section-by-section comparisons
- ✅ No console errors

---

## Test 5: Mode Switching

### Test 5A: Upload → Viewport
1. Start in Upload mode
2. Upload two images (don't compare yet)
3. Click "Viewport Comparison" button

**Expected:**
- ✅ Upload areas clear
- ✅ Viewport inputs show
- ✅ No console errors

### Test 5B: Viewport → Upload
1. Start in Viewport mode
2. Enter two URLs (don't compare yet)
3. Click "Upload Files" button

**Expected:**
- ✅ URL inputs clear
- ✅ Upload areas show
- ✅ No console errors

### Test 5C: Rapid Switching
1. Click "Upload Files"
2. Click "Viewport Comparison"
3. Click "Upload Files"
4. Click "Viewport Comparison"
5. Repeat 5 times

**Expected:**
- ✅ Modes switch smoothly
- ✅ Active button styling updates
- ✅ No console errors
- ✅ No visual glitches

---

## Test 6: Backend Validation

### Test 6A: Upload Endpoint
```powershell
# Test with curl (if available)
curl -X POST http://localhost:5000/compare \
  -F "image1=@test_image1.png" \
  -F "image2=@test_image2.png" \
  -F "comparison_type=general" \
  -F "model=gemini-2.5-flash"
```

**Expected:**
- ✅ Returns JSON with success: true
- ✅ Contains analysis text
- ✅ Contains SSIM score
- ✅ No errors about screenshot mode

### Test 6B: Viewport Endpoint
```powershell
# Test viewport comparison
curl -X POST http://localhost:5000/compare-viewports \
  -F "website1_url=https://www.adobe.com" \
  -F "website2_url=https://www.stage.adobe.com" \
  -F "viewport_size=desktop"
```

**Expected:**
- ✅ Returns JSON with success: true
- ✅ Contains PDF path
- ✅ Contains summary data
- ✅ No errors

---

## Test 7: Code Verification

### Check for Remaining Screenshot References

Run these searches in your code editor:

#### Search 1: JavaScript
```
Search: "screenshot"
Files: static/js/script.js
```

**Expected Results:**
- ❌ No references to `screenshotMode`
- ❌ No references to `screenshotBtn`
- ❌ No references to `website1Url` or `website2Url`
- ❌ No references to screenshot validation

#### Search 2: HTML
```
Search: "screenshot"
Files: templates/index.html
```

**Expected Results:**
- ❌ No screenshot button
- ❌ No screenshot input container
- ❌ No screenshot settings

#### Search 3: CSS
```
Search: ".screenshot"
Files: static/css/style.css
```

**Expected Results:**
- ❌ No `.screenshot-input-container`
- ❌ No `.screenshot-url-inputs`
- ❌ No `.screenshot-url-group`
- ❌ No `.screenshot-settings`
- ❌ No `.screenshot-info`

#### Search 4: Python
```
Search: "screenshot"
Files: app.py
```

**Expected Results:**
- ✅ Import is commented out: `# from screenshot_tool import WebsiteScreenshotTool`
- ✅ Screenshot handling is commented out or removed
- ❌ No active screenshot mode logic

---

## Test 8: Edge Cases

### Test 8A: Direct URL Access
1. Navigate to `http://localhost:5000`
2. Check URL parameters (should be none)
3. Verify default mode is "Upload Files"

**Expected:**
- ✅ Upload mode is active by default
- ✅ No errors in console

### Test 8B: Browser Back/Forward
1. Start in Upload mode
2. Switch to Viewport mode
3. Click browser back button
4. Click browser forward button

**Expected:**
- ✅ Mode doesn't change (no history navigation)
- ✅ No console errors

### Test 8C: Form Submission Without Selection
1. Click "Upload Files"
2. Don't upload any images
3. Click "Compare Images"

**Expected:**
- ✅ Alert: "Please select both images"
- ✅ No form submission
- ✅ No console errors

---

## Test 9: Performance Check

### Metrics to Verify:

1. **Page Load Time:**
   - Open DevTools → Network tab
   - Refresh page
   - Check total load time
   - ✅ Should be faster than before (less CSS/JS)

2. **JavaScript File Size:**
   - Check `script.js` size
   - ✅ Should be smaller (~30 lines removed)

3. **CSS File Size:**
   - Check `style.css` size
   - ✅ Should be smaller (~95 lines removed)

4. **Memory Usage:**
   - Open DevTools → Performance Monitor
   - ✅ Should be slightly lower (fewer DOM elements)

---

## Test 10: Accessibility Check

### Steps:
1. Use keyboard navigation only (Tab key)
2. Tab through all interactive elements

**Expected Tab Order:**
1. ✅ "Upload Files" button
2. ✅ "Viewport Comparison" button
3. ✅ Upload area 1 (or URL input 1)
4. ✅ Upload area 2 (or URL input 2)
5. ✅ Comparison type dropdown
6. ✅ Model selector
7. ✅ "Compare Images" button

**Should NOT tab to:**
- ❌ Screenshot mode button
- ❌ Screenshot URL inputs
- ❌ Screenshot settings

---

## Automated Test Script

Create a simple test file `test_removal.py`:

```python
import requests
import os

def test_upload_mode():
    """Test that upload mode still works"""
    url = 'http://localhost:5000/compare'
    
    # Create test files
    with open('test1.png', 'rb') as f1, open('test2.png', 'rb') as f2:
        files = {
            'image1': f1,
            'image2': f2
        }
        data = {
            'comparison_type': 'general',
            'model': 'gemini-2.5-flash'
        }
        
        response = requests.post(url, files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result['success'] == True
        print("✅ Upload mode test passed")

def test_viewport_mode():
    """Test that viewport mode still works"""
    url = 'http://localhost:5000/compare-viewports'
    
    data = {
        'website1_url': 'https://www.adobe.com',
        'website2_url': 'https://www.stage.adobe.com',
        'viewport_size': 'desktop'
    }
    
    response = requests.post(url, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result['success'] == True
    print("✅ Viewport mode test passed")

if __name__ == '__main__':
    print("Running screenshot removal tests...")
    test_upload_mode()
    test_viewport_mode()
    print("\n✅ All tests passed!")
```

---

## Success Criteria

All tests should pass with these results:

- ✅ No screenshot button visible
- ✅ No screenshot input fields visible
- ✅ No console errors
- ✅ Upload mode works correctly
- ✅ Viewport mode works correctly
- ✅ Mode switching works smoothly
- ✅ No references to screenshot in active code
- ✅ Backend handles upload mode correctly
- ✅ Backend handles viewport mode correctly
- ✅ PDF generation works for both modes

---

## Troubleshooting

### Issue: Screenshot button still appears
**Solution:** Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)

### Issue: Console error about website1Url
**Solution:** Check `static/js/script.js` for remaining references

### Issue: Console error about screenshotMode
**Solution:** Check `static/js/script.js` switchInputMode() function

### Issue: Backend error about WebsiteScreenshotTool
**Solution:** Verify import is commented out in `app.py`

### Issue: Styles look wrong
**Solution:** Clear browser cache and hard refresh

---

## Rollback Plan

If tests fail and you need to rollback:

1. Use git to revert changes:
   ```bash
   git checkout HEAD -- templates/index.html
   git checkout HEAD -- static/js/script.js
   git checkout HEAD -- static/css/style.css
   git checkout HEAD -- app.py
   ```

2. Or manually restore from `REMOVAL_screenshot_feature.md` documentation

---

## Final Checklist

Before marking as complete:

- [ ] All visual tests pass
- [ ] No console errors
- [ ] Upload mode works
- [ ] Viewport mode works
- [ ] Mode switching works
- [ ] Backend tests pass
- [ ] Code searches show no active screenshot references
- [ ] Performance is same or better
- [ ] Accessibility is maintained
- [ ] Documentation is updated

**Status:** Ready for production ✅


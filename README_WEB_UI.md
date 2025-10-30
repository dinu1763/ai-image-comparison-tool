# Image Comparison Tool - Web UI

A beautiful, modern web interface for the AI-powered Image Comparison Tool using Google Gemini.

## 🎨 Features

- **Drag & Drop Upload** - Easy image uploading with drag and drop support
- **Live Preview** - See your images before comparison
- **Multiple Comparison Types** - General, Differences, Similarities, Detailed
- **Custom Prompts** - Ask specific questions about your images
- **Model Selection** - Choose between different Gemini models
- **Beautiful UI** - Modern, responsive design with gradient backgrounds
- **Download Results** - Export comparison results as JSON
- **Real-time Analysis** - See AI analysis in real-time

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-generativeai` - Google Gemini API
- `Pillow` - Image processing
- `Flask` - Web framework
- `Werkzeug` - WSGI utilities

### 2. Set Your API Key

```bash
# Windows
set GEMINI_API_KEY=AIzaSyDIO_8C7YMWjXMbpPzemtjTOqeWH9UGT_A

# Linux/Mac
export GEMINI_API_KEY=AIzaSyDIO_8C7YMWjXMbpPzemtjTOqeWH9UGT_A
```

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## 📖 How to Use

1. **Upload Images**
   - Click or drag and drop your first image
   - Click or drag and drop your second image
   - Supported formats: PNG, JPG, JPEG, GIF, BMP, WEBP
   - Max file size: 16MB per image

2. **Choose Options**
   - **Comparison Type**: Select what kind of analysis you want
     - General: Overall comparison
     - Differences: Focus on what's different
     - Similarities: Focus on what's similar
     - Detailed: Comprehensive analysis
   
   - **AI Model**: Choose the Gemini model
     - Gemini 2.5 Flash: Fast and efficient (recommended)
     - Gemini 2.5 Pro: Most capable, best quality
     - Gemini 2.0 Flash: Alternative fast model

3. **Custom Prompt (Optional)**
   - Enter specific questions or instructions
   - Example: "Which image has better lighting?"
   - Example: "Compare the color schemes"

4. **Compare**
   - Click "Compare Images" button
   - Wait for AI analysis (usually 5-15 seconds)
   - View detailed results

5. **Download Results**
   - Click "Download JSON" to save the analysis
   - Results include full analysis and metadata

## 🎯 Use Cases

### Product Photography
Compare different product shots to choose the best one for your e-commerce site.

### Design Review
Compare design iterations to track changes and improvements.

### Quality Assurance
Compare original vs processed images to check for quality loss.

### A/B Testing
Compare different versions of marketing materials.

### Before/After
Document changes, renovations, or transformations.

## 📁 Project Structure

```
llm/
├── app.py                      # Flask web application
├── image_comparison_tool.py    # Core comparison logic
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css          # Styles
│   └── js/
│       └── script.js          # JavaScript functionality
└── uploads/                    # Uploaded images (auto-created)
```

## 🎨 UI Features

### Responsive Design
- Works on desktop, tablet, and mobile
- Adaptive layout for different screen sizes

### Modern Interface
- Gradient backgrounds
- Smooth animations
- Icon-based navigation
- Clean, professional look

### User Experience
- Drag and drop support
- Image previews
- Loading indicators
- Error handling
- Smooth scrolling to results

## ⚙️ Configuration

### Change Port
Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change port here
```

### Change Upload Folder
Edit `app.py`:
```python
UPLOAD_FOLDER = 'uploads'  # Change folder name
```

### Change Max File Size
Edit `app.py`:
```python
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB (change as needed)
```

## 🔧 API Endpoints

### `GET /`
Returns the main HTML page

### `POST /compare`
Compares two images

**Request:**
- Form data with `image1`, `image2` files
- Optional: `comparison_type`, `custom_prompt`, `model`

**Response:**
```json
{
  "success": true,
  "analysis": "...",
  "model_used": "gemini-2.5-flash",
  "tokens_used": {
    "prompt": 1250,
    "completion": 450,
    "total": 1700
  }
}
```

### `GET /models`
Returns available models

### `GET /health`
Health check endpoint

## 🐛 Troubleshooting

### "API key not configured" error
- Make sure `GEMINI_API_KEY` environment variable is set
- Restart the application after setting the variable

### Images not uploading
- Check file size (must be < 16MB)
- Check file format (PNG, JPG, JPEG, GIF, BMP, WEBP)
- Check browser console for errors

### Server not starting
- Make sure port 5000 is not in use
- Check if Flask is installed: `pip list | grep Flask`
- Try running with: `python -m flask run`

### Slow analysis
- Use `gemini-2.5-flash` for faster results
- Check your internet connection
- Large images take longer to process

## 🌐 Deployment

### Local Network Access
Change host in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```
Access from other devices: `http://YOUR_IP:5000`

### Production Deployment
For production, use a proper WSGI server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Performance Tips

1. **Use Flash models** for faster results
2. **Resize large images** before uploading
3. **Use specific prompts** for focused analysis
4. **Monitor token usage** to manage costs

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement rate limiting for production
- Add authentication for public deployments
- Validate and sanitize all user inputs

## 📝 License

MIT License - Free to use for personal and commercial projects

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📧 Support

For issues or questions, please check:
- Google Gemini API documentation
- Flask documentation
- This README file

---

**Enjoy comparing images with AI! 🎉**


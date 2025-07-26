# AI4med Data Preprocessing Label Tool

A simple, LabelMe-like annotation tool for AI4med data preprocessing with an intuitive GUI interface. This tool allows users to easily annotate medical images by clicking to place 600×600 pixel rectangular regions.

## Features

- **Simple GUI Interface**: LabelMe-like interface that's easy to use
- **Click-to-Annotate**: Simply click on the image to place a 600×600 pixel rectangular annotation
- **Automatic Window Sizing**: Adapts to your screen resolution for optimal viewing
- **Scroll Support**: Automatically shows horizontal/vertical scrollbars for large images
- **JSON Export**: Saves annotations in LabelMe-compatible JSON format
- **Image Support**: Supports common image formats (PNG, JPG, JPEG, BMP, TIF, TIFF)

## Installation

### Prerequisites
- Python 3.6 or higher
- PyQt5

### Setup
```bash
# Install PyQt5
pip install pyqt5
```

## Usage

### Basic Usage
```bash
# Start the tool and select an image through the GUI
python main.py

# Or directly load an image
python main.py path/to/your/image.png
```

### How to Use

1. **Open an Image**: Click the "打开图片 (Open)" button to select an image file
2. **Annotate**: Click anywhere on the image to place a 600×600 pixel rectangular annotation
3. **Save**: Click "保存标签 (Save)" to export the annotation as a JSON file

### Annotation Format

The tool exports annotations in LabelMe-compatible JSON format:

```json
{
  "version": "5.8.3",
  "flags": {},
  "shapes": [
    {
      "label": "d",
      "points": [[x1, y1], [x2, y2]],
      "group_id": null,
      "description": "",
      "shape_type": "rectangle",
      "flags": {},
      "mask": null
    }
  ],
  "imagePath": "image_name.jpg",
  "imageData": "base64_encoded_image_data",
  "imageHeight": 1080,
  "imageWidth": 1920
}
```

## Key Features

- **Automatic Resolution Adaptation**: The window automatically adjusts to your screen size
- **Scroll Support**: Large images automatically get scrollbars for easy navigation
- **Real-time Drawing**: Annotations are drawn immediately when you click
- **Boundary Clipping**: Rectangles are automatically clipped to image boundaries
- **Base64 Image Encoding**: Images are embedded in the JSON for complete annotation files

## File Structure

```
labelPZY/
├── main.py          # Main application file
├── .gitignore       # Git ignore rules (only tracks main.py)
└── d/              # Output directory for JSON files
    └── *.json      # Generated annotation files
```

## Dependencies

- **PyQt5**: For the GUI interface
- **pathlib**: For file path handling
- **json**: For JSON export
- **base64**: For image encoding

## Development

This tool was developed for AI4med data preprocessing workflows, providing a simple and efficient way to annotate medical images for machine learning training.

### Recent Updates
- Added "Open Image" button functionality
- Automatic resolution adaptation
- Horizontal/vertical scrollbar support for large images
- Improved button layout

## License

This tool is designed for AI4med data preprocessing workflows.

## Contributing

Feel free to submit issues and enhancement requests for this medical image annotation tool. 
# Computer Vision Analytics

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?logo=numpy&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> Computer Vision analysis tools and scripts focused on image processing and calibration using Python and OpenCV.

## Table of Contents

- [About the Project](#about-the-project)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## About the Project

**Computer Vision Analytics** is a Python-based project designed for computer vision tasks. It provides modular scripts for core image processing and color/space calibration (e.g., HSV), facilitating data extraction, image analysis, and color-based object detection.

## Repository Structure

```text
Computer-Vision-Analytics-main/
├── calibration.py          # Script focused on image and mask calibration (e.g., HSV calibration)
├── computer_vision_main.py # Main script that executes the core computer vision routine
├── grass_img.jpg           # Sample/test image used by the scripts
├── requirements.txt        # Project dependencies (numpy, opencv-python, deepmerge)
└── .gitignore              # Files and directories ignored by Git
```

## Prerequisites

Ensure you have the following installed on your system:
* [Python 3.8+](https://www.python.org/downloads/)
* Pip (Python package installer)
* Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/brayanwisller/Computer-Vision-Analytics.git
cd Computer-Vision-Analytics
```

2. (Optional) Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The project offers two main execution paths:

### 1. Calibration
To configure computer vision parameters (such as finding optimal color values), run the calibration script:
```bash
python calibration.py
```
*Note: You can use the provided `grass_img.jpg` to test green/grass filters and calibrations.*

### 2. Main Execution
To run the complete computer vision analysis with the established parameters, execute:
```bash
python computer_vision_main.py
```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/news`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/news`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
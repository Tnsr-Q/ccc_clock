
Installation Guide
==================

System Requirements
-------------------

* Python 3.9 or higher
* NumPy, SciPy, Matplotlib
* Plotly, Dash (for dashboard)
* FFmpeg (for animation generation)
* Jupyter (for analysis notebooks)

Installation Steps
------------------

1. Clone the repository::

    git clone https://github.com/username/ccc-clock.git
    cd ccc-clock

2. Install in development mode::

    pip install -e .

3. Install dependencies::

    pip install -r requirements.txt

4. Install optional dependencies for full functionality::

    pip install plotly dash websockets matplotlib ffmpeg-python

5. Verify installation::

    pytest tests/

Development Environment
-----------------------

For development, we recommend using the provided devcontainer configuration:

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Use "Reopen in Container" command
4. The environment will be automatically configured

Docker Setup
------------

Alternatively, you can use Docker directly::

    docker build -t ccc-clock .
    docker run -p 8050:8050 ccc-clock

This will start the dashboard on port 8050.

Troubleshooting
---------------

**FFmpeg Issues**
If animation generation fails, install FFmpeg::

    # Ubuntu/Debian
    sudo apt-get install ffmpeg
    
    # macOS
    brew install ffmpeg
    
    # Windows
    # Download from https://ffmpeg.org/

**Dashboard Not Loading**
Ensure all dashboard dependencies are installed::

    pip install plotly dash websockets

**Test Failures**
Run tests with verbose output to diagnose issues::

    pytest tests/ -v --tb=short

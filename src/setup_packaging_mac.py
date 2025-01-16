#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import platform

def check_system_dependencies():
    """Check and guide system dependency installation"""
    dependencies = {
        'tkinter': {
            'darwin': 'python3-tk (Install via brew: brew install python-tk)',
            'linux': {
                'ubuntu': 'python3-tk',
                'fedora': 'python3-tkinter'
            }
        },
        'venv': {
            'darwin': 'python3-venv (Install via brew: brew install python)',
            'linux': {
                'ubuntu': 'python3.12-venv',
                'fedora': 'python3-virtualenv'
            }
        }
    }

    def get_system_info():
        system = platform.system().lower()
        if system == 'linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('ID='):
                            return system, line.split('=')[1].strip().lower()
            except:
                pass
        return system, None

    system, dist = get_system_info()
    print(f"Detected system: {system.title()}{f' ({dist})' if dist else ''}")

    # Check Tkinter
    try:
        import tkinter
    except ImportError:
        print("\n!!! Tkinter not found !!!")
        if system == 'darwin':
            print("Install with: brew install python-tk")
            print("You may need to install Homebrew first: https://brew.sh")
        elif system == 'linux':
            if dist == 'ubuntu':
                print(f"Install with: sudo apt-get install {dependencies['tkinter']['linux']['ubuntu']}")
            elif dist == 'fedora':
                print(f"Install with: sudo dnf install {dependencies['tkinter']['linux']['fedora']}")
        input("Press Enter after installing Tkinter...")

    # Attempt virtual environment creation methods
    methods = [
        lambda: subprocess.check_call([sys.executable, '-m', 'venv', 'pimd_sim_venv']),
        lambda: subprocess.check_call(['virtualenv', '-p', sys.executable, 'pimd_sim_venv']),
        lambda: subprocess.check_call([sys.executable, '-m', 'virtualenv', 'pimd_sim_venv'])
    ]

    print("\nAttempting to create virtual environment...")
    for method in methods:
        try:
            method()
            print("Virtual environment created successfully!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    print("\n!!! Failed to create virtual environment !!!")
    if system == 'darwin':
        print("1. Install Python with venv: brew install python")
        print("2. Install virtualenv: pip3 install virtualenv")
    elif system == 'linux':
        if dist == 'ubuntu':
            print(f"1. Install venv: sudo apt-get install {dependencies['venv']['linux']['ubuntu']}")
        elif dist == 'fedora':
            print(f"1. Install venv: sudo dnf install {dependencies['venv']['linux']['fedora']}")
    
    print("\nAfter installing, try:")
    print("1. python3 -m venv pimd_sim_venv")
    print("   OR")
    print("2. virtualenv pimd_sim_venv")
    
    return False

def install_dependencies_in_venv():
    """Install Python dependencies in the virtual environment"""
    # Adjust paths based on platform
    is_windows = platform.system().lower() == 'windows'
    venv_path = 'pimd_sim_venv'
    bin_dir = 'Scripts' if is_windows else 'bin'
    pip_path = os.path.join(venv_path, bin_dir, 'pip')
    python_path = os.path.join(venv_path, bin_dir, 'python')

    # Add .exe extension on Windows
    if is_windows:
        pip_path += '.exe'
        python_path += '.exe'

    dependencies = [
        'numpy',
        'scipy',
        'i-pi',
        'pyinstaller',
        'lammps'
    ]

    try:
        # Upgrade pip
        subprocess.check_call([pip_path, 'install', '--upgrade', 'pip'])
        
        # Install dependencies
        subprocess.check_call([pip_path, 'install'] + dependencies)
        
        return python_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        print("Try these steps:")
        activate_cmd = f"source {venv_path}/{bin_dir}/activate" if not is_windows else f"{venv_path}\\Scripts\\activate"
        print(f"1. Activate the virtual environment: {activate_cmd}")
        print(f"2. Install dependencies: pip install {' '.join(dependencies)}")
        sys.exit(1)

def create_run_script():
    """Create platform-specific run script"""
    is_windows = platform.system().lower() == 'windows'
    
    if is_windows:
        script_name = '../run_pimd_simulation.bat'
        script_content = f"""@echo off
cd %~dp0
cd src
.\\pimd_sim_venv\\Scripts\\activate && python water_pimd_gui.py
"""
    else:
        script_name = '../run_pimd_simulation.sh'
        script_content = """#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$SCRIPT_DIR/src/pimd_sim_venv"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the PIMD simulation application
cd "$SCRIPT_DIR/src"
python water_pimd_gui.py

# Deactivate virtual environment
deactivate
"""

    with open(script_name, 'w') as f:
        f.write(script_content)
    
    # Make the script executable on Unix-like systems
    if not is_windows:
        os.chmod(script_name, 0o755)

def create_requirements_file():
    """Create a comprehensive requirements file"""
    requirements_content = """# Core dependencies
numpy
scipy
i-pi
pyinstaller
lammps

# System dependencies
# macOS (via Homebrew):
# brew install python-tk
#
# Linux:
# - python3-tk (Debian/Ubuntu)
# - python3-tkinter (Fedora)
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)

def create_readme():
    """Create a comprehensive README file"""
    readme_content = """# PIMD Water Molecule Simulation Tool

## Prerequisites

### System Dependencies
- Python 3.10+
- Tkinter
- Virtual environment support

### Installation Steps

1. Install System Dependencies

   **macOS:**
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python and Tkinter
   brew install python python-tk
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-tk python3.12-venv
   ```

   **Linux (Fedora):**
   ```bash
   sudo dnf install python3-tkinter python3-virtualenv
   ```

2. Create Virtual Environment and Install Dependencies
   ```bash
   # Create virtual environment
   python3 -m venv pimd_sim_venv

   # Activate virtual environment
   source pimd_sim_venv/bin/activate  # Unix/macOS
   ./pimd_sim_venv/Scripts/activate   # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

## Running the Application

### Unix-like Systems (macOS/Linux)
```bash
./run_pimd_simulation.sh
```

### Windows
```batch
run_pimd_simulation.bat
```

### Manual Activation
```bash
# Activate virtual environment
source pimd_sim_venv/bin/activate      # Unix/macOS
./pimd_sim_venv/Scripts/activate       # Windows

# Run the application
python water_pimd_gui.py

# Deactivate when done
deactivate
```

## Creating Executable
```bash
# Activate virtual environment
source pimd_sim_venv/bin/activate      # Unix/macOS
./pimd_sim_venv/Scripts/activate       # Windows

# Create executable
pyinstaller --onedir --windowed water_pimd_gui.py
```

## Troubleshooting
- Ensure all system dependencies are installed
- Verify virtual environment activation
- Check Python package versions
- On macOS, if Tkinter issues persist:
  - Try reinstalling Python: brew reinstall python
  - Verify Tkinter installation: python3 -m tkinter

## Contact
Created by Ouail Zakary (ouail.zakary@oulu.fi)
"""
    with open('README.md', 'w') as f:
        f.write(readme_content)

def main():
    print("Starting PIMD Simulation Tool Packaging Process")
    
    # Check and install system dependencies
    if not check_system_dependencies():
        print("Failed to set up virtual environment. Please follow the troubleshooting steps.")
        sys.exit(1)
    
    # Install dependencies in virtual environment
    install_dependencies_in_venv()
    
    # Create supporting files
    create_requirements_file()
    create_readme()
    create_run_script()
    
    # Print final instructions
    print("\n--- Setup Complete ---")
    print(f"Virtual Environment: {os.path.abspath('pimd_sim_venv')}")
    print("To run the application:")
    print("1. cd ../")
    if platform.system().lower() == 'windows':
        print("2. run_pimd_simulation.bat")
    else:
        print("2. Make the .sh file executable: chmod +x run_pimd_simulation.sh")
        print("3. Run: ./run_pimd_simulation.sh")

if __name__ == '__main__':
    main()

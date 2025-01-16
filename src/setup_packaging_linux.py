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
            'ubuntu': 'python3-tk',
            'fedora': 'python3-tkinter',
            'default': 'Consult your distribution\'s package manager'
        },
        'venv': {
            'ubuntu': 'python3.12-venv',
            'fedora': 'python3-virtualenv',
            'default': 'python3-venv or python3-virtualenv'
        }
    }

    def get_distribution():
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.split('=')[1].strip().lower()
        except:
            return 'unknown'

    dist = get_distribution()
    print("Checking system dependencies...")

    # Check Tkinter
    try:
        import tkinter
    except ImportError:
        print("\n!!! Tkinter not found !!!")
        if dist == 'ubuntu':
            print(f"Install with: sudo apt-get install {dependencies['tkinter']['ubuntu']}")
        elif dist == 'fedora':
            print(f"Install with: sudo dnf install {dependencies['tkinter']['fedora']}")
        else:
            print(f"Install Tkinter: {dependencies['tkinter']['default']}")
        input("Press Enter after installing Tkinter...")

    # Attempt alternative virtual environment creation methods
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
    print("Possible solutions:")
    if dist == 'ubuntu':
        print(f"1. Install venv: sudo apt-get install {dependencies['venv']['ubuntu']}")
    elif dist == 'fedora':
        print(f"1. Install venv: sudo dnf install {dependencies['venv']['fedora']}")
    
    print("2. Install virtualenv: pip install virtualenv")
    print("3. Manually create virtual environment:")
    print("   python3 -m venv pimd_sim_venv")
    
    return False

def install_dependencies_in_venv():
    """Install Python dependencies in the virtual environment"""
    # Paths for virtual environment
    venv_path = 'pimd_sim_venv'
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    python_path = os.path.join(venv_path, 'bin', 'python')

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
        print(f"1. Activate the virtual environment: source {venv_path}/bin/activate")
        print(f"2. Install dependencies: pip install {' '.join(dependencies)}")
        sys.exit(1)

def create_run_script():
    """Create a run script for the application"""
    run_script_content = """#!/bin/bash
# Activate virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$SCRIPT_DIR/src/pimd_sim_venv"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Run the PIMD simulation application
cd src
python water_pimd_gui.py

# Deactivate virtual environment
deactivate
"""
    with open('../run_pimd_simulation.sh', 'w') as f:
        f.write(run_script_content)
    
    # Make the script executable
    os.chmod('../run_pimd_simulation.sh', 0o755)

def create_requirements_file():
    """Create a comprehensive requirements file"""
    requirements_content = """# Core dependencies
numpy
scipy
i-pi
pyinstaller
lammps

# System dependencies (install via package manager)
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
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-tk python3.12-venv

   # Fedora
   sudo dnf install python3-tkinter python3-virtualenv
   ```

2. Create Virtual Environment and Install Dependencies
   ```bash
   # Create virtual environment
   python3 -m venv pimd_sim_venv

   # Activate virtual environment
   source pimd_sim_venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Using Run Script
```bash
./run_pimd_simulation.sh
```

### Option 2: Manual Activation
```bash
# Activate virtual environment
source pimd_sim_venv/bin/activate

# Run the application
python water_pimd_gui.py

# Deactivate when done
deactivate
```

## Creating Executable
```bash
# Activate virtual environment
source pimd_sim_venv/bin/activate

# Create executable
pyinstaller --onedir --windowed water_pimd_gui.py
```

## Troubleshooting
- Ensure all system dependencies are installed
- Verify virtual environment activation
- Check Python package versions

## Contact
Created by Ouail Zakary (ouail.zakary@oulu.fi)
"""
    with open('README.md', 'w') as f:
        f.write(readme_content)

def create_spec_file():
    """Create PyInstaller spec file with robust configuration"""
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# Determine the project root directory
root_dir = os.path.abspath(os.path.dirname('{os.path.abspath(__file__)}'))

# Define additional hidden imports
additional_hidden_imports = [
    'numpy',
    'scipy',
    'tkinter',
    'lammps',
    'i-pi',
    'ipi.engine.simulation',
]

# Data files to include
additional_datas = [
    ('run_ipi.py', '.'),
    ('run_lammps.py', '.'),
]

a = Analysis(
    ['water_pimd_gui.py'],
    pathex=[root_dir],
    binaries=[],
    datas=additional_datas,
    hiddenimports=additional_hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PIMD_Water_Simulation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='PIMD_Water_Simulation'
)
"""
    with open('pimd_water_sim.spec', 'w') as f:
        f.write(spec_content)

def build_application():
    """Build the application using PyInstaller in virtual environment"""
    pyinstaller_path = os.path.join('pimd_sim_venv', 'bin', 'pyinstaller')
    
    try:
        # Prepare build command
        build_command = [
            pyinstaller_path, 
            '--onedir',      # Create a directory with executable and dependencies
            '--windowed',    # No console window
            'pimd_water_sim.spec'  # Use the spec file for more control
        ]
        
        # Run PyInstaller
        result = subprocess.run(
            build_command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        print("Application successfully built!")
        print("Executable can be found in the 'dist' directory")
        print("\nBuild Output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("PyInstaller build failed:")
        print(e.stderr)
    except Exception as e:
        print(f"Unexpected error during build: {e}")
        import traceback
        traceback.print_exc()

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
    create_spec_file()
    
    # Build the application
    build_application()
    
    # Print final instructions
    print("\n--- Setup Complete ---")
    print(f"Virtual Environment: {os.path.abspath('pimd_sim_venv')}")
    print("To run the application:")
    print("1. cd ../")
    print("2. Make the .sh file executable if it isn't already : chmod +x run_pimd_simulation.sh")
    print("3. Run: ./run_pimd_simulation.sh")

if __name__ == '__main__':
    main()

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

    system = platform.system().lower()
    print(f"Detected system: {system.title()}")

    # Check Tkinter
    try:
        import tkinter
    except ImportError:
        print("\n!!! Tkinter not found !!!")
        if system == 'darwin':
            print("Install with: brew install python-tk")
            print("You may need to install Homebrew first: https://brew.sh")
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
    
    print("\nAfter installing, try:")
    print("1. python3 -m venv pimd_sim_venv")
    print("   OR")
    print("2. virtualenv pimd_sim_venv")
    
    return False

def install_dependencies_in_venv():
    """Install Python dependencies in the virtual environment and register IPython kernel"""
    # Paths for virtual environment
    venv_path = 'pimd_sim_venv'
    pip_path = os.path.join(venv_path, 'bin', 'pip')
    python_path = os.path.join(venv_path, 'bin', 'python')
    dependencies = [
        'numpy',
        'matplotlib',
        'pandas',
        'plotly',
        'jupyter',
        'notebook',
        'ipykernel',
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
        
        # Activate virtual environment before registering kernel
        activate_script = os.path.join(venv_path, 'bin', 'activate')
        activate_cmd = f'source {activate_script} && {python_path} -m ipykernel install --user --name=jupyter_env --display-name="Python (jupyter_env)"'
        
        # Use shell=True to properly source the activate script
        subprocess.check_call(activate_cmd, shell=True)
        
        return python_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies or register kernel: {e}")
        print("Try these steps manually:")
        print(f"1. Activate the virtual environment: source {venv_path}/bin/activate")
        print(f"2. Install dependencies: pip install {' '.join(dependencies)}")
        print("3. Register kernel: python -m ipykernel install --user --name=jupyter_env --display-name=\"Python (jupyter_env)\"")
        sys.exit(1)

def create_run_script():
    """Create platform-specific run script"""
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
    
    # Make the script executable
    os.chmod(script_name, 0o755)

def create_requirements_file():
    """Create a comprehensive requirements file"""
    requirements_content = """# Core dependencies
numpy
matplotlib
pandas
scipy
plotly
jupyter
notebook
ipykernel
i-pi
pyinstaller
lammps

# System dependencies
# macOS (via Homebrew):
# brew install python-tk
"""
    with open('requirements.txt', 'w') as f:
        f.write(requirements_content)

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
    'matplotlib',
    'pandas',
    'scipy',
    'plotly',
    'jupyter',
    'notebook',
    'ipykernel',
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
        # Simplified build command - just use the spec file
        build_command = [
            pyinstaller_path,
            'pimd_water_sim.spec'  # Use the spec file only
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
    create_run_script()
    create_spec_file()
    
    # Build the application
    build_application()
    
    # Print final instructions
    print("\n--- Setup Complete ---")
    print(f"Virtual Environment: {os.path.abspath('pimd_sim_venv')}")
    print("To run the application:")
    print("1. cd ../")
    print("2. Make the .sh file executable: chmod +x run_pimd_simulation.sh")
    print("3. Run: ./run_pimd_simulation.sh")

if __name__ == '__main__':
    main()

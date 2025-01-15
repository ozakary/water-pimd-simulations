# PIMD Water Molecule Simulation Tool

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

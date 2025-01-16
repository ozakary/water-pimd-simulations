# Water Path Integral Molecular Dynamics (PIMD) Simulation Tool

![Graphical Abstract](./image.png)

**Author:** Ouail Zakary  
**ORCID:** [0000-0002-7793-3306](https://orcid.org/0000-0002-7793-3306)  
**E-mail:** [Ouail.Zakary@oulu.fi](mailto:Ouail.Zakary@oulu.fi)  
**Website:** [Ouail Zakary - webpage](https://cc.oulu.fi/~nmrwww/members/Ouail_Zakary.html)	

## Course Information
This is Exercise N°4 from the Computational Physics and Chemistry 2025 course.

## Prerequisites

### System Requirements
- Python 3.10+
- Tkinter
- Virtual environment support
- Linux (Ubuntu) or macOS
- Jupyter Notebook (for exercise notebooks)

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-tk python3.12-venv

# macOS (using Homebrew)
brew install python-tk@3.12
```

## Installation Instructions

1. Download the Repository
   - Clone or download the repository to your local machine

2. Navigate to Source Directory
   ```bash
   cd path/to/repository/src
   ```

3. Install the Application
   ```bash
   # IMPORTANT: Ensure you are NOT in a Conda environment
   # If in Conda base, deactivate it:
   conda deactivate

   # Run the setup script
   python3 setup_packaging.py
   ```

4. Start the Application
   - After successful installation, a `.sh` file will be created in the parent directory
   - Run the application using:
     ```bash
     ../run_pimd_simulation.sh
     ```

## Using the PIMD Simulation GUI

1. When the GUI opens, set the working directory name
   - **Important**: This directory will contain all input and output data
   - The directory will be created one level up from the source directory

2. Configure Simulation Parameters:
   - Temperature (K)
   - Timestep (fs)
   - Output Stride
   - Number of Beads
   - Total Steps
   - Dynamics Mode
   - Thermostat Mode

3. Click "Start Simulation"

4. After the simulation completes:
   - Manually close the application window
   - Navigate to the working directory to explore the generated data

## Exercise Notebooks
Complete the exercise by following the instructions in:
- `exercice_4_part-1.ipynb`
- `exercice_4_part-2.ipynb`

## Compatibility
- Tested on Ubuntu Linux
- Partial support for macOS
- Not yet implemented for Windows

## Troubleshooting
- Ensure all system dependencies are installed
- Verify you are not in a Conda environment
- Check Python version compatibility

## Contact
Created by Ouail Zakary (ouail.zakary@oulu.fi)

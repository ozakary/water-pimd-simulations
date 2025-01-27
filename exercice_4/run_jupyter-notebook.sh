#!/bin/bash
# Activate virtual environment
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$SCRIPT_DIR/../src/pimd_sim_venv"

# Activate virtual environment
source "$VENV_PATH/bin/activate"


# To open Jupyter Notebook:
jupyter notebook

# Deactivate virtual environment
deactivate

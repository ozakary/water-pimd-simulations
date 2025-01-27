from lammps import lammps
import time
import os
import sys


def create_water_data():
    with open('water.data', 'w') as f:
        f.write("""# Water molecule structure (q-TIP4P/f)

3 atoms
2 bonds
1 angles
2 atom types
1 bond types
1 angle types

-10.0 10.0 xlo xhi
-10.0 10.0 ylo yhi
-10.0 10.0 zlo zhi

Masses

1 15.9994 # O
2 1.008   # H

Atoms # full

1 1 1 -1.1128 0.0 0.0 0.0
2 1 2 0.5564  0.9419 0.0 0.0
3 1 2 0.5564  -0.2392 0.9087 0.0

Bonds

1 1 1 2
2 1 1 3

Angles

1 1 2 1 3
""")

def create_lammps_input():
    socket_name = "water_ipi"
    
    with open('in.water_ipi', 'w') as f:
        f.write(f"""units real
atom_style full
boundary p p p
read_data water.data

# Force field parameters (q-TIP4P/f)
pair_style lj/cut/tip4p/long 1 2 1 1 0.1577 17.007
bond_style harmonic
angle_style harmonic

pair_coeff * * 0.0 0.0
pair_coeff 1 1 0.1852 3.1589  # O-O LJ parameters
bond_coeff 1 1089.1 0.9419    # O-H bond
angle_coeff 1 87.85 107.4     # H-O-H angle

kspace_style pppm/tip4p 1.0e-4

# i-PI socket communication
fix 1 all ipi {socket_name} 32345 unix

timestep 0.5  # Match the timestep in i-PI input
thermo_style custom step temp pe ke etotal press
thermo 10
run 100000000  # Let i-PI control the simulation length
""")

if __name__ == "__main__":
    socket_path = "/tmp/ipi_water_ipi"
    print(f"Looking for socket at: {socket_path}")
    
    create_water_data()
    create_lammps_input()
    
    # Wait for i-PI to initialize
    print("Waiting for i-PI to initialize...")
    max_wait = 30  # Maximum wait time in seconds
    start_time = time.time()
    
    while not os.path.exists(socket_path):
        if time.time() - start_time > max_wait:
            print(f"Error: i-PI socket file not found at {socket_path} after waiting")
            sys.exit(1)
        time.sleep(1)
        print(f"Waiting for socket file at {socket_path}...")
    
    print("Socket file found, starting LAMMPS...")
    time.sleep(2)  # Give a little extra time for i-PI to be ready
    
    try:
        lmp = lammps()
        lmp.file("in.water_ipi")
    except Exception as e:
        print(f"Error running LAMMPS: {e}")
        sys.exit(1)

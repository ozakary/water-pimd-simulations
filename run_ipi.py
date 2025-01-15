from ipi.engine.simulation import Simulation
import os
import sys

def create_init_xyz():
    with open('init.xyz', 'w') as f:
        f.write("""3
Water molecule
O     0.000   0.000   0.000
H     0.958   0.000   0.000
H    -0.239   0.927   0.000
""")

if __name__ == "__main__":
    # Check and remove socket if it exists
    socket_path = "/tmp/ipi_water_ipi"
    if os.path.exists(socket_path):
        try:
            os.remove(socket_path)
            print(f"Removed existing socket file: {socket_path}")
        except Exception as e:
            print(f"Error removing socket file: {e}")
            sys.exit(1)
    
    # Create init.xyz file
    create_init_xyz()
    
    # Check if input.xml exists
    if not os.path.exists("input.xml"):
        print("Error: input.xml file not found!")
        sys.exit(1)
    
    print("Starting i-PI simulation...")
    try:
        simulation = Simulation.load_from_xml("input.xml")
        simulation.run()
    except Exception as e:
        print(f"Error running i-PI: {e}")
        sys.exit(1)

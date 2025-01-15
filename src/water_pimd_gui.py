import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import queue
import sys
import os
import time
from datetime import datetime

class SimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PIMD Simulation GUI")
        
        # Configure main window
        self.root.geometry("800x800")
        self.root.minsize(600, 600)
        
        # Add window closing handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Initialize variables
        self.running = False
        self.processes = []
        self.output_queues = []
        self.socket_path = "/tmp/ipi_water_ipi"
        
        # Create all widgets
        self.create_widgets(main_frame)
        
    def on_closing(self):
        """Handle window closing event"""
        if self.running:
            self.stop_simulation()
            
        # Move any remaining files
        work_dir_name = self.work_dir.get()
        
        # Get the parent directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        work_dir = os.path.normpath(os.path.join(script_dir, '..', work_dir_name))
        
        files_to_move = ['input.xml', 'init.xyz', 'water.data', 'in.water_ipi', 'log.lammps']
        
        for file in files_to_move:
            if os.path.exists(file):
                try:
                    dest_path = os.path.join(work_dir, file)
                    
                    # Ensure destination directory exists
                    os.makedirs(work_dir, exist_ok=True)
                    
                    # Remove existing file at destination if it exists
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    
                    # Move the file
                    os.rename(file, dest_path)
                except Exception as e:
                    print(f"Error moving {file}: {str(e)}")
        
        # Destroy the window
        self.root.destroy()
        
    def create_widgets(self, frame):
        current_row = 0
        
        # Title
        title_label = ttk.Label(frame, text="Path Integral MD Simulation\n \nCreated by Ouail Zakary (e-mail: ouail.zakary@oulu.fi)", 
                              font=('Arial', 14, 'bold'))
        title_label.grid(row=current_row, column=0, columnspan=2, pady=10)
        current_row += 1
        
        # Working Directory Frame
        dir_frame = ttk.LabelFrame(frame, text="Working Directory", padding="10")
        dir_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(dir_frame, text="Directory name:").grid(row=0, column=0, padx=5, sticky="w")
        self.work_dir = tk.StringVar(value="pimd_run_1")
        ttk.Entry(dir_frame, textvariable=self.work_dir, width=30).grid(row=0, column=1, padx=5, sticky="ew")
        current_row += 1
        
        # Parameters Frame
        param_frame = ttk.LabelFrame(frame, text="PIMD Parameters", padding="10")
        param_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Initialize parameters dictionary
        self.params = {}
        
        # Create parameter inputs
        parameters = [
            ("Temperature (K)", "temperature", "300"),
            ("Number of Beads", "nbeads", "32"),
            ("Timestep (fs)", "timestep", "0.5"),
            ("Total Steps", "total_steps", "80000"),
            ("Output Stride", "stride", "100"),
            ("Thermostat τ (fs)", "tau", "100"),
        ]
        
        for i, (label, key, default) in enumerate(parameters):
            row = i // 2
            col_start = (i % 2) * 2
            
            ttk.Label(param_frame, text=label).grid(
                row=row, column=col_start, padx=5, pady=2, sticky="w")
            
            var = tk.StringVar(value=default)
            self.params[key] = var
            ttk.Entry(param_frame, textvariable=var, width=10).grid(
                row=row, column=col_start + 1, padx=5, pady=2)

        # Add dynamics mode dropdown
        row += 1
        ttk.Label(param_frame, text="Dynamics Mode:").grid(
            row=row, column=0, padx=5, pady=2, sticky="w")
        
        self.dynamics_mode = tk.StringVar(value="nvt")
        dynamics_options = ["nvt", "npt", "nve"]
        dynamics_dropdown = ttk.Combobox(param_frame, 
                                       textvariable=self.dynamics_mode,
                                       values=dynamics_options,
                                       width=7,
                                       state="readonly")
        dynamics_dropdown.grid(row=row, column=1, padx=5, pady=2)

        # Add thermostat mode dropdown
        ttk.Label(param_frame, text="Thermostat Mode:").grid(
            row=row, column=2, padx=5, pady=2, sticky="w")
        
        self.thermostat_mode = tk.StringVar(value="langevin")
        thermostat_options = ["langevin", "pile_g", "pile_l", "svr", "ggmt"]
        thermostat_dropdown = ttk.Combobox(param_frame, 
                                         textvariable=self.thermostat_mode,
                                         values=thermostat_options,
                                         width=7,
                                         state="readonly")
        thermostat_dropdown.grid(row=row, column=3, padx=5, pady=2)
        
        current_row += 1
        
        current_row += 1
        
        # Control Buttons Frame
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=current_row, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="Start Simulation", 
                                  command=self.start_simulation)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop Simulation", 
                                 command=self.stop_simulation, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        current_row += 1
        
        # Output Console Frame
        console_frame = ttk.LabelFrame(frame, text="Simulation Output")
        console_frame.grid(row=current_row, column=0, columnspan=2, sticky="nsew", pady=5)
        frame.rowconfigure(current_row, weight=1)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=20)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        current_row += 1
        
        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start simulation")
        status_label = ttk.Label(frame, textvariable=self.status_var)
        status_label.grid(row=current_row, column=0, columnspan=2, pady=5, sticky="w")

    def log_message(self, message):
        """Add timestamped message to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        
    def check_socket_exists(self):
        """Check if the IPI socket file exists"""
        return os.path.exists(self.socket_path)

    def wait_for_socket(self, timeout=30):
        """Wait for the IPI socket file to appear"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_socket_exists():
                return True
            time.sleep(0.1)
        return False
        
    def start_simulation(self):
        if not self.running:
            self.running = True
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self.console.delete(1.0, tk.END)
            
            # Remove existing socket file if it exists
            if self.check_socket_exists():
                try:
                    os.remove(self.socket_path)
                    self.log_message("Removed existing socket file")
                except OSError as e:
                    self.log_message(f"Warning: Could not remove old socket file: {e}")
            
            self.status_var.set("Simulation running...")
            self.output_queues = [queue.Queue(), queue.Queue()]
            threading.Thread(target=self.run_simulation).start()

    def stop_simulation(self):
        if self.running:
            self.running = False
            self.status_var.set("Stopping simulation...")
            
            # Terminate all processes
            for process in self.processes:
                if process and process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
            
            self.processes = []
            
            # Clean up socket file
            if self.check_socket_exists():
                try:
                    os.remove(self.socket_path)
                    self.log_message("Cleaned up socket file")
                except OSError as e:
                    self.log_message(f"Warning: Could not remove socket file: {e}")
            
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self.status_var.set("Simulation stopped")
    
    def monitor_process(self, process, name):
        """Monitor a process and log if it exits unexpectedly"""
        while self.running:
            if process.poll() is not None:
                exit_code = process.poll()
                self.log_message(f"{name} process exited unexpectedly with code {exit_code}")
                self.stop_simulation()
                break
            time.sleep(0.5)

    def ensure_work_dir(self):
        """Create working directory if it doesn't exist"""
        work_dir_name = self.work_dir.get()
        if not work_dir_name:
            raise ValueError("Working directory name cannot be empty")
        
        # Get the parent directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        work_dir = os.path.normpath(os.path.join(script_dir, '..', work_dir_name))
            
        # Create directory if it doesn't exist
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
            self.log_message(f"Created working directory: {work_dir}")
        return work_dir

    def update_xml(self):
        """Update the input.xml file with current parameter values"""
        work_dir = self.ensure_work_dir()
        
        # Log current parameter values
        self.log_message("Current parameter values:")
        for key, var in self.params.items():
            self.log_message(f"  {key}: {var.get()}")
        
        xml_content = f'''<simulation verbosity='high'>
    <output prefix='{os.path.join(work_dir, "simulation")}'>
        <properties stride='{self.params["stride"].get()}' filename='out'>  [ step, time{{picosecond}}, temperature{{kelvin}}, 
            conserved{{electronvolt}}, potential{{electronvolt}}, kinetic_cv{{electronvolt}} ] </properties>
        <trajectory filename='pos' stride='{self.params["stride"].get()}'> positions{{angstrom}} </trajectory>
    </output>
    <total_steps>{self.params["total_steps"].get()}</total_steps>
    <prng><seed>32345</seed></prng>
    <ffsocket mode='unix' name='water_ipi'>
        <address>water_ipi</address>
        <port>32345</port>
    </ffsocket>
    <system>
        <initialize nbeads='{self.params["nbeads"].get()}'>
            <file mode='xyz'> {os.path.join(work_dir, "init.xyz")} </file>
            <cell mode='abc'> [20.0, 20.0, 20.0] </cell>
        </initialize>
        <forces><force forcefield='water_ipi'></force></forces>
        <ensemble>
            <temperature units='kelvin'>{self.params["temperature"].get()}</temperature>
        </ensemble>
        <motion mode='dynamics'>
            <dynamics mode='{self.dynamics_mode.get()}'>
                <timestep units='femtosecond'>{self.params["timestep"].get()}</timestep>
                <thermostat mode='{self.thermostat_mode.get()}'>
                    <tau units='femtosecond'>{self.params["tau"].get()}</tau>
                </thermostat>
            </dynamics>
        </motion>
    </system>
</simulation>'''

        # Write the XML file to working directory
        xml_path = os.path.join(work_dir, 'input.xml')
        try:
            with open(xml_path, 'w') as f:
                f.write(xml_content)
            self.log_message(f"Created input.xml in {work_dir}")
            
            # Create init.xyz in working directory
            xyz_path = os.path.join(work_dir, 'init.xyz')
            with open(xyz_path, 'w') as f:
                f.write("""3
Water molecule
O     0.000   0.000   0.000
H     0.958   0.000   0.000
H    -0.239   0.927   0.000
""")
            self.log_message(f"Created init.xyz in {work_dir}")
            
        except Exception as e:
            self.log_message(f"Error writing files: {str(e)}")
            raise
        
        # Write the XML file
        try:
            with open('input.xml', 'w') as f:
                f.write(xml_content)
            
            # Verify the file was written correctly
            with open('input.xml', 'r') as f:
                written_content = f.read()
                self.log_message("Verifying XML file content:")
                self.log_message(written_content)
                
        except Exception as e:
            self.log_message(f"Error writing XML file: {str(e)}")
            raise
            
    def run_simulation(self):
        try:
            # Clean up any existing files
            if os.path.exists('input.xml'):
                os.remove('input.xml')
                self.log_message("Removed existing input.xml")
            
            # Update input.xml with current parameters
            self.update_xml()
            self.log_message("Created new input.xml with current parameters")
            
            # Start I-PI process with environment variable to increase socket timeout
            env = os.environ.copy()
            env['IPI_TIMEOUT'] = '600'  # 10 minutes timeout
            
            self.log_message("Starting I-PI process...")
            ipi_process = subprocess.Popen(
                [sys.executable, 'run_ipi.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            self.processes.append(ipi_process)
            
            # Start process monitor for I-PI
            threading.Thread(
                target=self.monitor_process,
                args=(ipi_process, "I-PI"),
                daemon=True
            ).start()
            
            # Start output reader for I-PI
            threading.Thread(
                target=self.read_output,
                args=(ipi_process, self.output_queues[0], "I-PI"),
                daemon=True
            ).start()
            
            # Wait for socket file to appear
            self.log_message("Waiting for I-PI to initialize...")
            if not self.wait_for_socket():
                raise Exception("Timeout waiting for I-PI socket file")
            
            self.log_message("I-PI socket file detected, starting LAMMPS...")
            
            # Additional delay to ensure I-PI is fully initialized
            time.sleep(5)
            
            # Start LAMMPS process with environment variable for socket timeout
            env = os.environ.copy()
            env['LAMMPS_IPI_TIMEOUT'] = '600'  # 10 minutes timeout
            
            lammps_process = subprocess.Popen(
                [sys.executable, 'run_lammps.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            self.processes.append(lammps_process)
            
            # Start output reader for LAMMPS
            threading.Thread(
                target=self.read_output,
                args=(lammps_process, self.output_queues[1], "LAMMPS"),
                daemon=True
            ).start()
            
            # Start output processor
            self.process_output()
            
        except Exception as e:
            self.log_message(f"Error starting simulation: {str(e)}")
            self.stop_simulation()
    
    def read_output(self, process, output_queue, prefix):
        try:
            for line in process.stdout:
                if self.running:
                    output_queue.put(f"[{prefix}] {line.strip()}")
                else:
                    break
        except Exception as e:
            output_queue.put(f"[{prefix}] Error reading output: {str(e)}")
        finally:
            output_queue.put(None)  # Signal that the process has ended
    
    def process_output(self):
        # Process any pending output from both queues
        for q in self.output_queues:
            try:
                while True:
                    line = q.get_nowait()
                    if line is None:  # Process has ended
                        break
                    self.log_message(line)
            except queue.Empty:
                pass
        
        # Check processes status
        all_finished = True
        for process in self.processes:
            if process and process.poll() is None:
                all_finished = False
                break
        
        if self.running and not all_finished:
            self.root.after(100, self.process_output)
        else:
            if self.running:  # If we were running but all processes finished
                self.log_message("All processes have finished")
                self.stop_simulation()

def main():
    root = tk.Tk()
    app = SimulationGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

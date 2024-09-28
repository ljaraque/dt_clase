import numpy as np
import matplotlib.pyplot as plt
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil
import csv

# Step function for testing
def step_function(t, step_start_time=4.0, initial_value=0.0, final_value=2.0):
    return initial_value if t < step_start_time else final_value

# Export results to a CSV file
def export_to_csv(time_sim, y_sim, u, filename='simulation_results_dostep.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['time', 'y', 'u'])
        for t, y, u_val in zip(time_sim, y_sim, u):
            writer.writerow([f'{t:.10f}', y, u_val])

# Path to the exported FMU
fmu_path = 'SecondOrderFMU.fmu'

# Simulation parameters
step_start_time = 4.0
initial_value = 0.0
final_value = 2.0
time_start = 0.0
time_end = 16.0
step_size = 0.001

# Time and input arrays for testing
time = np.arange(time_start, time_end, step_size)
u = np.array([step_function(t, step_start_time, initial_value, final_value) for t in time])

# Extract the FMU
unzipdir = extract(fmu_path)
model_description = read_model_description(fmu_path)
model_identifier = model_description.coSimulation.modelIdentifier

# Initialize FMU instance
fmu = FMU2Slave(guid=model_description.guid, unzipDirectory=unzipdir, modelIdentifier=model_identifier, instanceName='instance1')

fmu.instantiate()
fmu.setupExperiment(startTime=time_start)
fmu.enterInitializationMode()
fmu.exitInitializationMode()

# Initialize lists to store results
time_do_step = []
y_do_step = []

# Simulation loop for do_step
current_time = time_start

inputs = [v for v in model_description.modelVariables if v.causality == 'input']
outputs = [v for v in model_description.modelVariables if v.causality == 'output']

while current_time < time_end:
    # Append the current time
    time_do_step.append(current_time)
    
    # Set the input signal for the current time step
    input_value = u[int(current_time / step_size)]
    fmu.setReal([v.valueReference for v in inputs], [input_value])

    # Perform the simulation step
    fmu.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)

    # Collect output value (assuming 'y' is the output variable name)
    y_value = fmu.getReal([v.valueReference for v in outputs])[0]
    y_do_step.append(y_value)

    # Advance time
    current_time += step_size

# Terminate and clean up FMU instance
fmu.terminate()
fmu.freeInstance()

# Export do_step results to CSV
export_to_csv(time_do_step, y_do_step, u, filename='simulation_results_dostep.csv')

# Plot both input and output signals for the FMU simulation (do_step)
plt.figure(figsize=(10, 6))
plt.plot(time, u, label='Input signal u (Step Function)', linestyle='--')
plt.plot(time_do_step, y_do_step, label='Output signal y (do_step)')
plt.xlabel('Time [s]')
plt.ylabel('Signal')
plt.title('Input and Output Signals (do_step)')
plt.grid(True)
plt.legend()
plt.show()

# Clean up extracted FMU directory
shutil.rmtree(unzipdir)

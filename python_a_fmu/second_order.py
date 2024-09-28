from pythonfmu.fmi2slave import Fmi2Slave, Real
import numpy as np

class SecondOrderFMU(Fmi2Slave):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Register parameters
        self.k = 450.0  # Default gain, can be changed
        self.D = 0.2  # Damping ratio
        self.w = 15.0  # Natural frequency

        self.state = np.zeros(2)  # [x, dx/dt]
        self.u = 0.0    # Input signal (start value of 0.0)
        self.y = 0.0    # Output signal

        # Register input and output variables
        # Set start value for input 'u' to avoid validation issues
        self.register_variable(Real("u", causality="input", start=0.0))  # Input signal u
        self.register_variable(Real("y", causality="output"))  # Output signal y
        
        # Register parameters with 'fixed' variability
        self.register_variable(Real("k", causality="parameter", variability="fixed", start=self.k))  # Gain k
        self.register_variable(Real("D", causality="parameter", variability="fixed", start=self.D))  # Damping D
        self.register_variable(Real("w", causality="parameter", variability="fixed", start=self.w))  # Frequency w

    def get_u(self):
        return self.u

    def set_u(self, value):
        self.u = value

    def get_y(self):
        return self.y

    def set_k(self, value):
        self.k = value

    def set_D(self, value):
        self.D = value

    def set_w(self, value):
        self.w = value

    def do_step(self, current_time, step_size):
        # Extract the state variables
        x, dx = self.state

        # Compute the acceleration
        ddx = -2 * self.D * self.w * dx - self.w**2 * x + self.k * self.u

        # Update the state using simple Euler integration
        dx_new = dx + ddx * step_size
        x_new = x + dx * step_size

        # Save the new state
        self.state = np.array([x_new, dx_new])

        # Output is the new displacement
        self.y = x_new

        return True  # Successfully completed the step




# Step function for testing
def step_function(t, step_start_time=4.0, initial_value=0.0, final_value=2.0):
    return initial_value if t < step_start_time else final_value


if __name__ == "__main__":
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

    # Instantiate the FMU-compatible system
    system_fmu = SecondOrderFMU(instance_name="SecondOrderSystem")  # Pass instance_name here
    y_do_step = []
    time_do_step = []

    # Simulate using do_step
    for t in time:
        system_fmu.set_u(step_function(t))
        system_fmu.do_step(t, step_size)
        y_do_step.append(system_fmu.get_y())
        time_do_step.append(t)

    # Plot both input and output signals for do_step simulation
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))
    plt.plot(time, u, label='Input signal u (Step Function)', linestyle='--')
    plt.plot(time_do_step, y_do_step, label='Output signal y (do_step)')
    plt.xlabel('Time [s]')
    plt.ylabel('Signal')
    plt.title('Input and Output Signals (do_step)')
    plt.grid(True)
    plt.legend()
    plt.show()



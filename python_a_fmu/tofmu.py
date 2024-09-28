from pythonfmu import FmuBuilder
from second_order import SecondOrderFMU


# Export the FMU directly from within the script, using the class defined in the script
FmuBuilder.build_FMU(
    class_to_export=SecondOrderFMU,  # Your FMU class defined earlier in the same script
    output_path="second_order_system.fmu",
    script_file="second_order.py",
    fmi_version="2.0",
    fmi_type="CoSimulation"
)

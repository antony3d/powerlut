==================================================
POWER LUT MOD v0.9.6
==================================================

Tool for analyzing and modifying engine torque curves 
specifically for Assetto Corsa.

FEATURES:
- BHP calculation from Torque (Nm).
- Curve visualization and PNG graph export.
- Quick curve modification (+X, -X, *X).
- Export formats: .lut and .json (100 RPM steps).
- Advanced statistics (Peak, Median, Power Band).

REQUIREMENTS:
- Python
- Matplotlib library (run: pip install matplotlib).

USAGE:
1. Modify Torque values:
   python powerlut.py power.lut +10
   python powerlut.py power.lut -5
   python powerlut.py power.lut *0.75

2. Command Flags:
   -png  Export graph to PNG without GUI.
   -v    Enable Verbose Mode for detailed debug.

OUTPUT FILES:
- ui_car.json (Game integration).
- power.lut   (Standard AC format).
- .png        (Graph visualization).

LICENSE: GPL-3.0.
Made for the Assetto Corsa community.
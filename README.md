Power Lut Mod 

Assetto Corsa engine torque/power curve analyzer and modifier tool.
Features

    Calculate power (BHP) from torque (Nm)
    Plot torque/power curves with statistics
    Modify curves (+X, -X, *X)
    Export in ui_car.json format
    Export graphs to PNG (300 DPI)
    Detailed statistics (Median, Peak, Power Band)
    Verbose mode for debugging

Requirements
pip install matplotlib
Usage
Basic run
python powerlut.py power.lut
With modifier
python powerlut.py power.lut +10
python powerlut.py power.lut -5
python powerlut.py power.lut '*1.2'
Export to PNG (no GUI window)
python powerlut.py power.lut -png
Verbose mode (debug output)
python powerlut.py power.lut -v
Combined options
python powerlut.py power.lut +10 -v -png
File Formats
Input: .lut
Format: RPM|Torque(Nm)
Output: .json
No outer {}
Comma at the end
Newline before powerCurve
100 RPM step interpolation
1 decimal place precision
Output: .png

    300 DPI resolution
    Dark theme
    Torque (yellow) + Power (red) curves
    Median lines
    Power Band (80% peak)

Output: _bph.txt (verbose mode only)
Format: RPM|Power(BHP)
Statistics Report
Metric
	
Description
Peak Torque
	
Maximum torque value and RPM
Median Torque
	
Median value in working range
Effective Range
	
RPM range where torque is effective
Peak Power
	
Maximum power value and RPM
Power Band
	
RPM range where power 80% of peak
Median Power
	
Median value in working range
Version
Current: v0.9.6
Author
Anton (antony3d)
License
GPL-3.0
Support
For issues, suggestions, or questions, please open an issue on GitHub.
Made with love for Assetto Corsa community
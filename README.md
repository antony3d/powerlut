Power Lut Mod v0.9.6

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
Basic run - powerlut.py (use power.lut for input)

With modifier torque curve

powerlut.py power.lut +10 (add torque curve)

powerlut.py power.lut -5 (- torque)

powerlut.py power.lut '*1.2' (mult torque)

Export to PNG (no GUI window)

python powerlut.py power.lut -png

Verbose mode (debug output)

powerlut.py power.lut -v

Output: .json file:

100 RPM step interpolation

Output: _bph.txt (verbose mode only)

Format: RPM|Power(BHP)

=
ENGINE CURVE STATISTICS REPORT
=

[TORQUE]

  Peak Torque:     46.00 Nm @ 3750 RPM
  
  Median:          28.00 Nm
  
  Effective Range: 1500 – 6000 RPM

[POWER]

  Peak Power:      26.26 BHP @ 4250 RPM
  
  Power Band:      3750 – 4750 RPM (≥80% peak)
  
  Median:          15.31 BHP
  
  Effective Range: 1500 – 6000 RPM

============================================================

License GPL-3.0

For issues, suggestions, or questions, please open an issue on GitHub.

Made with love for Assetto Corsa community ;)

Markdown
# Power Lut Mod `v0.9.6`

**Power Lut Mod** is a specialized tool for analyzing and modifying engine torque/power curves specifically for the **Assetto Corsa** engine.

---

## 🚀 Features

* **BHP Calculation:** Automatically calculates Power (BHP) from Torque (Nm).
* **Curve Visualization:** Plots high-quality torque/power curves with detailed statistics.
* **Curve Modification:** Quickly adjust values using mathematical operators (`+X`, `-X`, `*X`).
* **Format Export:** * Export in `ui_car.json` format for direct game integration.
    * High-resolution **PNG** graph export (**300 DPI**).
* **Advanced Statistics:** Tracks Peak values, Median, and the specific Power Band.
* **Verbose Mode:** Detailed console output for debugging and deep analysis.

---

## 🛠 Requirements

This tool requires Python and the `matplotlib` library for rendering:

```bash
pip install matplotlib
💻 Usage
Basic Execution
The program looks for power.lut by default:

Bash
python powerlut.py
Torque Curve Modifiers
Modify the torque values on the fly by passing arguments:

Bash
python powerlut.py power.lut +10      # Add 10 Nm to the entire curve
python powerlut.py power.lut -5       # Subtract 5 Nm
python powerlut.py power.lut "*1.2"   # Multiply torque by 1.2 (+20%)
Command Flags
Export to PNG: Generate a graph file without opening a GUI window.

Bash
python powerlut.py power.lut -png
Verbose Mode: Enable detailed debug output.

Bash
python powerlut.py power.lut -v
📂 Output Files
.json file: Features 100 RPM step interpolation for the game engine.

_bph.txt: (Verbose mode only) A raw text file in RPM | Power(BHP) format.

📊 Engine Curve Statistics Report
The tool generates a structured report in the console:

Plaintext
============================================================
ENGINE CURVE STATISTICS REPORT

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
📜 License & Support
License: GPL-3.0

Feedback: For issues, suggestions, or questions, please open an issue on GitHub.

Made with love for the Assetto Corsa community ;)
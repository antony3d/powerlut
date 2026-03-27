Markdown
# Power Lut Mod `v0.9.6`

**Power Lut Mod** is a specialized tool for analyzing and modifying engine torque/power curves specifically for the **Assetto Corsa** engine.

<img src="powerlut.jpg" alt="Preview" width="100%">

## Features

* **BHP Calculation:** Automatically calculates Power (BHP) from Torque (Nm).
* **Curve Visualization:** Plots high-quality torque/power curves with detailed statistics.
* **Curve Modification:** Quickly adjust values using mathematical operators (`+X`, `-X`, `*X`).
* **Format Export:** * Export in `ui_car.json` `power.lut` format for direct game integration.
* **PNG** file graph export
* **Advanced Statistics:** Tracks Peak values, Median, and the specific Power Band.
* **Verbose Mode:** Detailed console output for debugging and deep analysis.


## Requirements

This tool requires Python and the `matplotlib` library for rendering:

	pip install matplotlib

## Usage
**Torque Curve Modifiers** 
Modify the torque values on the fly by passing arguments
Add 10 Nm to the entire curve:

	python powerlut.py power.lut +10
    
Subtract 5 Nm:

	python powerlut.py power.lut -5

Multiply torque by 0.75 (-25%)

	python powerlut.py power.lut *0.75

**Command Flags**

`-png` – Export to PNG: generate a graph file without opening a GUI window.

	python powerlut.py power.lut -png
    
`-v` – Verbose Mode: enable detailed debug output.
 
	python powerlut.py power.lut -v
    
## Output Files

`.json` – Features 100 RPM step interpolation for the game engine.
`.lut` - text output for RPM|Torque at AC format    
`_bph.txt` – _(Verbose mode only)_ raw text file in `RPM | Power(BHP)` format, just for fun. 


## Console Output Example

    ==============================
    ENGINE CURVE STATISTICS REPORT
    ==============================
    [TORQUE]
      Peak Torque:     46.00 Nm @ 3750 RPM
      Median:          28.00 Nm
      Effective Range: 1500 – 6000 RPM
    [POWER]
      Peak Power:      26.26 BHP @ 4250 RPM
      Power Band:      3750 – 4750 RPM (≥80% peak)
      Median:          15.31 BHP
      Effective Range: 1500 – 6000 RPM
    
**License: GPL-3.0**
    
*Made with love for the Assetto Corsa community ;)*


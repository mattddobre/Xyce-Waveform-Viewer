This is a basic interactive waveform viewer that parses the .prn ouptut of the xyce spice simulator, supporting the outputs of multiple simulations (monte carlo, parameters sweeps). 

Use: 
- To load file, select 'add file' from the utils dropdown 
- To add a new pane, select 'add pane' from the utils dropdown 
- To plot a mathematical expression, hold command while selecting signals from the sidebar, right-click and select plot math. Insert a mathematical expression into the popup of the selected signals. 
  Ex: 
  ln(V1) + V2
  Click ok, and the plot will appear on the right.   
- To plot a group of signals, hold command while selecting signals from the sidebar, right-click and select plot group.
- To delete or rename a pane, right click on the tab in the plotting window and selected appropriate option

command: python3 xyceWaveformViewer.py (filename)

dependencies:
pyqt5 
matplotlib 
numpy 
sympy 
pandas

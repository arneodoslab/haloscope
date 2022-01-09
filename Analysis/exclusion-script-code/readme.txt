file descriptions:

final-plot.ipynb - notebook to plot all the exclusion curves from different experiments
computation.py - contains relevant functions to do haloscope calculations
dm_statistics.py - contains the code to calculate+plot the upper limits and discovery power
optimization.py - contains the code for stack optimization
rate.py - contains the code for getting the kinetic mixing parameter values from given rate 
		or number of events

-----------
to get the upper limit plot,run the dm_statistics script from terminal as:

python3 dm_statistics.py

--------------
After executing the program asks to input values for different parameters. 

Values to use:
observed rate in Hz: 98
bgd rate in Hz: 96
plot type: B1
sensor: excelitas
---------------

Plot descriptions:

A1: 90% CL upper limit assuming no bgd
A2: Discovery power assuming no bgd
B1: 90% CL upper limit using likelihood ratios
B2: Discovery power using likelihood ratios

the data is saved in the plot-data file. 

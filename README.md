# Haloscope

Multilayer dielectric haloscope prototype using a SPAD as photosensor. GEANT4 sim, statistical analysis, boost factor optimisation

Here we provide all the code used in the analysis for the publication found [here](https://arxiv.org/abs/2110.10497)

# Contents

1. **[Analysis]() |** Data and code for SPAD characterization, boost spectrum, and exclusion curve
2. **[Geant4](https://github.com/arneodoslab/haloscope/tree/master/Geant4) |** Code from the Geant4 optical photon simulation.

# Analysis

## About
Data analysis and statistics code for the SPAD characterization, boost spectrum optimization, and generating the exclusion curve. 

## Links

1. **[SPAD Plots](https://github.com/arneodoslab/haloscope/blob/master/Analysis/apd-characterization/excelitas-characterization.ipynb):** SPAD characterization plots corresponding to figure 9 in the paper
2. **[Boost Spectrum with Error Band](https://github.com/arneodoslab/haloscope/blob/master/Analysis/boost-error-optimization/boost-error.ipynb):** Boost spectrum plot with 15th to 85th percentile variations (Figure 10)
3. **[Exclusion Curve](https://github.com/arneodoslab/haloscope/blob/master/Analysis/exclusion-script-code/final-plot.ipynb):** Exclusion curve calculated using 90% CL upper limits (Figure 11)


# Geant4

## About

C++ code for conducting optical photon simulations. Specifically, we generate photons in a disk within the stack with a small random perturbation from the normal. The photons propagate through the stack and the CAD model of the lens, and finally hit a detector at a predefined distance. Finally the coordinated of the hits on the detector as exported, and then processed by the analysis script to reconstruct it.

## Links

1. **[Final Plot](https://github.com/arneodoslab/haloscope/blob/master/Geant4/Results/lens-GEANT4.png):** Plot of frequency vs distance from focal point.
2. **[Hits Visualization](https://github.com/arneodoslab/haloscope/blob/master/Geant4/Results/hits.gif):** Animation that shows how the hits are distributed to the detector surface as the detector moves away from the lens.
3. **[Analysis Script](https://github.com/arneodoslab/haloscope/blob/master/Geant4/Results/Results.ipynb):** Jupyter notebook with the analysis of the data from the simulation.
4. **[Lens Simulation](https://github.com/arneodoslab/haloscope/tree/master/Geant4/Lens_Simulation):** Code to optimize the shape of the lens for maximum collection efficiency. 

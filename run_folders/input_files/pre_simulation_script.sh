#!/bin/bash

# A script to do things before the simulator runs
# Be sure to use paths relative to the container's file hierachy


echo "Doing pre simulation actions in pre_simulation_scipt.sh"
# How to pass arguments into here???
python3 /home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/R_code_generator.py $*

# Use the R library to turn the trace file into a binary for injestion by the simulator
R_LIBS_SITE=/home/slurm/R_packages Rscript /home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/trace.R

# singularity_slurm_simulator
A Singularity container for the Slurm Simulator

To build the `slurm_sim.sif` container, use the following command:
```
sudo singularity build slurm_sim.sif slurm_sim.def
```

To execute the container, we must make the directories read/writable by mapping the `run_folders` into our conatiner in the appropriate places: 
```
singularity run \
 -B ./run_folders/sql_data:/var/lib/mysql \
 -B ./run_folders/sql_run:/var/run/mysqld \
 -B ./run_folders/results:/home/slurm/slurm_sim_ws/sim/micro/baseline/results \
 -B ./run_folders/log:/home/slurm/slurm_sim_ws/sim/micro/baseline/log \
 -B ./run_folders/var:/home/slurm/slurm_sim_ws/sim/micro/baseline/var \
 -B ./run_folders/etc:/home/slurm/slurm_sim_ws/sim/micro/baseline/etc \
 -B ./run_folders/input_files:/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files \
 slurm_sim.sif 
```

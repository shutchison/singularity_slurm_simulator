# singularity_slurm_simulator
A Singularity container for the Slurm Simulator

For portability, each container creates its own database for logging information about the submitted and run jobs, and for checking the users in the simulation have the appropriate permissions to access the simulated resources.

To build the `slurm_sim.sif` container, use the following command:
```
sudo singularity build slurm_sim.sif slurm_sim.def
```
# About the files in this repo
The file hierarchy of this repository should look like this:
```
Repo
│   README.md
│   
└── R_packages
└── run_folders
    └── etc
    └── input_files
    └── log
    └── results
    └── sql_data
    └── sql_run
    └── var
└── simulator_files
```
## R\_packages
The simulator authors wrote an R package which allows you to specify the job requirements which will be simulated by the Slurm simulator (see https://github.com/ubccr-slurm-simulator/slurm\_sim\_tools).  This R script generates a binary trace file which is then ingested by the simulator.  If each simulation is simulating different jobs, it can be useful to let the Singularity container run the R script to generate the trace file required by the simulator.  If each simulation is simulating the same set of input jobs, it would be more efficient to generate this once yourself and provide the .trace file to the simulator in the `run_folders/input_files` folder directly.

## run\_folders
In order to run properly and produce lasting output, the conatiner requires certain folders to be writable. In order to provide writable into the singularity container upon execution, these folders are bound using the `-B` flag into the contains in the appropriate places.

###  run\_folders/etc
This folder contains configuration files for Slurm, such as the sim.conf and the slurm.conf files.

### run\_folders/input\_files
This folder contains pre and post simulation scripts, which can be modified for set up and clean up tasks.  It should also contain a file named `trace.R` if you want the container to produce a files names `test.trace` for you.  If a file named `test.trace` already exists in this folder, R will not run to produce another one.

### run\_folders/log
As the simulator runs, slurmctld, slurmdbd, and various other slurm utilities are executed periodically, and their output is logged into this folder.  If your simulator has issues or crashes, these files will be invaluable in investigating what went wrong and how you can fix it.

### run\_folders/results
Assuming your simulator successfully completes, a script provided by the simulator authors will parse the various log files into CSV files into this folder, and will copy various log files you may be interested in into this folder.  If the logging is done too frequently, these scripts can have parse errors when attempting to generate the CSV files.  You can adjust this frequency in the `sim.conf` file.

### run\_folders/sql\_data
This folder is mapped to where MariaDB creates the files for the database.  This folder should be empty upon starting the simulation, but files will be created as the database is created and populated so Slurm can run properly.

### run\_folders/sql\_run
To reduce the number of ports, the database is directed to use a socket for interprocess communication.  The socket and a .pid file the simulator expects are located in this folder.

### run\_folders/var
If you want your simulation to begin "in the middle of things" or already be running jobs, you would modify the files in this folder to specify what's already running or the current status of your nodes upon simulation start up.  Currently, the simulation starts fresh with no running jobs, and no downed nodes.

## simulator\_files
This is a copy of the Slurm simulator files (see: https://github.com/ubccr-slurm-simulator/slurm_simulator)

To start this container as an instance:
```
singularity instance start \
 -B ./run_folders/sql_data:/var/lib/mysql \
 -B ./run_folders/sql_run:/var/run/mysqld \
 -B ./run_folders/results:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/results \
 -B ./run_folders/log:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/log \
 -B ./run_folders/var:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/var \
 -B ./run_folders/etc:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/etc \
 -B ./run_folders/input_files:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/input_files \
 slurm_sim.sif instance1
```
You would interact with this instance using:
```
singularity shell instance://instance1
```

You would stop this instance using:
```
singularity instance stop instance1
```

To execute the container, we must make the directories read/writable by mapping the `run_folders` into our conatiner in the appropriate places: 
```
singularity run \
 -B ./run_folders/sql_data:/var/lib/mysql \
 -B ./run_folders/sql_run:/var/run/mysqld \
 -B ./run_folders/results:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/results \
 -B ./run_folders/log:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/log \
 -B ./run_folders/var:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/var \
 -B ./run_folders/etc:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/etc \
 -B ./run_folders/input_files:/home/slurm/singularity_slurm_simulator/simulator_files/slurm_sim_ws/sim/micro/baseline/input_files \
 slurm_sim.sif 
```

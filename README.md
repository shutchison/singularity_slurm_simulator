# singularity_slurm_simulator
A Singularity container for the Slurm Simulator

For portability, each container creates its own database for logging information about the submitted and run jobs, and for checking the users in the simulation have the appropriate permissions to access the simulated resources.  When the simulator runs, the database user is your username.  The username/passsword created when building the container should agree with the creditials provided in the ```input_files/etc/slurmdbd.conf``` file.  Edit the slurm_sim.def file (around line 50) to ensure you add your preferred user/password combo.  If you're running this on an HPC system, you should use your HP username as the database admin.

To build the `slurm_sim.sif` container, use the following command:
```
sudo singularity build slurm_sim.sif slurm_sim.def
```

To run this container: 
First, delete any contents of the sql_data folder and then, to execute the container, we must make the directories read/writable by mapping the `run_folders` into our conatiner in the appropriate places: 
```
rm -rf ./run_folders/sql_data/* && \
singularity run \
 -B ./run_folders/sql_data:/var/lib/mysql \
 -B ./run_folders/sql_run:/var/run/mysqld \
 -B ./run_folders/results:/slurm_sim_ws/sim/micro/baseline/results \
 -B ./run_folders/log:/slurm_sim_ws/sim/micro/baseline/log \
 -B ./run_folders/var:/slurm_sim_ws/sim/micro/baseline/var \
 -B ./run_folders/etc:/slurm_sim_ws/sim/micro/baseline/etc \
 -B ./run_folders/input_files:/slurm_sim_ws/sim/micro/baseline/input_files \
 slurm_sim.sif  
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

# Container workflow
See slurm_sim.def and modify prior to building it if you need to make changes to how this container executes.  As is, this container will 
1. Create a new database in the empty sql_data folder.  If this folder has database files in it already from previous runs, sometimes the container's database can not start, which will prevent the simulator from running.  It is recommended to delete all files in the sql_data folder prior to running the container.
2. Add the slurm user as a super user to the database.  This is required because the simulator runs as your user which will create a database to allow for authentication of user accounts in Slurm when they submit jobs.
3. Run the pre-simulation.sh script.  Any actions required prior to running the simulator need to be done by this script.  For instance, you may need to locate an available port on the running machine for your database to bind to, and adjust the slurmdbd.conf and slurm.conf file's DefaultStoragePort=<whatever open port you've found> (see ```run_folders/input_files/find_open_port.sh``` and ```/run_folders/input_files/update_ports.py```).  You might also want each container to simulate different jobs by generating a new trace.R file (see ```/run_folders/input_files/R_code_generation.py```)
4. Start the slurm database daemon running in the background and run some sacctmgr commands.  Since this will be the first time starting, the appropriate cluster's database will be created in the database.
5. Grant the slurm user permissions to the new database.  Again, this is required by Slurm so job records can be created as jobs are simulated.
6. Do the simulation by calling the run_sim.py script provided by the simulator authors and modified by me.
    - The -a flag in the script will use sacctmgr to execute the lines of the ```/run_folders/input_files/sacctmgr_commands.txt``` file.  You might need to populate this file with the users and accounts from the set of jobs you've chosen so when a user or account submits a job to the simulation, that user and account will exist already.  Otherwise, the job will not be scheduled for execution by the simulator.
    - Assuming the simulation went well and didn't crash, upon completing the simulations, the run_sim.py script will copy log files from the log folder into the results folder.  It will do some post processing on the files and create some CSV files which are easier to process than the raw log data itself.  If the logging period is too short (see ```/input_files/etc/sim.conf```) and the simulator is very busy, the output from the Slurm commands (sdiag, sprio, squeue, etc.) as the simulator is running might not complete which can cause parsing errors, even if the simulation completed successfully.
7. Run the post_simulation_script.sh script to do any actions inside the container prior to container run exit.

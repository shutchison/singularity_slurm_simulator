from collections import namedtuple
from collections import defaultdict
import math
import datetime
import argparse
import shutil
import datetime

headers = ""

DEVELOPING = False

def get_slurm_parameters(slurm_array_task_id):
    directives_file = open("/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/run_directives.txt", "r")
    if DEVELOPING:
        directives_file = open("/homes/scotthutch/singularity_slurm/run_directives/run_directives.txt", "r")
    directive_lines = directives_file.readlines()
    directives_file.close()
    
    directive_line = ""
    print("Run directive for this run is:")
    for line in directive_lines:
        if "run_{}:".format(slurm_array_task_id) in line:
            directive_line = line
            print(directive_line)
            break;

    if directive_line == "":
        raise NameError("Unable to find run directive.  You must have a \"run_{}: \" in your run_directives.txt file.".format(slurm_array_task_id))

    run_num, directives = directive_line.split()

    slurm_params = directives[:directives.find(",DateFilter=")] + "\n"
    
    return slurm_params

def get_date_filter(slurm_array_task_id):
    global DEVELOPING 

    if DEVELOPING:
        directives_file = open("/homes/scotthutch/singularity_slurm/run_directives/run_directives.txt", "r")
    else:
        directives_file = open("/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/run_directives.txt", "r")
    directive_lines = directives_file.readlines()
    directives_file.close()
    
    directive_line = ""
    print("Run directive for this run is:")
    for line in directive_lines:
        if "run_{}:".format(slurm_array_task_id) in line:
            directive_line = line
            print(directive_line)
            break;

    if directive_line == "":
        raise NameError("Unable to find run directive.  You must have a \"run_{}: \" in your run_directives.txt file.".format(slurm_array_task_id))

    run_num, directives = directive_line.split()

    date_filter = directives[directives.find("DateFilter="):].split("=")[1]
    
    return date_filter

def update_slurm_conf(slurm_array_task_id):
    if DEVELOPING:
        return

    scheduler_parameter = get_slurm_parameters(slurm_array_task_id)

    slurm_conf_file = open("/home/slurm/slurm_sim_ws/sim/micro/baseline/etc/slurm.conf", "r")
    lines = slurm_conf_file.readlines()
    slurm_conf_file.close()

    for index, line in enumerate(lines):
        if "SchedulerParameters" in line:
            lines[index] = scheduler_parameter
            print("Replacing SlurmParameters line in run_{}.txt".format(slurm_array_task_id))
            break
    
    slurm_conf_file = open("/home/slurm/slurm_sim_ws/sim/micro/baseline/etc/slurm.conf", "w")
    slurm_conf_file.write("".join(lines))
    slurm_conf_file.close()
    print("Update complete to: /home/slurm/slurm_sim_ws/sim/micro/baseline/etc/slurm.conf")


def find_jobs(slurm_array_task_id):
    global headers

    START_LINE = -1
    NUM_JOBS = -1
    DATE_TO_KEEP = get_date_filter(slurm_array_task_id)
    date_elements = DATE_TO_KEEP.split(",")
    if "pack" in date_elements:
       date_elements = date_elements[:date_elements.index("pack")] 
#    if START_LINE == -1:
#        raise NameError("You must have a StartLine=<some number> line in your directives file.")
#    if NUM_JOBS == -1:
#        raise NameError("You must have a NumJobs=<some number> line in your directives file.")
    if DATE_TO_KEEP == "":
        raise NameError("You must have a DateFilter=YYYY-MM-DD line in your directives file.")

    #check if this trace file has already been created.
    tracefile_name = r"/homes/scotthutch/singularity_slurm/trace_files/{}.trace".format(DATE_TO_KEEP)
    usersfile_name = r"/homes/scotthutch/singularity_slurm/trace_files/{}.users.sim".format(DATE_TO_KEEP)
    sacctmgr_commandsfile_name = r"/homes/scotthutch/singularity_slurm/trace_files/{}.sacctmgr_commands.txt".format(DATE_TO_KEEP)
    try:
        shutil.copyfile(tracefile_name, r"/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/test.trace")
        print("Found archived {}.trace.  Copying to input folder.".format(DATE_TO_KEEP))
        shutil.copyfile(usersfile_name, r"/home/slurm/slurm_sim_ws/sim/micro/baseline/etc/users.sim")
        print("Found archived {}.users.sim.  Copying to etc folder.".format(DATE_TO_KEEP))
        shutil.copyfile(sacctmgr_commandsfile_name , r"/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/sacctmgr_commands.txt")
        print("Found archived {}.sacctmgr_commands.txt.  Copying to input folder.".format(DATE_TO_KEEP))
        exit()
    except FileNotFoundError as e:
        print("Archived trace file not found for {}.  Attempting to create one.".format(DATE_TO_KEEP))
        print(e)

    jobs = []

    start_processing = False

    with open("/homes/scotthutch/beocat_slurm_raw.csv", "r", encoding="latin-1") as f_in:
        for line_num, line in enumerate(f_in):
            if headers == "":
                headers = list(map(str.strip, line.split("|")))
                Job = namedtuple("Job", headers)
                continue
            
            try:
                job = Job._make(line.split("|"))
            except Exception as e:
                #print("Problem on line number: {}".format(line_num))
                #print("Line is: {}".format(line))
                #print(e)
                continue
            
            if "." in job.JobID or "_" in job.JobID or job.JobID == "":
                continue

            # Logic for ommiting certain jobs here
            if any([date in job.Submit for date in date_elements]):
                jobs.append(job)

    jobs = sorted(jobs, key=lambda j: j.Submit)

    #make unique jobID
    for index, job in enumerate(jobs):
        jobs[index] = job._replace(JobID=str(1000 + index))

    print("Found {} jobs".format(len(jobs)))

    if "pack" in DATE_TO_KEEP:
        date_filter_elements = DATE_TO_KEEP.split(",")
        num_days = int(date_filter_elements[date_filter_elements.index("pack")+1])
        print("Found pack directive to adjust job submit times into {} days".format(num_days))
        
        date, time = jobs[0].Submit.split("T")
        years, months, days = date.split("-")
        hours, minutes, seconds = time.split(":")

        start_time = datetime.datetime(year=int(years),
                                       month=int(months),
                                       day=int(days),
                                       hour=int(hours),
                                       minute=int(minutes),
                                       second=int(seconds))

        running_time = start_time
        num_jobs = len(jobs)
        job_delta = datetime.timedelta(days=num_days)/num_jobs

        for index, job in enumerate(jobs):
            new_start_time = running_time + job_delta
            running_time = new_start_time
            new_start_string = "{}-{:02}-{:02}T{:02}:{:02}:{:02}".format(new_start_time.year,
                                                                         new_start_time.month,
                                                                         new_start_time.day,
                                                                         new_start_time.hour,
                                                                         new_start_time.minute,
                                                                         new_start_time.second)
            jobs[index] = job._replace(Submit=new_start_string)

    return jobs

def write_csv(out_folder, jobs):
    if DEVELOPING:
        return
    global headers 

    with open(out_folder + "trace.csv", "w") as f_out:
        f_out.write("|".join(headers) + "\n")
        for job in jobs:
            try:
                f_out.write("|".join([getattr(job, field) for field in job._fields]))
            except UnicodeEncodeError as e:
                print("UnicodeEncodeError writing line to csv file.  Ignoring.")

                print(e)
                try:
                    print(job)
                except Exception as e:
                    print(e)

    print("csv file written to " + out_folder + "trace.csv")

def write_R_script(out_folder, jobs):
    if DEVELOPING:
        return

    #build a trace file R script for R to run
    R_string = "library(RSlurmSimTools)\n\ntrace <- list(\n"
    for job in jobs:
        R_string += " "*4 +"sim_job(\n"
        R_string += " "*8 + "job_id = " + job.JobID + ",\n"
        R_string += " "*8 + "submit = \"" + job.Submit.replace("T", " ") + "\",\n"

        req_seconds = int(job.TimelimitRaw)
        req_minutes = math.ceil(req_seconds/60)
        R_string += " "*8 + "wclimit = " + str(req_minutes) + "L,\n"
        R_string += " "*8 + "duration = " + job.ElapsedRaw + "L,\n"
        R_string += " "*8 + "tasks = " + job.ReqCPUS + "L,\n"
        R_string += " "*8 + "tasks_per_node = " + job.ReqNodes + "L,\n"
        R_string += " "*8 + "username = \"" + job.User + "\",\n"
        R_string += " "*8 + "qosname = \"" + job.QOS + "\",\n" 
        R_string += " "*8 + "account = \"" + job.Account + "\",\n"
        
        mem_string = ""
        for character in job.ReqMem:
            if character.isdecimal():
                mem_string += character
            else:
                break
        if "Gn" in job.ReqMem:
            mem_string = str(int(mem_string) * 1000)
            R_string += " "*8 + "req_mem = " + mem_string + "L,\n"
            R_string += " "*8 + "req_mem_per_cpu = " + mem_string + "L,\n"
        elif "Gc" in job.ReqMem:
            mem_string = str(int(mem_string) * 1000)
            req_nodes = job.ReqNodes
            if(req_nodes == "-1.00"):
                req_nodes = 1
            R_string += " "*8 + "req_mem = " + str(int(mem_string) * int(req_nodes)) + "L,\n"
            R_string += " "*8 + "req_mem_per_cpu = " + mem_string + "L,\n"
        if "Mn" in job.ReqMem:
            R_string += " "*8 + "req_mem = " + mem_string + "L,\n"
            R_string += " "*8 + "req_mem_per_cpu = " + mem_string + "L,\n"
        elif "Mc" in job.ReqMem:
            R_string += " "*8 + "req_mem = " + str(int(mem_string) * int(job.ReqNodes)) + "L,\n"
            R_string += " "*8 + "req_mem_per_cpu = " + mem_string + "L,\n"
            
#        R_string += " "*8 + "features = " + job. + ",\n"
#        if job.ReqGRES != "":
#            R_string += " "*8 + "gres = \"" + job.ReqGRES + "\",\n"
#        R_string += " "*8 + "shared = " + job. + ",\n"
#        R_string += " "*8 + "dependency = " + job. + ",\n"
#        R_string += " "*8 + "cancelled = " + job. + ",\n"

        R_string += " "*4 + "),\n"
        #print(R_string)

    R_string = R_string.strip(",\n") + "\n)\n\ntrace <- do.call(rbind, lapply(trace,data.frame))\n\nwrite_trace(\"/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/test.trace\",trace)"
    
    with open(out_folder + "trace.R", "w") as f_out:
        f_out.write(R_string)
    print("R file written to " + out_folder + "trace.R")

def write_files_for_database(jobs):
    if DEVELOPING:
        return

    #production
    users_file_name = r"/home/slurm/slurm_sim_ws/sim/micro/baseline/etc/users.sim"
    sacctmgr_file_name = r"/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/sacctmgr_commands.txt"
    #testing
    #users_file_name = r"/homes/scotthutch/singularity_slurm/run_folders/etc/users.sim"
    #sacctmgr_file_name = r"/homes/scotthutch/singularity_slurm/run_folders/input_files/sacctmgr_commands.txt"
    
    accounts_with_users = defaultdict(set)

    for job in jobs:
       accounts_with_users[job.Account].add(job.User) 

    users_file = open(users_file_name, "w")
    sacctmgr_file = open(sacctmgr_file_name, "w")

    #sacctmgr_file.write("modify QOS set normal Priority=0\n")
    #sacctmgr_file.write("add QOS Name=supporters Priority=100\n")
    #sacctmgr_file.write("add cluster Name=beocat Fairshare=1 QOS=normal,supporters\n")

    for account, user_set in accounts_with_users.items():
        sacctmgr_file.write("add account name={} Fairshare=100\n".format(account))

        for user in user_set:
            sacctmgr_file.write("add user name={} DefaultAccount={} MaxSubmitJobs=10000\n".format(user, account))

    sacctmgr_file.write("modify user set qoslevel=\"normal,supporters\"")

    UID = 2001
    users = set()
    
    for user_set in accounts_with_users.values():
        users = users.union(user_set)

    for user in users:
        users_file.write("{}:{}\n".format(user, UID))
        UID += 1

    sacctmgr_file.write("\n")

    users_file.close()
    sacctmgr_file.close()
    
    print("Users file created:  {}".format(users_file_name))
    print("sacctmgr directives created: {}".format(sacctmgr_file_name))

if __name__ == "__main__":
    if DEVELOPING:
        jobs = find_jobs(2)
        exit()
    parser = argparse.ArgumentParser(description="A program for selecting jobs from a .csv file to generate an R script.")

    parser.add_argument("slurm_array_job_id",
                        type=int
                       )
    parser.add_argument("slurm_array_task_id",
                        type=int
                       )
    

    parser.add_argument("-o", "--output-folder",
                        default=r"/home/slurm/slurm_sim_ws/sim/micro/baseline/input_files/"
                       )

    args = parser.parse_args()
    print("***Arguments recieved in R_code_generator.py: {}".format(args))

    update_slurm_conf(args.slurm_array_task_id)
    jobs = find_jobs(args.slurm_array_task_id)

    write_files_for_database(jobs)
    write_csv(args.output_folder, jobs)
    write_R_script(args.output_folder, jobs)

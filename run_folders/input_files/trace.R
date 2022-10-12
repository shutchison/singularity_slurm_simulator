library(RSlurmSimTools)

trace <- list(
    sim_job(
        job_id = 1000,
        submit = "2018-04-02 11:06:12",
        wclimit = 1L,
        duration = 3L,
        tasks = 1L,
        username = "user1",
        account = "account1"
    ),
    sim_job(
        job_id = 1001,
        submit = "2018-04-02 11:19:12",
        wclimit = 1L,
        duration = 9L,
        tasks = 1L,
        username = "user1",
        account = "account1"
    ),
    sim_job(
        job_id = 1002,
        submit = "2018-04-02 11:29:46",
        wclimit = 304L,
        duration = 18L,
        tasks = 1L,
        username = "user1",
        account = "account1"
    ),
    sim_job(
        job_id = 1003,
        submit = "2018-04-02 11:46:14",
        wclimit = 1L,
        duration = 5L,
        tasks = 1L,
        username = "user1",
        account = "account1"
    ),
    sim_job(
        job_id = 1004,
        submit = "2018-04-02 11:49:43",
        wclimit = 42L,
        duration = 8L,
        tasks = 8L,
        username = "user1",
        account = "account1"
    ),
    sim_job(
        job_id = 1005,
        submit = "2018-04-02 12:00:49",
        wclimit = 42L,
        duration = 14L,
        tasks = 8L,
        username = "user1",
        account = "account1"
    ))


trace <- do.call(rbind, lapply(trace,data.frame))

# Need to change the path in the file that generates this?
write_trace("/slurm_sim_ws/sim/micro/baseline/input_files/test.trace",trace)

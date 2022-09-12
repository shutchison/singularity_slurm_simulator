import os
import re
from slurmsim import log

import subprocess
import tqdm
import multiprocessing
#import zstandard as zstd


class Archive:
    def __init__(self, top_dir: str, type='slurm_run', threads_per_file: int = 1, num_of_proc: int = 1):
        self.top_dir = top_dir
        self.threads_per_file = threads_per_file
        self.num_of_proc = num_of_proc
        if type == 'slurm_run':
            self.filenames_to_archive = [
                'jobcomp.log', 'perf_profile.log', 'perf_stat.log', 'sched.log', 'sdiag.out',
                'sinfo.out', 'slurm_acct.out', 'slurmctld.log', 'sprio.out', 'squeue.out',
                'slurmdbd.log', 'slurmd.log'
            ]
        else:
            self.filenames_to_archive = []

        # detect zstd
        out = subprocess.run(["which", "zstd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if out.returncode != 0:
            raise Exception("Can not find zstd binary, install it")
        self.zstd_loc = out.stdout.strip()
        log.debug(f"zstd in {self.zstd_loc}")

    def compress(self, filename):
        log.debug(f"compressing {filename}")
        out = subprocess.run([
            self.zstd_loc,
            '-19',
            '--rm',
            f"-T{self.threads_per_file}",
            filename
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if out.returncode != 0:
            print(out.stdout)
            raise Exception("Can not compress {filename}!")

    def run(self):
        log.info(f"Looking in {self.top_dir} for {self.filenames_to_archive}")
        files_to_archive = []
        for root, dirs, files in os.walk(self.top_dir):
            for file in files:
                if file in self.filenames_to_archive or re.search(r'dtstart_\d+_\d+\.out', file):
                    files_to_archive.append(os.path.join(root,file))

        log.info(f"Found {len(files_to_archive)} files to archive")
        if self.num_of_proc == 1:
            for file in files_to_archive:
                self.compress(file)
        else:
            pool = multiprocessing.Pool(processes=self.num_of_proc)
            for _ in tqdm.tqdm(pool.imap_unordered(self.compress, files_to_archive), total=len(files_to_archive)):
                pass

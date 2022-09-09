#!/usr/bin/python3

import sys
import os

if len(sys.argv) < 5:
    print("Requires 4 arguments!")
    print("Usage: "+ sys.argv[0] + " open-port-number job-number array-number base-folder" )
    exit()

print("Arguments recieved in update_ports.py:")
for index, arg in enumerate(sys.argv):
    print("{}: {}".format(index, arg))
file_name = os.path.join(sys.argv[4], "run_{}_{}/etc/slurmdbd.conf".format(sys.argv[2], sys.argv[3]))
f = open(file_name, "r")
lines = f.readlines()
f.close()
for index, line in enumerate(lines):
    if "DbdPort" in line:
        lines[index] = "DbdPort=" + sys.argv[1] + "\n"

os.remove(file_name)

f = open(file_name, "w")
f.write("".join(lines))
f.close()

print("Port changed to {} in {} file".format(sys.argv[1], file_name))

file_name = os.path.join(sys.argv[4], "run_{}_{}/etc/slurm.conf".format(sys.argv[2], sys.argv[3]))
f = open(file_name, "r")
lines = f.readlines()
f.close()
for index, line in enumerate(lines):
    if "DefaultStoragePort" in line:
        lines[index]="DefaultStoragePort=" + sys.argv[1] + "\n"

os.remove(file_name)
f = open(file_name, "w")
f.write("".join(lines))
f.close()
print("Port changed to {} in {} file".format(sys.argv[1], file_name))

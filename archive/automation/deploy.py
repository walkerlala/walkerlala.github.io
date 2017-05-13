#!/usr/bin/python3
#coding:utf-8

import os
import re
import subprocess

def execute(cmd):
    """
        cmd - command to execute
        return, exit code
    """
    process = subprocess.Popen(cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (result, error) = process.communicate()
    rc = process.wait()
    if 0 != rc:
        print("Error: failed to execute command:" + cmd)
        print(error)
    return result

def not_deployed_yet(filename):
    """
        Testing whether `filename.html' existed
    """
    for existing_file in os.listdir("."):
        if re.match(filename+".html", existing_file):
            return False
    return True

# deployment start
print("walkerlala website deployment tool.")

exclude_files = [
        '000-exported'
        ]
template_file = "./000-template.html"

files_summary = []
for filename in os.listdir("."):
    if os.path.isfile(filename):
        if ((not re.findall(".*\..*", filename))
                and (filename not in exclude_files)
                and (not_deployed_yet(filename))):
            files_summary.append(filename)
            print("COPY %s => %s.html" % (template_file, filename))
            command = "cp %s %s.html" % (template_file, filename)
            execute(command)

# summary
print("")
if files_summary:
    print("Summary:")
    print("Posts added:")
    for filename in files_summary:
        print("\t" + filename)

    print("")
    print("Remember to add corresponding entries to the EXPORT file")
    print("")
else:
    print("Nothing to deploy. END")


#!/usr/bin/python3
#coding:utf-8

# pylint: disable=superfluous-parens,invalid-name,broad-except

#################################################################
# This file was originally used to pull those Latex img from the
# urls specified in the generated html from `https://upmath.me'.
# However, as I have adopted my blog system to a
# Typora-based-system(also made by myself), we do not use the
# upmath.me website anymore. So this script is useless right now.
#
# You may want to have a look at `importblog.py', which is now
# currently used to automatically produced a entry in my special
# blog system after I have finished an essay using Typora and
# transformed it to html format.
###############################################################

import re
import sys
import os
import random
import string
windows_platform = False
try:
    import readline
except Exception:
    windows_platform = True
import requests

#enable autocompletion
if not windows_platform:
    readline.parse_and_bind("tab: complete")

tex_out = "../img/tex-img/"
tex_file_len = 24
fnames = []
if len(sys.argv) == 1:
    fnames.append(input("File not specified. Please specified a file: "))
else:
    fnames.extend(sys.argv[1:])

for file in fnames:
    with open(file, "rb+") as f:
        s = []
        for line in f:
            if windows_platform:
                s.append(line.decode('utf-8'))
            else:
                s.append(line)
        stream = "".join(s)
        urls = set(re.findall(r'"(https?://[^/]*?/svg/.*?)"', stream, re.DOTALL))
        urls = list(urls)
        print("Going to replace %d urls" % len(urls))
        for url in urls:
            # note that on Windows you cannot put a # in a filename, or the
            # browser cannot find it
            name = "".join(random.choice(string.ascii_uppercase + string.digits + "-") for _ in range(tex_file_len))
            c = 0
            while os.path.exists(os.path.join(tex_out, name)):
                name = "".join(random.choice(string.ascii_uppercase + string.digits + "-") for _ in range(tex_file_len))
                c += 1
                if c > 20:
                    print("WARNING: generate over %d random file name and cannot one that doesn't exist!" % c, file=sys.stderr)
            relative_path = os.path.join(tex_out, name) + ".svg"
            fpath = os.path.abspath(relative_path)

            print("Requesting [%s](with timeout 120)" % url)
            try:
                resp = requests.get(url, timeout=120)
            except Exception as e:
                print("Exception: [%s]" % str(e))
                continue

            print("Replacing [%s] with [%s]..." % (url, fpath), end=" ")
            with open(fpath, "w+") as g:
                g.write(resp.text)
            # replace those urls in html
            stream = stream.replace('"' + url + '"', '"' + relative_path + '"')
            print("OK\n")

        f.truncate(0)
        if windows_platform:
            f.write(stream.encode('utf-8'))
        else:
            f.write(stream)
        print("Finish %s" % file)


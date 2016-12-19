#!/usr/bin/python3
#coding:utf-8

# pylint: disable=superfluous-parens,invalid-name,broad-except

import re
import sys
import os
import random
import string
import readline
import requests

#enable autocompletion
readline.parse_and_bind("tab: complete")

tex_out = "../img/tex-img/"
tex_file_len = 16
fnames = []
if len(sys.argv) == 1:
    fnames.append(input("File not specified. Please specified a file: "))
else:
    fnames.extend(sys.argv[1:])

for file in fnames:
    with open(file, "r+") as f:
        s = []
        for line in f:
            s.append(line)
        stream = "".join(s)
        urls = set(re.findall(r'"(https?://[^/]*?/svg/.*?)"', stream, re.DOTALL))
        urls = list(urls)
        print("Going to replace %d urls" % len(urls))
        for url in urls:
            name = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(tex_file_len))
            c = 0
            while os.path.exists(os.path.join(tex_out, name)):
                name = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(tex_file_len))
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
        f.write(stream)
        print("Finish %s" % file)


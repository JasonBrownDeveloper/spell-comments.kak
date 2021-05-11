#!/bin/python

import argparse
import clang.cindex
import ctypes.util
import os
import re
import subprocess
import sys
import tempfile

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Spell check only comments")
    parser.add_argument("filename", help="file to spell check")
    parser.add_argument("-l", "--lang", metavar="<str>", help="see aspell's usage")
    parser.add_argument("-std", metavar="<standard>", help="see clang's usage")
    parser.add_argument("-w", "--windows", action="store_true", help="see cygpath's usage")
    args = parser.parse_args()

    options = []

    # libclang's langage detection is bugged. Stripping the file extension and
    # passing *any* language seems to work in most cases
    options += ["-x", "c"]
    dirname = tempfile.mkdtemp(prefix="spell-comments.")
    basename = os.path.splitext(os.path.basename(args.filename))[0]
    tempname = dirname+"/"+basename
    subprocess.run(["cp", args.filename, tempname])
    args.filename = tempname

    if args.windows:
        args.filename = subprocess.run(["cygpath", "-w", args.filename], stdout=subprocess.PIPE).stdout.strip(b"\n")
        for root, dirs, files in os.walk("C:\\Program Files\\LLVM\\"):
            if re.match("C:\\\\Program Files\\\\LLVM\\\\/[0-9.]*/bin",root) and "libclang.dll" in files:
                clang.cindex.Config.set_library_file(os.path.join(root, "libclang.dll"))

    if args.std: options += ["-std", args.std]

    index = clang.cindex.Index.create()
    tu = index.parse(args.filename, args=options)

    regions = ""
    options = ["-l", args.lang] if args.lang else []
    for node in tu.cursor.get_tokens():
        if node.kind == clang.cindex.TokenKind.COMMENT:
            aspell = subprocess.Popen(["aspell", "--byte-offsets", "-a", *options],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            aout, aerr = aspell.communicate(str(node.spelling))

            lineoffset = 0
            for result in aout.split("\n"):
                token = result.split(" ")
                if result == "":
                    lineoffset = lineoffset + 1
                    continue
                elif token[0] == "&":
                    wordoffset = int(token[3][:-1])
                elif token[0] == "#":
                    wordoffset = int(token[2][:-1])
                else:
                    continue
                line = lineoffset + node.extent.start.line
                word = wordoffset + (node.extent.start.column if lineoffset == 0 else 1)
                wordlen = len(token[1])
                regions = regions+" "+str(line)+"."+str(word)+"+"+str(wordlen)+"|Error"

    subprocess.run(["rm", "-rf", os.path.dirname(args.filename)])
    print(regions.strip())

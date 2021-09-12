import codecs
import csv
import os
import game
from hacktools import common


def run(ps2):
    infile = "data/extract_FPK/Pack/Fpk/game_system_fpk/CustomVoiceStatus.csv"
    outfile = "data/csv_output.txt"

    common.logMessage("Extracting CSV to", outfile, "...")
    alllines = []
    with codecs.open(outfile, "w", "utf-8") as out:
        common.logDebug("Processing", infile, "...")
        with codecs.open(infile, "r", "shift_jis") as f:
            lines = f.readlines()
        for i in range(8, len(lines) - 16):
            line = lines[i].strip().split(",")
            if line[2] not in alllines:
                out.write(line[2] + "=\n")
                alllines.append(line[2])
            if line[5] not in alllines:
                out.write(line[5] + "=\n")
                alllines.append(line[5])
            if line[6] != "":
                out.write(line[6] + "=\n")
                alllines.append(line[6])
    common.logMessage("Done!")

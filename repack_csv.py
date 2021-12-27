import codecs
import os
import game
from hacktools import common


def run(ps2):
    outfilein = "data/extract_FPK/Pack/Fpk/game_system_fpk/CustomVoiceStatus.csv"
    if ps2:
        outfilein = outfilein.replace("extract_FPK", "extract_PS2_FPK")
    outfile = outfilein.replace("extract_", "repack_")
    infile = "data/csv_input.txt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking CSV from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as csv:
        section = common.getSection(csv, "")
        chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
        # Repack the file
        common.logDebug("Processing", outfilein, "...")
        with codecs.open(outfilein, "r", "shift_jis") as f:
            lines = f.readlines()
        common.makeFolders(os.path.dirname(outfile))
        with codecs.open(outfile, "w", "shift_jis") as fout:
            for i in range(len(lines)):
                if i < 8 or i >= len(lines) - 16:
                    fout.write(lines[i])
                    continue
                line = lines[i].strip().split(",")
                if line[2] in section and section[line[2]][0] != "":
                    line[2] = section[line[2]][0]
                if line[5] in section and section[line[5]][0] != "":
                    line[5] = section[line[5]][0]
                if line[6] != "" and line[6] in section and section[line[6]][0] != "":
                    line[6] = section[line[6]][0]
                fout.write(",".join(line) + "\n")

    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))

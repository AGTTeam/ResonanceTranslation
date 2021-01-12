import codecs
import os
import game
from hacktools import common


def run(ps2):
    if ps2:
        infolder = "data/extract_PS2_DATA/"
        outfile = "data/smd_output_PS2.txt"
    else:
        infolder = "data/extract/PSP_GAME/USRDIR/Shibusen/Message/"
        outfile = "data/smd_output.txt"
    commonfile = "data/common.txt"

    commonstr = {}
    # Read common strings from another file
    if os.path.isfile(commonfile):
        with codecs.open(commonfile, "r", "utf-8") as commonf:
            commonstr = common.getSection(commonf, "COMMON")

    common.logMessage("Extracting SMD to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
        if len(commonstr) > 0:
            out.write("!FILE:COMMON\n")
            for s in commonstr:
                out.write(s + "=\n")
        files = common.getFiles(infolder, ".smd")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            with common.Stream(infolder + file, "rb") as f:
                out.write("!FILE:" + file + "\n")
                f.seek(4)
                strnum = f.readUInt()
                for i in range(strnum):
                    f.seek(8 + i * 4)
                    offset = f.readUInt()
                    f.seek(offset + 16)
                    utfstr = game.readShiftJIS(f)
                    if utfstr not in commonstr:
                        out.write(utfstr + "=\n")
    common.logMessage("Done! Extracted", len(files), "files")

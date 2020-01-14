import codecs
import game
from hacktools import common


def run():
    infolder = "data/extract/PSP_GAME/USRDIR/Shibusen/Message/"
    outfile = "data/smd_output.txt"

    common.logMessage("Extracting SMD to", outfile, "...")
    with codecs.open(outfile, "w", "utf-8") as out:
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
                    out.write(utfstr + "=\n")
    common.logMessage("Done! Extracted", len(files), "files")

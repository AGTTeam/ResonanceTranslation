import codecs
import os
import game
from hacktools import common


def run():
    binin = "data/extract/PSP_GAME/SYSDIR/BOOT.BIN"
    binout = "data/repack/PSP_GAME/SYSDIR/BOOT.BIN"
    ebinout = "data/repack/PSP_GAME/SYSDIR/EBOOT.BIN"
    binfile = "data/bin_input.txt"

    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return

    common.logMessage("Repacking BIN from", binfile, "...")
    # load common section
    section = {}
    with codecs.open(binfile, "r", "utf-8") as bin:
        section = common.getSection(bin, "")
        chartot, transtot = common.getSectionPercentage(section)
    with common.Stream(binin, "rb") as fi:
        with common.Stream(binout, "r+b") as fo:
            # Skip the beginning and end of the file to avoid false-positives
            fi.seek(game.binrange[0])
            while fi.tell() < game.binrange[1]:
                pos = fi.tell()
                check = game.detectShiftJIS(fi)
                if check in section and section[check][0] != "":
                    common.logDebug("Replacing string at", pos)
                    fo.seek(pos)
                    endpos = fi.tell() - 1
                    newlen = game.writeShiftJIS(fo, section[check][0], endpos - pos + 1)
                    if newlen < 0:
                        fo.writeZero(1)
                        common.logError("String", section[check][0], "is too long.")
                    else:
                        fo.writeZero(endpos - fo.tell())
                fi.seek(pos + 1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
    common.copyFile(binout, ebinout)

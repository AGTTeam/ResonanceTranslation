import codecs
import json
import os
import struct
from hacktools import common, psp


def run(ps2):
    fontfile = "data/pspfont.pgf"
    fontinject = "data/extract/PSP_GAME/USRDIR/OutGame/Ending/PS2_staff_role_ex.gmo"
    fontfile_ps2 = "data/extract_PS2_DATA/file227.bin"
    infile = "data/fontconfig.txt"
    if ps2:
        fontfile = fontfile_ps2
        infile = infile.replace(".txt", "_PS2.txt")

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return
    if not ps2 and not os.path.isfile(fontfile):
        common.logError("Font file", fontfile, "not found")
        return

    common.logMessage("Repacking font from", infile, "...")
    if not ps2:
        fontin = fontinject
        fontout = fontin.replace("extract", "repack")
        psp.repackPGFData(fontfile, fontout, "data/fontconfig.txt")
    else:
        fontin = fontfile
        fontout = fontin.replace("extract", "repack")
        common.copyFile(fontin, fontout)
        with codecs.open(infile, "r", "utf-8") as f:
            section = common.getSection(f, "")
        with common.Stream(fontout, "rb+") as f:
            f.seek(0x14)
            sectionsize = f.readUInt()
            while f.tell() < sectionsize + 0x14:
                ucs = f.readUShort()
                char = struct.pack(">H", ucs).decode("utf-16-be").replace("=", "<3D>")
                if char not in section:
                    f.seek(10, 1)
                    continue
                fontdata = json.loads(section[char][0])
                f.seek(5, 1)
                # Write the x advance in place of the y one, so we can keep the state messages
                # the same, and only change what we use in game
                f.writeByte(fontdata["advance"]["x"])
                f.seek(4, 1)
    common.logMessage("Done!")

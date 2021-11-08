import codecs
import struct
import json
from hacktools import common, psp


def run(ps2):
    fontfile = "data/pspfont.pgf"
    fontfile_ps2 = "data/extract_PS2_DATA/file227.bin"
    outfile = "data/fontconfig_output.txt"

    if ps2:
        fontfile = fontfile_ps2
        outfile = outfile.replace(".txt", "_PS2.txt")
    common.logMessage("Extracting font to", outfile, "...")
    if ps2:
        with common.Stream(fontfile, "rb") as f:
            with codecs.open(outfile, "w", "utf-8") as fout:
                f.seek(0x14)
                sectionsize = f.readUInt()
                while f.tell() < sectionsize + 0x14:
                    ucs = f.readUShort()
                    data = {}
                    data["width"] = f.readByte()
                    data["height"] = f.readByte()
                    data["left"] = f.readSByte()
                    data["top"] = f.readSByte()
                    data["advance"] = {"x": f.readByte(), "y": f.readByte()}
                    bitmapptr = f.readUInt()
                    char = struct.pack(">H", ucs).decode("utf-16-be").replace("=", "<3D>")
                    fout.write(char + "=" + json.dumps(data) + "\n")
    else:
        psp.extractPGFData(fontfile, outfile)
    common.logMessage("Done!")

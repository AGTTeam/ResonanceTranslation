import os
import img
from hacktools import common

datain = "data/repack_PS2_DATA/"
datafile = "data/extract_PS2/DATA.IMG;1"
dataout = "data/repack_PS2/DATA.IMG;1"
comparedata = "data/ps2files.txt"


def run():
    common.logMessage("Repacking PS2 DATA ...")
    with open(comparedata, "r") as data:
        section = common.getSection(data, "")
    common.copyFile(datafile, dataout)
    with common.Stream(dataout, "rb+") as f:
        ps2files = img.readFiles(f)
        # Repack files
        for ps2file in common.showProgress(ps2files):
            filename = ps2file.name
            if ps2file.name in section:
                filename = section[ps2file.name].pop(0)
            filesize = os.path.getsize(datain + filename)
            f.seek(12 + ps2file.index * 12)
            f.seek(8, 1)
            f.writeUInt(filesize)
            f.seek(ps2file.offset)
            with common.Stream(datain + filename, "rb") as fin:
                f.write(fin.read())
            f.writeZero(img.sectorsize - (filesize % img.sectorsize))
    common.logMessage("Done!")

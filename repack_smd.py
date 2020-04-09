import codecs
import os
import game
from hacktools import common


def run(ps2):
    infolder = "data/extract/PSP_GAME/USRDIR/Shibusen/Message/"
    outfolder = "data/repack/PSP_GAME/USRDIR/Shibusen/Message/"
    if ps2:
        outfolder_ps2 = outfolder.replace("repack/PSP_GAME/USRDIR/", "repack_PS2_DATA/")
        common.copyFolder(outfolder, outfolder_ps2)
        return
    infile = "data/smd_input.txt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    common.logMessage("Repacking SMD from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as smd:
        files = common.getFiles(infolder, ".smd")
        for file in common.showProgress(files):
            section = common.getSection(smd, file)
            if len(section) == 0:
                common.copyFile(infolder + file, outfolder + file)
                continue
            chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
            # Repack the file
            common.logDebug("Processing", file, "...")
            size = os.path.getsize(infolder + file)
            with common.Stream(infolder + file, "rb") as fin:
                common.makeFolders(infolder + file)
                with common.Stream(outfolder + file, "wb") as f:
                    f.write(fin.read(4))
                    strnum = fin.readUInt()
                    f.writeUInt(strnum)
                    f.write(fin.read(strnum * 4))
                    fin.seek(8)
                    for i in range(strnum):
                        fin.seek(8 + 4 * i)
                        offset = fin.readUInt()
                        fin.seek(offset)
                        f.seek(offset)
                        f.write(fin.read(16))
                        check = game.readShiftJIS(fin)
                        if check in section:
                            newsjis = section[check].pop(0)
                            if len(section[check]) == 0:
                                del section[check]
                            if newsjis != "":
                                game.writeShiftJIS(f, newsjis)
                            else:
                                game.writeShiftJIS(f, check)
                        else:
                            game.writeShiftJIS(f, check)
                    f.seek(size - 1)
                    f.writeZero(1)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))

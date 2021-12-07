import codecs
import os
import game
from hacktools import common


def run(ps2):
    infolder = "data/extract/PSP_GAME/USRDIR/Shibusen/Message/"
    outfolder = "data/repack/PSP_GAME/USRDIR/Shibusen/Message/"
    mtefilein = "data/extract_FPK/Shibusen/Mission/Mission_fpk/"
    mtefileout = mtefilein.replace("extract_FPK", "repack_FPK")
    fontconfig = "data/fontconfig.txt"
    if ps2:
        outfolder_ps2 = outfolder.replace("repack/PSP_GAME/USRDIR/", "repack_PS2_DATA/")
        common.copyFolder(outfolder, outfolder_ps2)
        mtefilein = mtefileout.replace("extract_FPK", "repack_FPK")
        mtefileout = mtefileout.replace("repack_FPK", "repack_PS2_FPK")
        common.copyFolder(mtefilein, mtefileout)
        return
    infile = "data/smd_input.txt"
    chartot = transtot = 0

    if not os.path.isfile(infile):
        common.logError("Input file", infile, "not found")
        return

    glyphs = game.readFontGlyphs(fontconfig)

    common.logMessage("Repacking SMD from", infile, "...")
    with codecs.open(infile, "r", "utf-8") as smd:
        files = common.getFiles(infolder, ".smd")
        commonsection = common.getSection(smd, "COMMON")
        chartot, transtot = common.getSectionPercentage(commonsection)
        for file in common.showProgress(files):
            section = common.getSection(smd, file)
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
                        fin.seek(8 + i * 4)
                        offset = fin.readUInt()
                        fin.seek(offset)
                        f.seek(offset)
                        f.write(fin.read(16))
                        check = game.readShiftJIS(fin)
                        newsjis = ""
                        if check in section:
                            newsjis = section[check].pop(0)
                            if len(section[check]) == 0:
                                del section[check]
                        elif check in commonsection:
                            newsjis = commonsection[check][0]
                        if newsjis != "":
                            newsjis = common.wordwrap(newsjis, glyphs, game.wordwrap, game.detectTextCode, 16)
                            if newsjis.count("|") > 2:
                                common.logError("Too many line breaks:", newsjis)
                            game.writeShiftJIS(f, newsjis)
                        else:
                            game.writeShiftJIS(f, check)
                    f.seek(size - 1)
                    f.writeZero(1)

    file = "MissionTE.mte"
    mtein = "data/mte_input.txt"
    common.logMessage("Repacking MTE from", mtein, "...")
    with codecs.open(mtein, "r", "utf-8") as mte:
        section = common.getSection(mte, file)
        chartot, transtot = common.getSectionPercentage(section, chartot, transtot)
        common.logDebug("Processing", file, "...")
        common.copyFolder(mtefilein, mtefileout)
        with common.Stream(mtefilein + file, "rb") as fin:
            with common.Stream(mtefileout + file, "rb+") as f:
                for i in range(0x33):
                    basepos = 0x290 + (i * 0x1b8)
                    for strrange in [0x0, 0x1c, 0x38]:
                        fin.seek(basepos + strrange)
                        f.seek(fin.tell())
                        check = game.readShiftJIS(fin)
                        newsjis = ""
                        if check in section:
                            newsjis = section[check].pop(0)
                            if len(section[check]) == 0:
                                del section[check]
                        if newsjis != "":
                            if strrange == 0x38:
                                newsjis = common.wordwrap(newsjis, glyphs, game.wordwrap_mission, game.detectTextCode, 16)
                            game.writeShiftJIS(f, newsjis)
                            # Pad with 0s
                            while f.tell() < fin.tell():
                                f.writeByte(0)
                        else:
                            game.writeShiftJIS(f, check)
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))

import filecmp
import os
import fpk
from hacktools import common, psp


isofileps2 = "data/resonance_ps2.iso"
infolderps2 = "data/extract_PS2/"
datain = "data/extract_ps2/DATA.IMG;1"
dataout = "data/extract_PS2_DATA/"
comparedata = "data/ps2files.txt"
comparefolder = "data/extract/PSP_GAME/USRDIR/"

fileheaders = {}
fileheaders["FPK"] = ".fpk"
fileheaders["OMG"] = ".gmo"
fileheaders["MIG"] = ".gim"
fileheaders["SMD"] = ".smd"
fileheaders["// "] = ".nut"
fileheaders["~SC"] = ".prx"
fileheaders["Z:\\"] = ".txt"


class PS2File:
    name = ""
    extension = ""
    index = 0
    offset = 0
    size = 0
    unk1 = 0
    unk2 = 0
    unk3 = 0
    unk4 = 0
    unk12 = 0
    unk34 = 0


def run():
    ps2files = []
    if os.path.isfile(isofileps2):
        psp.extractIso(isofileps2, infolderps2)
        common.logMessage("Extracting PS2 DATA ...")
        common.makeFolder(dataout)
        with common.Stream(datain, "rb") as f:
            f.seek(4)
            filenum = f.readUInt()
            # Read file info
            for i in range(filenum):
                f.seek(12 + i * 12)
                ps2file = PS2File()
                ps2file.index = i
                ps2file.unk1 = f.readByte()
                ps2file.unk2 = f.readByte()
                ps2file.unk3 = f.readByte()
                ps2file.unk4 = f.readByte()
                f.seek(-4, 1)
                ps2file.unk12 = f.readUShort()
                ps2file.unk34 = f.readUShort()
                ps2file.offset = f.readUInt()
                ps2file.size = f.readUInt()
                common.logDebug(str(i) + "@" + str(f.tell() - 12) + ":" + str(vars(ps2file)))
                ps2files.append(ps2file)
            # Extract files
            for ps2file in common.showProgress(ps2files):
                f.seek(ps2file.offset * 0x800)
                ps2file.name = "file"
                if ps2file.index < 10:
                    ps2file.name += "0"
                if ps2file.index < 100:
                    ps2file.name += "0"
                ps2file.extension = ".bin"
                header = f.readString(3)
                f.seek(-3, 1)
                if header in fileheaders:
                    ps2file.extension = fileheaders[header]
                ps2file.name += str(ps2file.index) + ps2file.extension
                common.makeFolders(os.path.dirname(dataout + ps2file.name))
                with common.Stream(dataout + ps2file.name, "wb") as fout:
                    fout.write(f.read(ps2file.size))
        common.logMessage("Done!")
    return ps2files


def rename(ps2files, fpkin_ps2, fpkout_ps2):
    common.logMessage("Renaming PS2 DATA ...")
    with open(comparedata, "r") as data:
        section = common.getSection(data, "PS2")
    for ps2file in common.showProgress(ps2files):
        if ps2file.name in section:
            comparefile = section[ps2file.name].pop(0)
            common.makeFolders(dataout + os.path.dirname(comparefile))
            os.rename(dataout + ps2file.name, dataout + comparefile)
    common.logMessage("Done!")
    common.makeFolder(fpkout_ps2)
    fpk.extractFolder(fpkin_ps2, fpkout_ps2)


def compare(ps2files, fpkout, fpkin_ps2, fpkout_ps2):
    common.makeFolder(fpkout_ps2)
    common.logMessage("Comparing PS2 DATA ...")
    with open(comparedata, "w") as out:
        out.write("!FILE:PS2\n")
        foundfiles = []
        for ps2file in common.showProgress(ps2files):
            filename = ps2file.name
            extension = ps2file.extension
            comparefiles = common.getFiles(comparefolder, extension if extension != ".bin" else "")
            found = False
            for comparefile in comparefiles:
                if filecmp.cmp(comparefolder + comparefile, dataout + ps2file.name, False) and comparefile not in foundfiles:
                    out.write(filename + "=" + comparefile + "\n")
                    foundfiles.append(comparefile)
                    found = True
                    break
            if not found and extension == ".fpk":
                fpk.extract(dataout + filename, fpkin_ps2, fpkout_ps2)
                for comparefile in comparefiles:
                    fpkfolder = fpkout + comparefile.replace(".fpk", "_fpk")
                    fpkfolder_ps2 = fpkout_ps2 + filename.replace(".fpk", "_fpk")
                    dcmp = filecmp.dircmp(fpkfolder, fpkfolder_ps2)
                    if len(dcmp.left_only) == 0 and len(dcmp.right_only) == 0:
                        same = len(dcmp.diff_files) == 0
                        if not same:
                            same = True
                            for diff_file in dcmp.diff_files:
                                if ".phd" not in diff_file and ".fpk" not in diff_file:
                                    same = False
                                    break
                        if same:
                            out.write(filename + "=" + comparefile + "\n")
                            foundfiles.append(comparefile)
                            break
    common.logMessage("Done!")

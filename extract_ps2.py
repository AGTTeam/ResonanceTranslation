import filecmp
import os
import img
import fpk
from hacktools import common, psp

isofileps2 = "data/resonance_ps2.iso"
infolderps2 = "data/extract_PS2/"
datain = "data/extract_PS2/DATA.IMG;1"
dataout = "data/extract_PS2_DATA/"
comparedata = "data/ps2files.txt"
comparefolder = "data/extract/PSP_GAME/USRDIR/"


def run():
    ps2files = []
    if os.path.isfile(isofileps2):
        psp.extractIso(isofileps2, infolderps2)
        common.logMessage("Extracting PS2 DATA ...")
        common.makeFolder(dataout)
        with common.Stream(datain, "rb") as f:
            ps2files = img.readFiles(f)
            # Extract files
            for ps2file in common.showProgress(ps2files):
                f.seek(ps2file.offset)
                common.makeFolders(os.path.dirname(dataout + ps2file.name))
                with common.Stream(dataout + ps2file.name, "wb") as fout:
                    fout.write(f.read(ps2file.size))
        common.logMessage("Done!")
    return ps2files


def rename(ps2files, fpkin_ps2, fpkout_ps2):
    common.logMessage("Renaming PS2 DATA ...")
    with open(comparedata, "r") as data:
        section = common.getSection(data, "")
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

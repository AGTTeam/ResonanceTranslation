import os
from hacktools import common, psp


def run():
    workfolder = "data/work_IMG/"
    extractfolder = "data/extract/PSP_GAME/USRDIR/"
    extractfpkfolder = "data/extract_FPK/"
    workfolder = "data/work_IMG/"
    repackfolder = "data/repack/PSP_GAME/USRDIR/"
    repackfpkfolder = "data/repack_FPK/"
    common.makeFolder(repackfpkfolder)

    common.logMessage("Repacking GIM from", workfolder, "...")
    files = common.getFiles(extractfolder, ".gim") + common.getFiles(extractfpkfolder, ".gim")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        pngfile = workfolder + file.replace(".gim", ".png")
        folder = extractfolder
        repack = repackfolder
        if not os.path.isfile(folder + file):
            folder = extractfpkfolder
            repack = repackfpkfolder
        common.makeFolders(os.path.dirname(repack + file))
        common.copyFile(folder + file, repack + file)
        if not os.path.isfile(pngfile):
            continue
        gim = psp.readGIM(folder + file)
        psp.writeGIM(repack + file, gim, pngfile)

    common.logMessage("Repacking GMO from", workfolder, "...")
    files = common.getFiles(extractfolder, ".gmo") + common.getFiles(extractfpkfolder, ".gmo")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        folder = extractfolder
        repack = repackfolder
        if not os.path.isfile(folder + file):
            folder = extractfpkfolder
            repack = repackfpkfolder
        common.makeFolders(os.path.dirname(repack + file))
        common.copyFile(folder + file, repack + file)
        if os.path.isdir(workfolder + file):
            gmo = psp.readGMO(folder + file)
            for i in range(len(gmo.gims)):
                gim = gmo.gims[i]
                if gim is not None:
                    pngfile = workfolder + file + "/" + gmo.names[i] + ".png"
                    if os.path.isfile(pngfile):
                        psp.writeGIM(repack + file, gim, pngfile)

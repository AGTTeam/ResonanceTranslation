import os
from hacktools import common, psp


def run(ps2):
    if ps2:
        workfolder = "data/work_PS2_IMG/"
        extractfolder = "data/extract_PS2_DATA/"
        extractfpkfolder = "data/extract_PS2_FPK/"
        repackfolder = "data/repack_PS2_DATA/"
        repackfpkfolder = "data/repack_PS2_FPK/"
        repackfolder_psp = "data/repack/PSP_GAME/USRDIR/"
        repackfpkfolder_psp = "data/repack_FPK/"
    else:
        workfolder = "data/work_IMG/"
        extractfolder = "data/extract/PSP_GAME/USRDIR/"
        extractfpkfolder = "data/extract_FPK/"
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

    # Merge same files from PSP to PS2
    if ps2:
        repackfiles = common.getFiles(repackfolder_psp)
        for repackfile in repackfiles:
            if os.path.isfile(repackfolder + repackfile):
                common.copyFile(repackfolder_psp + repackfile, repackfolder + repackfile)
        repackfiles = common.getFiles(repackfpkfolder_psp)
        for repackfile in repackfiles:
            if os.path.isfile(repackfpkfolder + repackfile):
                common.copyFile(repackfpkfolder_psp + repackfile, repackfpkfolder + repackfile)

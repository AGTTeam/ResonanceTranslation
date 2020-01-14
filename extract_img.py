import os
from hacktools import common, psp


def run():
    infolder = "data/extract/PSP_GAME/USRDIR/"
    infolderfpk = "data/extract_FPK/"
    outfolder = "data/extract_IMG/"
    common.makeFolder(outfolder)

    common.logMessage("Extracting GIM to", outfolder, "...")
    files = common.getFiles(infolder, ".gim") + common.getFiles(infolderfpk, ".gim")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.makeFolders(os.path.dirname(outfolder + file))
        infile = (infolderfpk if "_fpk" in file else infolder) + file
        gim = psp.readGIM(infile)
        psp.drawGIM(outfolder + file.replace(".gim", ".png"), gim)
    common.logMessage("Done! Extracted", len(files), "files")

    common.logMessage("Extracting GMO to", outfolder, "...")
    files = common.getFiles(infolder, ".gmo") + common.getFiles(infolderfpk, ".gmo")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.makeFolders(outfolder + file)
        infile = (infolderfpk if "_fpk" in file else infolder) + file
        gmo = psp.readGMO(infile)
        for i in range(len(gmo.gims)):
            gim = gmo.gims[i]
            if gim is not None:
                psp.drawGIM(outfolder + file + "/" + gmo.names[i] + ".png", gim)
    common.logMessage("Done! Extracted", len(files), "files")

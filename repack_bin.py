import codecs
import os
import game
from hacktools import common, psp


def run(ps2):
    if ps2:
        binin = "data/extract_PS2/SLPS_259.12;1"
        binout = "data/repack_PS2/SLPS_259.12;1"
        binpatch = "bin_patch_PS2.asm"
    else:
        binin = "data/extract/PSP_GAME/SYSDIR/BOOT.BIN"
        binout = "data/repack/PSP_GAME/SYSDIR/BOOT.BIN"
        ebinout = "data/repack/PSP_GAME/SYSDIR/EBOOT.BIN"
        binpatch = "bin_patch.asm"
    binfile = "data/bin_input.txt"

    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return

    common.logMessage("Repacking BIN from", binfile, "...")
    # load common section
    section = {}
    with codecs.open(binfile, "r", "utf-8") as bin:
        section = common.getSection(bin, "")
        chartot, transtot = common.getSectionPercentage(section)
    elf = psp.readELF(binin)
    common.copyFile(binin, binout)
    psp.repackBinaryStrings(elf, section, binin, binout, game.detectShiftJIS, game.writeShiftJIS)
    psp.repackBinaryStrings(elf, section, binin, binout, game.detectUTF, game.writeUTF, "utf_8")
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
    common.armipsPatch(common.bundledFile(binpatch))
    if not ps2:
        common.logMessage("Signing BIN ...")
        sign_np = common.bundledExecutable("sign_np.exe")
        if not os.path.isfile(sign_np):
            common.logError("sign_np not found")
        else:
            common.execute(sign_np + " -elf {binout} {ebinout} 2".format(binout=binout, ebinout=ebinout), False)
            common.logMessage("Done!")

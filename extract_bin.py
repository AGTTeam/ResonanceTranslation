import codecs
import game
from hacktools import common, psp


def run(ps2):
    if ps2:
        binfile = "data/extract_PS2/SLPS_259.12;1"
        outfile = "data/bin_output_PS2.txt"
        outfile_psp = "data/bin_output.txt"
    else:
        binfile = "data/extract/PSP_GAME/SYSDIR/BOOT.BIN"
        outfile = "data/bin_output.txt"

    common.logMessage("Extracting BIN to", outfile, "...")
    elf = psp.readELF(binfile)
    foundstrings = psp.extractBinaryStrings(elf, [], binfile, game.detectShiftJIS)
    foundstrings = psp.extractBinaryStrings(elf, foundstrings, binfile, game.detectUTF, "utf_8")
    if ps2:
        newfound = []
        with codecs.open(outfile_psp, "r", "utf-8") as sectionfile:
            section = common.getSection(sectionfile, "")
        for foundstring in foundstrings:
            if foundstring not in section:
                newfound.append(foundstring)
        foundstrings = newfound
    with codecs.open(outfile, "w", "utf-8") as out:
        for foundstring in foundstrings:
            out.write(foundstring + "=\n")
    common.logMessage("Done! Extracted", len(foundstrings), "lines")

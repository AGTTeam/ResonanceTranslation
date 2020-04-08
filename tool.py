import os
import click
import game
import fpk
from hacktools import common, psp

version = "0.8.1"
isofile = "data/resonance.iso"
isopatch = "data/resonance_patched.iso"
patchfile = "data/patch.xdelta"
infolder = "data/extract/"
fpkin = "data/extract/PSP_GAME/USRDIR/"
fpkout = "data/extract_FPK/"
fpkin_ps2 = "data/extract_PS2_DATA/"
fpkout_ps2 = "data/extract_PS2_FPK/"
fpkrepack = "data/repack_FPK/"
outfolder = "data/repack/"
outdatafolder = "data/repack/PSP_GAME/USRDIR/"
replacefolder = "data/replace/"


@common.cli.command()
@click.option("--iso", is_flag=True, default=False)
@click.option("--ps2", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--smd", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
@click.option("--cmp", is_flag=True, default=False)
def extract(iso, ps2, bin, smd, img, cmp):
    all = not iso and not ps2 and not bin and not smd and not img
    if all or iso:
        psp.extractIso(isofile, infolder, outfolder)
        fpk.extractFolder(fpkin, fpkout)
    if all or ps2:
        import extract_ps2
        ps2files = extract_ps2.run()
        if len(ps2files) > 0:
            if cmp:
                extract_ps2.compare(ps2files, fpkout, fpkin_ps2, fpkout_ps2)
            extract_ps2.rename(ps2files, fpkin_ps2, fpkout_ps2)
    if all or bin:
        binfile = "data/extract/PSP_GAME/SYSDIR/BOOT.BIN"
        outfile = "data/bin_output.txt"
        common.logMessage("Extracting BIN to", outfile, "...")
        elf = psp.readELF(binfile)
        foundstrings = psp.extractBinaryStrings(elf, binfile, outfile, game.detectShiftJIS)
        common.logMessage("Done! Extracted", len(foundstrings), "lines")
        binfile = "data/extract_PS2/SLPS_259.12;1"
        outfile = "data/bin_output_PS2.txt"
        common.logMessage("Extracting BIN to", outfile, "...")
        elf = psp.readELF(binfile)
        foundstrings = psp.extractBinaryStrings(elf, binfile, outfile, game.detectShiftJIS)
        common.logMessage("Done! Extracted", len(foundstrings), "lines")
    if all or smd:
        import extract_smd
        extract_smd.run(False)
    if all or img:
        import extract_img
        extract_img.run(False)
        extract_img.run(True)


@common.cli.command()
@click.option("--no-iso", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--smd", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
def repack(no_iso, bin, smd, img):
    all = not bin and not smd and not img
    if all or smd:
        import repack_smd
        repack_smd.run()
    if all or bin:
        import repack_bin
        repack_bin.run()
    if all or img:
        import repack_img
        repack_img.run()
    if os.path.isdir(replacefolder):
        common.mergeFolder(replacefolder, outfolder)

    if not no_iso:
        common.logMessage("Repacking nested FPK ...")
        files = common.getFiles(fpkout, ".fpk")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            common.makeFolders(os.path.dirname(fpkrepack + file))
            fpk.repack(fpkout + file, fpkrepack + file, fpkin, fpkout, fpkrepack, "2")
        common.logMessage("Repacking FPK ...")
        files = common.getFiles(fpkin, ".fpk")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            common.makeFolders(os.path.dirname(outdatafolder + file))
            fpk.repack(fpkin + file, outdatafolder + file, fpkin, fpkout, fpkrepack)
        common.logMessage("Done!")
        psp.repackIso(isofile, isopatch, outfolder, patchfile)


if __name__ == "__main__":
    click.echo("ResonanceTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()

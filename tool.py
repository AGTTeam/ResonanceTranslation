import os
import click
import fpk
from hacktools import common, psp

version = "1.2.0"
isofile = "data/resonance.iso"
isopatch = "data/resonance_patched.iso"
patchfile = "data/patch.xdelta"
isofile_ps2 = "data/resonance_ps2.iso"
isopatch_ps2 = "data/resonance_patched_ps2.iso"
patchfile_ps2 = "data/patch_ps2.xdelta"

infolder = "data/extract/"
fpkin = "data/extract/PSP_GAME/USRDIR/"
fpkout = "data/extract_FPK/"
fpkrepack = "data/repack_FPK/"
outfolder = "data/repack/"
outdatafolder = "data/repack/PSP_GAME/USRDIR/"
replacefolder = "data/replace/"

fpkout_ps2 = "data/extract_PS2_FPK/"
data_ps2 = "data/extract_PS2_DATA/"
datarepack_ps2 = "data/repack_PS2_DATA/"
fpkrepack_ps2 = "data/repack_PS2_FPK/"
infolder_ps2 = "data/extract_PS2/"
outfolder_ps2 = "data/repack_PS2/"
replacefolder_ps2 = "data/replace_PS2/"


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
    if (all or ps2) and os.path.isfile(isofile_ps2):
        import extract_ps2
        ps2files = extract_ps2.run()
        if len(ps2files) > 0:
            if cmp:
                extract_ps2.compare(ps2files, fpkout, data_ps2, fpkout_ps2)
            extract_ps2.rename(ps2files, data_ps2, fpkout_ps2)
            common.copyFolder(data_ps2, datarepack_ps2)
            common.copyFolder(infolder_ps2, outfolder_ps2)
    if all or bin:
        import extract_bin
        extract_bin.run(False)
        if os.path.isfile(isofile_ps2):
            extract_bin.run(True)
    if all or smd:
        import extract_smd
        extract_smd.run(False)
    if all or img:
        import extract_img
        extract_img.run(False)
        if os.path.isfile(isofile_ps2):
            extract_img.run(True)


@common.cli.command()
@click.option("--no-psp", is_flag=True, default=False)
@click.option("--no-ps2", is_flag=True, default=False)
@click.option("--bin", is_flag=True, default=False)
@click.option("--smd", is_flag=True, default=False)
@click.option("--img", is_flag=True, default=False)
def repack(no_psp, no_ps2, bin, smd, img):
    if not os.path.isfile(isofile_ps2):
        no_ps2 = True
    all = not bin and not smd and not img
    if all or smd:
        import repack_smd
        repack_smd.run(False)
        if not no_ps2:
            repack_smd.run(True)
    if all or bin:
        import repack_bin
        repack_bin.run(False)
        if not no_ps2:
            repack_bin.run(True)
    if all or img:
        import repack_img
        repack_img.run(False)
        if not no_ps2:
            repack_img.run(True)
    if os.path.isdir(replacefolder):
        common.mergeFolder(replacefolder, outfolder)
    if os.path.isdir(replacefolder_ps2) and not no_ps2:
        common.mergeFolder(replacefolder_ps2, datarepack_ps2)

    if not no_psp:
        common.logMessage("Repacking nested FPK ...")
        fpk.repackFolder(fpkout, fpkrepack, fpkin, fpkout, fpkrepack, "2")
        common.logMessage("Repacking FPK ...")
        fpk.repackFolder(fpkin, outdatafolder, fpkin, fpkout, fpkrepack)
        psp.repackIso(isofile, isopatch, outfolder, patchfile)

    if not no_ps2:
        common.logMessage("Repacking nested FPK ...")
        fpk.repackFolder(fpkout_ps2, fpkrepack_ps2, data_ps2, fpkout_ps2, fpkrepack_ps2, "2")
        common.logMessage("Repacking FPK ...")
        fpk.repackFolder(data_ps2, datarepack_ps2, data_ps2, fpkout_ps2, fpkrepack_ps2)
        import repack_ps2
        repack_ps2.run()
        psp.repackIso(isofile_ps2, isopatch_ps2, outfolder_ps2, patchfile_ps2)


@common.cli.command()
def dupe():
    seen = {}
    sections = common.getSections("data/smd_input.txt")
    for section in sections:
        for line in sections[section]:
            translation = sections[section][line][0]
            if line not in seen:
                seen[line] = [translation, section, 1]
            else:
                seen[line][2] += 1
                if translation != seen[line][0]:
                    common.logMessage("{}: {}={} ({} @{})".format(section, line, translation, seen[line][0], seen[line][1]))
    for line in seen:
        if seen[line][2] > 2:
            common.logMessage("Dupe", seen[line][2], line + "=")


@common.cli.command()
def font():
    psp.extractFontData("font/jpn0.pgf", "data/fontconfig.txt")


if __name__ == "__main__":
    click.echo("ResonanceTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.runCLI(common.cli)

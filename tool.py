import os
import click
import game
from hacktools import common, psp

version = "0.8.0"
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
def extract(iso, ps2, bin, smd, img):
    all = not iso and not ps2 and not bin and not smd and not img
    if all or iso:
        psp.extractIso(isofile, infolder, outfolder)
        common.logMessage("Extracting FPK ...")
        common.makeFolder(fpkout)
        files = common.getFiles(fpkin, ".fpk")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            extractFPK(fpkin + file, fpkin, fpkout)
        common.logMessage("Done!")
    if all or ps2:
        import extract_ps2
        extract_ps2.run()
        common.logMessage("Extracting FPK ...")
        common.makeFolder(fpkout_ps2)
        files = common.getFiles(fpkin_ps2, ".fpk")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            extractFPK(fpkin_ps2 + file, fpkin_ps2, fpkout_ps2)
        common.logMessage("Done!")
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
        extract_smd.run(True)
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
            repackFPK(fpkout + file, fpkrepack + file, "2")
        common.logMessage("Repacking FPK ...")
        files = common.getFiles(fpkin, ".fpk")
        for file in common.showProgress(files):
            common.logDebug("Processing", file, "...")
            common.makeFolders(os.path.dirname(outdatafolder + file))
            repackFPK(fpkin + file, outdatafolder + file)
        common.logMessage("Done!")
        psp.repackIso(isofile, isopatch, outfolder, patchfile)


def extractFPK(fpk, folderin, folderout, add=""):
    fpkfolder = fpk.replace(folderin, folderout).replace(".fpk", "_fpk" + add) + "/"
    common.makeFolders(fpkfolder)
    with common.Stream(fpk, "rb") as f:
        f.seek(4)  # Header: FPK 0x00
        filenum = f.readUInt()
        f.seek(4, 1)  # Always 0x10
        datastart = f.readUInt()
        common.logDebug("Found", filenum, "files, data starting at", datastart)
        for i in range(filenum):
            f.seek(16 + 80 * i)
            # Filenames are always 64 bytes long, padded with 0s
            subname = f.readString(64).replace("/", "_")
            # Read starting position and size
            startpos = datastart + f.readUInt()
            size = f.readUInt()
            # Extract the file
            common.logDebug("Extracting", subname, "starting at", startpos, "with size", size)
            f.seek(startpos)
            with common.Stream(fpkfolder + subname, "wb") as newf:
                newf.write(f.read(size))
            # Nested fpk files
            if subname.endswith(".fpk"):
                extractFPK(fpkfolder + subname, folderin, folderout, "2")


def repackFPK(fpki, fpk, add=""):
    fpkfolder = fpki.replace(fpkin, fpkout).replace(".fpk", "_fpk" + add) + "/"
    with common.Stream(fpki, "rb") as fin:
        with common.Stream(fpk, "wb") as f:
            f.write(fin.read(4))  # Header: FPK 0x00
            filenum = fin.readUInt()
            f.writeUInt(filenum)
            f.write(fin.read(4))  # Always 0x10
            datastart = datapos = fin.readUInt()
            f.writeUInt(datastart)
            for i in range(filenum):
                fin.seek(16 + 80 * i)
                f.seek(fin.tell())
                f.write(fin.read(64))
                fin.seek(-64, 1)
                subname = fin.readString(64).replace("/", "_")
                filepath = fpkfolder + subname
                if os.path.isfile(filepath.replace(fpkout, fpkrepack)):
                    filepath = filepath.replace(fpkout, fpkrepack)
                filesize = os.path.getsize(filepath)
                f.writeUInt(datapos - datastart)
                f.writeUInt(filesize)
                fin.seek(8, 1)
                unk = fin.readUInt()
                f.writeUInt(unk)
                f.write(fin.read(4))  # 0x00
                f.seek(datapos)
                with common.Stream(filepath, "rb") as fpkfile:
                    f.write(fpkfile.read())
                datapos += filesize
                if f.tell() % 16 > 0:
                    padding = 16 - (f.tell() % 16)
                    f.writeZero(padding)
                    datapos += padding


if __name__ == "__main__":
    click.echo("ResonanceTranslation version " + version)
    if not os.path.isdir("data"):
        common.logError("data folder not found.")
        quit()
    common.cli()

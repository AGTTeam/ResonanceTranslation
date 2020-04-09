import os
from hacktools import common


def extractFolder(fpkin, fpkout):
    common.logMessage("Extracting FPK ...")
    common.makeFolder(fpkout)
    files = common.getFiles(fpkin, ".fpk")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        extract(fpkin + file, fpkin, fpkout)
    common.logMessage("Done!")


def extract(fpk, folderin, folderout, add=""):
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
                extract(fpkfolder + subname, folderin, folderout, "2")


def repackFolder(folderin, folderout, fpkin, fpkout, fpkrepack, add=""):
    files = common.getFiles(folderin, ".fpk")
    for file in common.showProgress(files):
        common.logDebug("Processing", file, "...")
        common.makeFolders(os.path.dirname(folderout + file))
        repack(folderin + file, folderout + file, fpkin, fpkout, fpkrepack, add)
    common.logMessage("Done!")


def repack(fpki, fpk, folderin, folderout, folderrepack, add=""):
    fpkfolder = fpki.replace(folderin, folderout).replace(".fpk", "_fpk" + add) + "/"
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
                if os.path.isfile(filepath.replace(folderout, folderrepack)):
                    filepath = filepath.replace(folderout, folderrepack)
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

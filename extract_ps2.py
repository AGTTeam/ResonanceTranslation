import os
from hacktools import common, psp


class PS2File:
    offset = 0
    size = 0
    unk1 = 0
    unk2 = 0
    unk3 = 0
    unk4 = 0
    unk12 = 0
    unk34 = 0


def run():
    isofileps2 = "data/resonance_ps2.iso"
    infolderps2 = "data/extract_PS2/"
    datain = "data/extract_ps2/DATA.IMG;1"
    dataout = "data/extract_PS2_DATA/"
    folderstart = "Z:\\SOUL\\Program\\RomData\\Master\\"

    if os.path.isfile(isofileps2):
        psp.extractIso(isofileps2, infolderps2)
        # Header size is 8508? +4 0 begin, +8/12 end?
        # First file is at 212992: Black_0.scb, length 1268, actual "Sector size" is 16384 (0x4000)
        # "File table" starts at 16384 (0x4000), len 187880 (0x2DDE8), sector size 196608 (0x30000 = 12*0x4000)
        # First FPK file is at 2228224 / 0x220000, maybe info is at 0xE44?, file is Effect\Eff00\effect.pack, size 205584 (0x32310), sec size 212992 (0x34000 = 13*0x4000)
        common.logMessage("Extracting PS2 DATA ...")
        common.makeFolder(dataout)
        with common.Stream(datain, "rb") as f:
            f.seek(4)
            filenum = f.readUInt()
            f.seek(16384)
            # Extract filenames from master.txt file
            filenames = []
            extnames = []
            filename = ""
            while True:
                byte = f.readByte()
                if byte == 0x0D:
                    filenames.append(filename)
                    if "." in filename and ".at3" not in filename:
                        extnames.append(filename.replace(folderstart, "").replace("\\", "/"))
                        common.logDebug(extnames[len(extnames) - 1])
                    filename = ""
                    f.seek(1, 1)
                    continue
                if byte == 0x00:
                    break
                filename += chr(byte)
            common.logDebug("Found " + str(len(filenames)) + " filenames.")
            common.logDebug("Found " + str(len(extnames)) + " extnames.")
            # Read file info
            maxoff = 0
            maxsize = 0
            ps2files = []
            for i in range(filenum):
                f.seek(12 + i * 12)
                ps2file = PS2File()
                ps2file.unk1 = f.readByte()
                ps2file.unk2 = f.readByte()
                ps2file.unk3 = f.readByte()
                ps2file.unk4 = f.readByte()
                f.seek(-4, 1)
                ps2file.unk12 = f.readUShort()
                ps2file.unk34 = f.readUShort()
                ps2file.offset = f.readUInt()
                ps2file.size = f.readUInt()
                if ps2file.offset > maxoff:
                    maxoff = ps2file.offset
                    maxsize = ps2file.size
                common.logDebug(str(i) + "@" + str(f.tell() - 12) + ":" + str(vars(ps2file)))
                ps2files.append(ps2file)
            common.logDebug("maxoff:" + str(maxoff) + " maxsize:" + str(maxsize))
            # Sort files
            # ps2files.sort(key=lambda x: x.offset)
            # Extract files
            for i in range(len(ps2files)):
                ps2file = ps2files[i]
                f.seek(ps2file.offset * 0x800)
                filename = "file"
                if i < 10:
                    filename += "0"
                if i < 100:
                    filename += "0"
                extension = "bin"
                header = f.readString(3)
                f.seek(-3, 1)
                if header == "FPK":
                    extension = "fpk"
                elif header == "OMG":
                    extension = "gmo"
                elif header == "MIG":
                    extension = "gim"
                elif header == "SMD":
                    extension = "smd"
                elif header == "// ":
                    extension = "scr"
                elif header == "$ty":
                    extension = "csv"
                filename += str(i) + "." + extension
                common.logDebug(str(i) + ":" + filename + ":" + str(vars(ps2file)))
                common.makeFolders(os.path.dirname(dataout + filename))
                with common.Stream(dataout + filename, "wb") as fout:
                    fout.write(f.read(ps2file.size))
        common.logMessage("Done!")

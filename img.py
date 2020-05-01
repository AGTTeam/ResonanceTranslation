from hacktools import common

sectorsize = 0x4000

fileheaders = {}
fileheaders["FPK"] = ".fpk"
fileheaders["OMG"] = ".gmo"
fileheaders["MIG"] = ".gim"
fileheaders["SMD"] = ".smd"
fileheaders["// "] = ".nut"
fileheaders["~SC"] = ".prx"
fileheaders["Z:\\"] = ".txt"


class PS2File:
    name = ""
    extension = ""
    index = 0
    offset = 0
    size = 0
    unk1 = 0
    unk2 = 0
    unk3 = 0
    unk4 = 0
    unk12 = 0
    unk34 = 0


def readFiles(f):
    ps2files = []
    f.seek(4)
    filenum = f.readUInt()
    for i in range(filenum):
        f.seek(12 + i * 12)
        ps2file = PS2File()
        ps2file.index = i
        ps2file.unk1 = f.readByte()
        ps2file.unk2 = f.readByte()
        ps2file.unk3 = f.readByte()
        ps2file.unk4 = f.readByte()
        f.seek(-4, 1)
        ps2file.unk12 = f.readUShort()
        ps2file.unk34 = f.readUShort()
        ps2file.offset = f.readUInt() * 0x800
        ps2file.size = f.readUInt()
        common.logDebug(str(i) + "@" + str(f.tell() - 12) + ":" + str(vars(ps2file)))
        f.seek(ps2file.offset)
        ps2file.extension = ".bin"
        header = f.readString(3)
        if header in fileheaders:
            ps2file.extension = fileheaders[header]
        ps2file.name += "file" + str(ps2file.index).zfill(3) + ps2file.extension
        ps2files.append(ps2file)
    return ps2files

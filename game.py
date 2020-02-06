from hacktools import common

# Control codes found in strings
codes = [0x0D, 0x0A]
# Control codes found in BIN strings
bincodes = [0x0A, 0x20]
# Ranges for BIN string locations
binrange = (1569272, 1614800)


def readShiftJIS(f, encoding="shift_jis"):
    sjis = ""
    i = 0
    while True:
        b1 = f.readByte()
        if b1 == 0x00:
            break
        elif b1 == 0x0A:
            sjis += "|"
            i += 1
        else:
            b2 = f.readByte()
            if not common.checkShiftJIS(b1, b2):
                if b2 == 0x01:
                    sjis += "UNK(" + common.toHex(b1) + common.toHex(b2) + ")"
                    i += 2
                else:
                    f.seek(-1, 1)
                    sjis += chr(b1)
                    i += 1
            else:
                f.seek(-2, 1)
                try:
                    sjis += f.read(2).decode(encoding).replace("〜", "～")
                except UnicodeDecodeError:
                    common.logError("[ERROR] UnicodeDecodeError")
                    sjis += "[ERROR" + str(f.tell() - 2) + "]"
                i += 2
    return sjis


def writeShiftJIS(f, s, maxlen=0, encoding="shift_jis"):
    x = 0
    strlen = 0
    s = s.replace("～", "〜")
    while x < len(s):
        c = s[x]
        if c == "|":
            f.writeByte(0x0A)
            strlen += 1
        elif ord(c) < 128:
            f.writeByte(ord(c))
            strlen += 1
        else:
            f.write(c.encode(encoding))
            strlen += 2
        x += 1
        if maxlen > 0 and strlen >= maxlen:
            return -1
    return strlen


def detectShiftJIS(f, encoding="shift_jis"):
    ret = ""
    sjis = 0
    while True:
        b1 = f.readByte()
        if b1 == 0:
            return ret
        if ret != "" and b1 in bincodes:
            if b1 == 0x0A:
                ret += "|"
            else:
                ret += "<" + common.toHex(b1) + ">"
            continue
        elif b1 >= 28 and b1 <= 126 and sjis > 0:
            ret += chr(b1)
            continue
        b2 = f.readByte()
        if common.checkShiftJIS(b1, b2):
            f.seek(-2, 1)
            try:
                ret += f.read(2).decode(encoding).replace("〜", "～")
                sjis += 1
            except UnicodeDecodeError:
                if ret.count("UNK(") >= 5:
                    return ""
                ret += "UNK(" + common.toHex(b1) + common.toHex(b2) + ")"
        elif len(ret) > 0 and ret.count("UNK(") < 5:
            ret += "UNK(" + common.toHex(b1) + common.toHex(b2) + ")"
        else:
            return ""

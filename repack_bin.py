import codecs
import os
import game
from hacktools import common, psp


def run(ps2):
    if ps2:
        binin = "data/extract_PS2/SLPS_259.12;1"
        binout = "data/repack_PS2/SLPS_259.12;1"
        binpatch = "bin_patch_PS2.asm"
        elfsections = [".rodata", ".sdata"]
        voiceptrs = (0x0048cf50, 0x0048d130)
        voicespace = (0x0048c3d0, 0x0048cf4f)
        baseptr = 0x00122000
        basestrptr = -0x00122000
    else:
        binin = "data/extract/PSP_GAME/SYSDIR/BOOT.BIN"
        binout = "data/repack/PSP_GAME/SYSDIR/BOOT.BIN"
        ebinout = "data/repack/PSP_GAME/SYSDIR/EBOOT.BIN"
        binpatch = "bin_patch.asm"
        elfsections = [".rodata"]
        voiceptrs = (0x089a4248, 0x089a4428)
        voicespace = (0x0898d67c, 0x0898e1ab)
        baseptr = 0x08803f8c
        basestrptr = 0x74
    binfile = "data/bin_input.txt"

    if not os.path.isfile(binfile):
        common.logError("Input file", binfile, "not found")
        return

    voicesection = {}
    if os.path.isfile("data/voice_input.txt"):
        # Read voice lines separately
        with codecs.open("data/voice_input.txt", "r", "utf-8") as voice:
            voicesection = common.getSection(voice, "")
            chartot, transtot = common.getSectionPercentage(voicesection)

    common.logMessage("Repacking BIN from", binfile, "...")
    # Replace normal BIN lines
    section = {}
    with codecs.open(binfile, "r", "utf-8") as bin:
        section = common.getSection(bin, "")
        chartot, transtot = common.getSectionPercentage(section)
    elf = psp.readELF(binin)
    common.copyFile(binin, binout)
    psp.repackBinaryStrings(elf, section, binin, binout, game.detectShiftJIS, game.writeShiftJIS, elfsections=elfsections)
    psp.repackBinaryStrings(elf, section, binin, binout, game.detectUTF, game.writeUTF, "utf_8", elfsections=elfsections)
    # Replace voice lines going with the pointer table
    if len(voicesection) > 0:
        currentvoiceptr = voicespace[0]
        voicelinetoptr = {}
        with common.Stream(binin, "rb") as fin:
            with common.Stream(binout, "rb+") as f:
                fin.seek(voiceptrs[0] - baseptr)
                ptrpos = fin.tell() - 4
                while True:
                    fin.seek(ptrpos + 4)
                    ptrpos = fin.tell()
                    if ptrpos == voiceptrs[1] - baseptr:
                        break
                    voiceptr = fin.readUInt() + basestrptr
                    fin.seek(voiceptr)
                    voiceline = game.detectShiftJIS(fin)
                    if voiceline not in voicesection:
                        continue
                    if voiceline in voicelinetoptr:
                        # Already added this, just write the pointer
                        f.seek(ptrpos)
                        f.writeUInt(voicelinetoptr[voiceline])
                    else:
                        f.seek(currentvoiceptr - baseptr)
                        newptr = f.tell() - basestrptr
                        lencheck = game.writeShiftJIS(f, voicesection[voiceline][0], voicespace[1] - currentvoiceptr)
                        f.writeByte(0x0)
                        if lencheck < 0:
                            common.logError("No more room!")
                            break
                        else:
                            currentvoiceptr = f.tell() + baseptr
                            f.seek(ptrpos)
                            f.writeUInt(newptr)
                            voicelinetoptr[voiceline] = ptrpos
    common.logMessage("Done! Translation is at {0:.2f}%".format((100 * transtot) / chartot))
    common.armipsPatch(common.bundledFile(binpatch))
    if not ps2:
        psp.signBIN(binout, ebinout, 2)

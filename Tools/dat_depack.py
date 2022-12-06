# Splits an AL DAT file into individual files
# furrtek 2022 see LICENSE
# File format info from @GMMan

import os
import struct
import sys

def getu32(pos):
	return int.from_bytes(ba[pos:pos+4], byteorder='little', signed = False)

if len(sys.argv) != 3:
	print("Usage: %s [dat file] [dest path]" % sys.argv[0])
	exit()

with open(sys.argv[1], "rb") as f_in:
	ba = bytearray(f_in.read())

if ba[0:4] != b"DAT\0":
	print("Invalid magic")
	exit()
	
entry_count = getu32(4)

for i in range(0, entry_count):
	offset = getu32(8 + i * 8)
	size = getu32(12 + i * 8)

	with open(sys.argv[2] + "\\" + os.path.basename(sys.argv[1]).rsplit('.', 1)[0] + "_" + str(i) + ".bin", "wb") as f_out:
		f_out.write(ba[offset: offset + size])

print("Depacked %d files" % entry_count)
exit()

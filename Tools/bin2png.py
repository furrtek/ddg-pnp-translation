# Converts bin (TXM) files to png files, accepts single files or directories
# furrtek 2022 see LICENSE
# File format info from @GMMan

import os
import sys
from PIL import Image

def getu32(pos):
	return int.from_bytes(ba[pos:pos+4], byteorder='little', signed = False)

def getu16(pos):
	return int.from_bytes(ba[pos:pos+2], byteorder='little', signed = False)
	
def getrgba(pos):
	return (ba[pos], ba[pos+1], ba[pos+2], min(255, ba[pos+3] * 2))

def convert(infile, outfile):
	global ba

	with open(infile, "rb") as f_in:
		ba = bytearray(f_in.read())
		
	ImageSourcePixelFormat = ba[0]
	ImageVideoPixelFormat = ba[1]
	ImageWidth = getu16(2)
	ImageHeight = getu16(4)
	ImageBufferBase = getu16(6)
	ClutPixelFormat = ba[8]
	Misc = ba[9]
	ClutWidth = getu16(10)
	ClutHeight = getu16(12)
	ClutBufferBase = getu16(14)

	read_pos = 16	# Skip header
	
	image = Image.new("RGBA", (ImageWidth, ImageHeight))

	if ImageSourcePixelFormat == 0x00:
		# PSMCT32
		for py in range(0, ImageHeight):
			for px in range(0, ImageWidth):
				image.putpixel((px, py), getrgba(read_pos))
				read_pos += 4
	else:
		# Palettized
		ClutSize = ClutWidth * ClutHeight
		
		# Extract and convert CLUT
		clut = []
		for i in range(0, ClutSize):
			clut.append(getrgba(read_pos))
			read_pos += 4

		if ImageSourcePixelFormat == 0x13:
			# PSMT8
			for py in range(0, ImageHeight):
				for px in range(0, ImageWidth):
					image.putpixel((px, py), clut[ba[read_pos]])
					read_pos += 1
		elif ImageSourcePixelFormat == 0x14:
			# PSMT4
			parity = False
			for py in range(0, ImageHeight):
				for px in range(0, ImageWidth):
					if parity == False:
						idx = ba[read_pos]
						read_pos += 1
						v = idx & 15
					else:
						v = idx >> 4
					image.putpixel((px, py), clut[v])
					parity = not parity
		
		else:
			print("Pixel format 0x%02X not supported for %s" % (ImageSourcePixelFormat, infile))
			exit()

	image.save(outfile)
	print("Converted " + os.path.basename(infile))

if len(sys.argv) != 3 or (os.path.isdir(sys.argv[1]) != os.path.isdir(sys.argv[2])):
	print("Usage: %s [bin file or directory] [png file or directory]" % sys.argv[0])
	exit()

if os.path.isdir(sys.argv[1]):
	for f in os.listdir(sys.argv[1]):
		if f.endswith(".bin"):
			convert(sys.argv[1] + f, sys.argv[2] + f.rsplit('.', 1)[0] + ".png")
else:
	convert(sys.argv[1], sys.argv[2])

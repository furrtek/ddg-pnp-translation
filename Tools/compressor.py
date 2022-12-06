# Generates an AL DAT from a directory and compresses it to an ALLZ file
# TODO: Shitty simple test method: only produce "flag 0" blocks with direct copies (no actual compression)
# furrtek 2022 see LICENSE
# File format info from @GMMan

import os
import struct
import hashlib

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Generate DAT file
directory = os.fsencode("dats/new/")

bin_count = 0
for file in os.listdir(directory):
	filename = os.fsdecode(file)
	if filename.endswith(".bin"):
		#print(os.path.join(directory, filename))
		bin_count += 1
		
print("Files found: %d" % bin_count)

ba = bytearray()
with open("new.dat", "wb") as f_out:
	f_out.write("DAT\0".encode('ascii'))		# Magic
	f_out.write(struct.pack("<L", bin_count))	# Number of entries

	# Concat all data, write start points and lengths
	for n in range(0, bin_count):
		fn = "dats/new/dat_" + str(n) + ".bin"
		#starts.append(len(ba))
		f_out.write(struct.pack("<L", len(ba) + (4 + 4 + bin_count*8)))
		#lengths.append(os.path.getsize(fn))
		f_out.write(struct.pack("<L", os.path.getsize(fn)))
		with open(fn, "rb") as f_in:
			ba += bytearray(f_in.read())
	f_out.write(ba)

#print(md5("out.bin"))	# Hash of original decompressed file
#print(md5("new.dat"))	# Hash of new DAT file - should be different

# Even shittier method: just plain copy with the first U/B value (what's the size limit ? 32 bits ?)
#with open("out.bin", "rb") as f_in:	# Use this to compare decompressed results (MD5s should be identical)
with open("new.dat", "rb") as f_in:
	ba = bytearray(f_in.read())
	
with open("new_compressed.bin", "wb") as f_out:
	f_out.write("ALLZ".encode('ascii'))
	f_out.write(bytearray([1, 1, 11, 0, 0xD0, 0x71, 0x24, 0x00]))	# Startup values, 2388432
	# The encoded value must be (remainder, binary)(power of two, unary)
	# 2388432: 2^21 + 291280
	# 291280: 1000111000111010000
	# 21 unary: 0111111111111111111111
	# 1000111000111010000 0111111111111111111111
	# 1 00011100 01110100 00011111 11111111 11111111 = 01 1C 74 1F FF FF
	f_out.write(bytearray([0xFF, 0xFF, 0x1F, 0x74, 0x1C, 0x01]))
	f_out.write(ba)
	# It works !

# Decompress recompressed file to see if it matches the correctly decompressed one
#os.system("..\main.exe new_compressed.bin new_decompressed.bin")
#print(md5("out.bin"))	# Hash of correctly decompressed file
#print(md5("new_decompressed.bin"))



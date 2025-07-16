#!/usr/bin/env python3
# Converts an audio file to a block of constant bytes which can be placed in audio.h
# The first two lines will be the header (wavHeader) and the remainder will be the audio
# (defaultAudio)
import sys

OCTS_PER_LINE = 22
DEFAULT_OUTPUT_FN = 'audio.txt'


def main(input_fn, output_fn=DEFAULT_OUTPUT_FN, octs_per_line=OCTS_PER_LINE):
	with open(input_fn, 'rb') as f:
		data = f.read().hex()

	output = ""
	for i in range(0, len(data), 2):
		if i == 0:
			output = "  "
		elif not i % (octs_per_line * 2):
			output += "\n  "
		else:
			output += " "
		output += "0x%s," % data[i:i+2]

	with open(output_fn, 'w') as f:
		f.write(output)


if __name__ == '__main__':
	main(sys.argv[-1])

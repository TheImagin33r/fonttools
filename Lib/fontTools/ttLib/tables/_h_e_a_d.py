from __future__ import print_function, division
from fontTools.misc.py23 import *
from fontTools.misc import sstruct
from fontTools.misc.textTools import safeEval, num2binary, binary2num
from . import DefaultTable
import time
import calendar


headFormat = """
		>	# big endian
		tableVersion:       16.16F
		fontRevision:       16.16F
		checkSumAdjustment: I
		magicNumber:        I
		flags:              H
		unitsPerEm:         H
		created:            Q
		modified:           Q
		xMin:               h
		yMin:               h
		xMax:               h
		yMax:               h
		macStyle:           H
		lowestRecPPEM:      H
		fontDirectionHint:  h
		indexToLocFormat:   h
		glyphDataFormat:    h
"""

class table__h_e_a_d(DefaultTable.DefaultTable):
	
	dependencies = ['maxp', 'loca']
	
	def decompile(self, data, ttFont):
		dummy, rest = sstruct.unpack2(headFormat, data, self)
		if rest:
			# this is quite illegal, but there seem to be fonts out there that do this
			assert rest == "\0\0"
	
	def compile(self, ttFont):
		self.modified = int(time.time() - mac_epoch_diff)
		data = sstruct.pack(headFormat, self)
		return data
	
	def toXML(self, writer, ttFont):
		writer.comment("Most of this table will be recalculated by the compiler")
		writer.newline()
		formatstring, names, fixes = sstruct.getformat(headFormat)
		for name in names:
			value = getattr(self, name)
			if name in ("created", "modified"):
				try:
					value = time.asctime(time.gmtime(max(0, value + mac_epoch_diff)))
				except ValueError:
					value = time.asctime(time.gmtime(0))
			if name in ("magicNumber", "checkSumAdjustment"):
				if value < 0:
					value = value + 0x100000000
				value = hex(value)
				if value[-1:] == "L":
					value = value[:-1]
			elif name in ("macStyle", "flags"):
				value = num2binary(value, 16)
			writer.simpletag(name, value=value)
			writer.newline()
	
	def fromXML(self, name, attrs, content, ttFont):
		value = attrs["value"]
		if name in ("created", "modified"):
			value = calendar.timegm(time.strptime(value)) - mac_epoch_diff
		elif name in ("macStyle", "flags"):
			value = binary2num(value)
		else:
			value = safeEval(value)
		setattr(self, name, value)


def calc_mac_epoch_diff():
	"""calculate the difference between the original Mac epoch (1904)
	to the epoch on this machine.
	"""
	safe_epoch_t = (1972, 1, 1, 0, 0, 0, 0, 0, 0)
	safe_epoch = time.mktime(safe_epoch_t) - time.timezone
	# This assert fails in certain time zones, with certain daylight settings
	#assert time.gmtime(safe_epoch)[:6] == safe_epoch_t[:6]
	seconds1904to1972 = 60 * 60 * 24 * (365 * (1972-1904) + 17) # thanks, Laurence!
	return int(safe_epoch - seconds1904to1972)

mac_epoch_diff = calc_mac_epoch_diff()


_months = ['   ', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug',
		'sep', 'oct', 'nov', 'dec']
_weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

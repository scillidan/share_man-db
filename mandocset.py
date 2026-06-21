#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
DocsetMaker - generate Dash/Zeal docsets from man pages

Based on: https://github.com/yanpas/mandocset (2017, author: yanpas)

Changes from upstream:
- Only skip Content-Type header when the line actually starts with
  "Content-type:" (prevents data loss when using converters like pandoc
  that do not emit HTTP headers)
- Tighten section-directory regex to ^man(\d\w*)$ to avoid false matches
  on unrelated directories
- Fix resource leaks: close input file handle and wait on decompressor
  subprocess before returning
- Use binary I/O throughout to handle non-UTF-8 man pages gracefully
- Remove unused typing import
'''

import sqlite3, argparse, os, re, subprocess, sys
import shutil


def getPlist(name: str) -> str:
	identifier = name.split('_')[0]
	return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{identifier}</string>
	<key>CFBundleName</key>
	<string>{name.replace('_', ' ')}</string>
	<key>DocSetPlatformFamily</key>
	<string>{identifier.lower()}</string>
	<key>isDashDocset</key>
	<true/>
</dict>
</plist>
'''


def toHtml(executable, inf: str, outdir: str, basedir: str):
	name = os.path.basename(inf)
	with open(inf, 'rb') as raw_f:
		input_f = raw_f
		decoder = None
		for suff, dec_cmd in [('.gz', ['gzip', '-d']), ('.bz2', ['bzip2', '-d'])]:
			if inf.endswith(suff):
				name = name.rsplit(suff, 1)[0]
				decoder = subprocess.Popen(dec_cmd, stdin=raw_f, stdout=subprocess.PIPE)
				input_f = decoder.stdout
				break
		try:
			subp = subprocess.Popen(executable, stdout=subprocess.PIPE, stdin=input_f)
			first_line = subp.stdout.readline()
			outpath = os.path.join(basedir, name) + '.html'
			with open(os.path.join(outdir, outpath), 'wb') as f:
				if not first_line.lower().startswith(b'content-type:'):
					f.write(first_line)
				f.write(subp.stdout.read())
			if subp.wait() != 0:
				print(executable[0], "error:", subp.returncode, file=sys.stderr)
		finally:
			if decoder:
				decoder.wait()
	return outpath


def getType(n):
	if n == 1:
		return 'Command'
	elif n == 2:
		return 'Service'
	elif n == 3:
		return 'Function'
	else:
		return 'Object'


class DocsetMaker:
	fldre  = re.compile(r'^man(\d\w*)$')
	manfre = re.compile(r'(.+)\..*?\d.*')

	def __init__(self, outname, executable: str):
		self.outname = outname
		self.dups = set()
		self.db = None
		self.executable = executable.split()

	def __enter__(self):
		os.makedirs(self.outname + '.docset/Contents/Resources/Documents')
		self.db = sqlite3.connect(self.outname + '.docset/Contents/Resources/docSet.dsidx')
		self.db.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
		self.db.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
		with open(self.outname + '.docset/Contents/Info.plist', 'w') as plist:
			plist.write(getPlist(self.outname))
		return self

	def __exit__(self, *oth):
		self.db.close()

	def scanDirectory(self, path1, it, mannum):
		outbase = self.outname + '.docset/Contents/Resources/Documents'
		os.makedirs(os.path.join(outbase, it), exist_ok=True)
		for jt in os.listdir(path1):
			manf = os.path.join(path1, jt)
			if os.path.isfile(manf) and re.match(DocsetMaker.manfre, jt):
				print('\tman', jt)
				name_for_db = re.match(DocsetMaker.manfre, jt).group(1)
				dashtype = getType(mannum)
				new_el = (mannum, name_for_db)
				if new_el not in self.dups:
					outpath = toHtml(self.executable, manf, outbase, it)
					self.db.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?);',
							[name_for_db, dashtype, outpath])
					self.dups.add(new_el)
				else:
					print('\tduplicate skipped', jt)

	def addToDocset(self, indir):
		self.db.execute("BEGIN")
		for it in os.listdir(indir):
			path1 = os.path.join(indir, it)
			if os.path.isdir(path1):
				mo = re.match(DocsetMaker.fldre, it)
				if mo:
					print('dir', it)
					self.scanDirectory(path1, it, int(mo.group(1)[0]))
		self.db.commit()


def main():
	argp = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	argp.add_argument('-p', '--paths', help='paths with unpacked archive, order matters', nargs='+', required=True)
	argp.add_argument('-o', '--out', help='new docset name', required=True)
	argp.add_argument('-f', help='force outdir', action='store_true')
	argp.add_argument('-i', help='x1 icon (16x16)', metavar='icon.png')
	argp.add_argument('-I', help='x2 icon (32x32)', metavar='icon@2x.png')
	argp.add_argument('-e', default='man2html -r',
		help=('Executable with arguments which reads from stdin and writes to stdout.'
			' Alternatively "pandoc -f man -t html" may be used'))
	args = argp.parse_args()
	if ' ' in args.out:
		exit('spaces are forbidden in outname')
	outpath = args.out + '.docset'
	if os.path.exists(outpath):
		if args.f:
			shutil.rmtree(outpath)
		else:
			exit('path already exists, exiting (use "-f" to ignore this)')
	with DocsetMaker(args.out, args.e) as dsm:
		for path in args.paths:
			dsm.addToDocset(path)
	for name, path in [('icon.png', args.i), ('icon@2x.png', args.I)]:
		if path:
			shutil.copyfile(path, os.path.join(outpath, name))


if __name__ == '__main__':
	main()

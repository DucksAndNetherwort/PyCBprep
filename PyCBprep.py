#!/usr/bin/env python3

import argparse
import pathlib
from dotenv import dotenv_values
import xml.etree.ElementTree as xml
from PIL import Image #needs to be installed as it's not stock, also I'm using pillow. It wouldn't install so I did python3 -m pip install -U --force-reinstall pip, then it worked just fine
from PIL import ImageOps
import logging
import subprocess
import tempfile

if(not __name__ == '__main__'): #prevent attempted use as a library without having to have an indent on every line
	print("this is a standalone program, not a library")
	exit()

parser = argparse.ArgumentParser( #get an argument parser
	prog = 'PyCBprep',
	description = 'Takes an svg and renders it out to an appropriately scaled and padded png for exposure on a dlp 3d printer',
	epilog = 'Written by Ducks And Netherwort (ducksnetherwort.ddns.net, github.com/DucksAndNetherwort)'
)

#define all our arguments
parser.add_argument('svgFilename', metavar='input', type=argparse.FileType('r'), help='filename for input svg')
parser.add_argument('output', type=argparse.FileType('w+b'), help='output image filename')
parser.add_argument('--config', default='config.env', type=pathlib.Path, help='alternate .env config file')
parser.add_argument('--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='logging level')
parser.add_argument('--rastercommand', default='configfile', help='custom command for converting svg to png raster. uses the one supplied by the config file by default')
parser.add_argument('-i', '--invert', action='store_true', help='invert colors, leaves them alone if not specified')

args = parser.parse_args() #parse said arguments

logging.basicConfig(level=args.loglevel) #set up logging
log = logging.getLogger("PyCBprep")

log.debug('parsed args and started logger')

conf = dotenv_values(args.config) #load configuration file
log.debug('loaded config file')
tree = xml.parse(args.svgFilename) #grab the svg
root = tree.getroot()
log.debug('grabbed svg')
rasterCommand = conf.get('RASTERCOMMAND') if args.rastercommand == 'configfile' else args.rastercommand #get the terminal command for converting svg to png
log.debug(f'raster command: {rasterCommand}')

#let's extract those svg dimentions in mm, shall we?
if root.attrib.get('width')[-2::] in ['cm', 'mm'] and root.attrib.get('height')[-2::] in ['cm', 'mm']: #make sure the svg is using the right units
	svgWidthMm = float(root.attrib.get('width')[:-2]) * (10 if root.attrib.get('width')[-2::] == 'cm' else 1)
	svgHeightMm = float(root.attrib.get('height')[:-2]) * (10 if root.attrib.get('width')[-2::] == 'cm' else 1)

	log.info(f'svg width in mm: {svgWidthMm}')
	log.info(f'svg height in mm: {svgHeightMm}')
else:
	log.error('svg dimentions not in centimeters or millimeters')
	raise Exception('give me centimeters or millimeters')
log.debug('got svg dimentions')

log.debug("done setting up, on to the main bit!") #time for the main part!

svgRasterWidth = int(int(conf.get('PRINTERXPX')) / (float(conf.get('PRINTERXMM')) / svgWidthMm)) #calculate the needed r=svg dimentions in pixels
svgRasterHeight = int(int(conf.get('PRINTERYPX')) / (float(conf.get('PRINTERYMM')) / svgHeightMm))
log.debug(f'calculated raster dimentions as {svgRasterWidth} by {svgRasterHeight}')

with tempfile.NamedTemporaryFile() as tmp: #get a tempfile with a name, so we can pass it to the raster command
	log.debug('opened tempfile')
	finalRasterCommand = (rasterCommand.format(outputPng=tmp.name, rasterWidth=svgRasterWidth, rasterHeight=svgRasterHeight, inputSvg=args.svgFilename.name)) #run said raster command
	log.debug(f'final raster command: {finalRasterCommand}')
	log.info(f'rasterising {args.svgFilename.name}')
	out = subprocess.run(finalRasterCommand, shell=True)
	log.debug(f'raster command returned {out.returncode}')
	with Image.open(tmp) as rasterSvg: #get it's output
		bg = Image.new('RGB', (int(conf.get('PRINTERXPX')), int(conf.get('PRINTERYPX'))), (255, 255, 255)) #blank canvas the size of the printer, so we can place our properly (maybe) scaled png on it
		log.debug('made background')
		bg.paste(rasterSvg, (int(int(conf.get('PRINTERXPX')) / 2 - svgRasterWidth / 2), int(int(conf.get('PRINTERYPX')) / 2 - svgRasterHeight / 2)), rasterSvg.convert('RGBA')) #paste the rasterised svg over the blank image

		if args.invert:
			log.debug('inverting colors')
			ImageOps.invert(bg).save(args.output) #save the result
		else:
			bg.save(args.output)

		log.debug('image generated, closing file')
		args.output.close()
		log.info(f'output image saved to {args.output.name}')

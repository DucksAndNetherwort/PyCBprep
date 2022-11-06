#!/usr/bin/env python3

import argparse
from dotenv import dotenv_values
import xml.etree.ElementTree as xml
import logging
import os

if(not __name__ == '__main__'): #prevent attempted use as a library without having to have an indent on every line
	print("this is a standalone program, not a library")
	exit()

parser = argparse.ArgumentParser( #get an argument parser
	prog = 'render.py',
	description = 'Takes an svg and renders it out to an appropriately scaled and padded png for exposure on a dlp 3d printer',
	epilog = 'Written by Ducks And Netherwort (ducksnetherwort.ddns.net, github.com/DucksAndNetherwort) for MakeItZone (makeit.zone, github.com/MakeItZone)'
)

#define all our arguments
parser.add_argument('svgFilename', metavar='input', type=argparse.FileType('r'), help='filename for input svg')
parser.add_argument('--config', default='renderconf.env', type=argparse.FileType('r'), help='alternate .env config file')
parser.add_argument('--loglevel', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help='logging level')

args = parser.parse_args() #parse said arguments

logging.basicConfig(level=args.loglevel) #set up logging
log = logging.getLogger("renderpy")

log.debug('parsed args and started logger')

conf = dotenv_values('renderconf.env') #load configuration file
log.debug('loaded config file')
tree = xml.parse(args.svgFilename) #grab the svg
root = tree.getroot()
log.debug('grabbed svg')
log.debug(root.attrib.get('width'))


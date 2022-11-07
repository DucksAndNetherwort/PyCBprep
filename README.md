# PyCBprep

usage: PyCBprep [-h] [--config CONFIG]
                [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                [--rastercommand RASTERCOMMAND] [-i]
                input output

Takes an svg and renders it out to an appropriately scaled and padded png for
exposure on a dlp 3d printer

positional arguments:
  input                 filename for input svg
  output                output image filename

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       alternate .env config file
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        logging level
  --rastercommand RASTERCOMMAND
                        custom command for converting svg to png raster. uses
                        the one supplied by the config file by default
  -i, --invert          invert colors, leaves them alone if not specified
# LR Preview JPEG Extractor

## Overview
This script is designed to extract the largest JPEG image embedded within Adobe Lightroom's preview files (.lrprev). It can process individual .lrprev files or directories containing multiple .lrprev files. The script also supports querying a Lightroom catalog (.lrcat) to retrieve the original file path for more organized output.

## :warning: Warning 
 - Use a copy of your Lightroom catalog and preview files with this script.
 - Tested with Lightroom v6.13 catalog on macOS

## Features
- Extract the largest JPEG image from .lrprev files.
- Process a single file or a directory of files.
- Query Lightroom catalog (.lrcat) for original file paths.
- Optionally include image dimensions in the extracted JPEG filename.

## Requirements
- Python 3.6 or newer
- Pillow library for image processing
- argparse for command-line options parsing

## Installation
Ensure you have [uv](https://docs.astral.sh/uv/) on your system. You can install the required dependencies by running:

```
uv sync
```

## Usage

### Command-Line Arguments
- `-d` or `--input-dir`: Path to your Lightroom directory(.lrdata) containing .lrprev files (optional).
- `-f` or `--input-file`: Path to your .lrprev file (optional).
- `-o` or `--output-directory`: Path to the output directory where extracted JPEGs will be saved (required).
- `-l` or `--lightroom-db`: Path to the Lightroom catalog file (.lrcat) (optional).
- `--include-size`: Include the image's dimensions in the filename of the output JPEG (optional).

### Examples

**Extracting from a Single File**

```
python lrprev-extract.py -f /path/to/file.lrprev -o /path/to/output
```

**Extracting from a Directory**

```
python lrprev-extract.py -d /path/to/lrcatalog/directory.lrdata -o /path/to/output
```

**Including Image Size in Filename**

```
python lrprev-extract.py -d /path/to/lrcatalog/directory.lrdata -o /path/to/output --include-size
```

**Specifying Lightroom Database**

```
python lrprev-extract.py -d /path/to/lrcatalog/directory.lrdata -o /path/to/output -l /path/to/lrcatalog/catalog.lrcat
```

## Note
- Either `--input-dir` or `--input-file` must be supplied. Both cannot be used simultaneously.
- The script prints the progress and any errors encountered during execution to the console.
- Ensure the output directory exists or has the necessary permissions to be created.
- Default path for Lightroom catalog are:
    - Windows: \Users\[user name]\Pictures\Lightroom.
    - macOS: /Users/[user name]/Pictures/Lightroom.

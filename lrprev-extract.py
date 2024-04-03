import re
import sys
from pathlib import Path
from PIL import Image
import io
import sqlite3
import argparse

include_size = False

def extract_jpeg_dimensions(jpeg_bytes):
    """Extract dimensions of a JPEG image, handling exceptions gracefully."""
    try:
        with Image.open(io.BytesIO(jpeg_bytes)) as img:
            return img.width, img.height
    except Exception as e:
        print(f"Error processing JPEG image: {e}")
        return None, None  # Return None values for width and height

def extract_uuid_from_filename(file_path):
    """Extract UUID from the file's name."""
    uuid_pattern = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    match = uuid_pattern.search(file_path.name)
    if match:
        return match.group(0)
    else:
        print(f"UUID could not be extracted from the filename: {file_path}")
        return None

def get_original_file_path(db_path, uuid):
    """Query the SQLite database for the directory path of the JPEG file based on the given UUID."""
    sql_query = """
    SELECT agfile.id_global as uuid, root.absolutePath, agfolder.pathFromRoot, agfile.baseName
    from AgLibraryFile agfile
    inner join AgLibraryFolder agfolder on agfolder.id_local = agfile.folder
    inner join AgLibraryRootFolder root on root.id_local = agfolder.rootFolder
    where agfile.id_global = ?
    """
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql_query, (uuid,))
        result = cur.fetchone()
        conn.close()
        if result:
            uuid, absolutePath, pathFromRoot, baseName = result
            # Remove first slash from the absolutePath
            full_path = Path(absolutePath[1:] + pathFromRoot)
            return full_path, baseName
        else:
            print(f"No entry found for UUID: {uuid}")
            return None, None
    except Exception as e:
        print(f"Database query failed: {e}")
        return None, None


def extract_largest_jpeg_from_lrprev(lrprev_path, output_directory, db_path):
    """Extract the last JPEG image from a .lrprev file and save it to the specified output directory."""
    file_path = Path(lrprev_path)
    
    if not file_path.exists() or not file_path.is_file():
        print(f"The file {lrprev_path} does not exist.")
        return

    with open(file_path, 'rb') as file:
        file_contents = file.read()

    uuid = extract_uuid_from_filename(file_path)
    if not uuid:
        return
    
    output_path = Path(output_directory)

    if db_path:
        # Query the original file path using the UUID
        original_file_path, base_name = get_original_file_path(db_path, uuid)
        if original_file_path:
            print(f"Original file path for UUID {uuid}: {original_file_path}")
            # Construct a relative path for the output based on the original file pathE
            final_output_directory = output_path / original_file_path
        else:
            print(f"Original file path for UUID {uuid} not found.")
            # Use default output directory if original path not found
            final_output_directory = output_path / "_path_not_found"
            base_name = uuid
    else:
        final_output_directory = output_path
        base_name = uuid

    final_output_directory.mkdir(parents=True, exist_ok=True)    

    start_markers = [m.start() for m in re.finditer(b'\xFF\xD8', file_contents)]
    end_markers = [m.end() for m in re.finditer(b'\xFF\xD9', file_contents)]

    if start_markers and end_markers:
        last_start = start_markers[-1]
        last_end = end_markers[-1]
        jpeg_contents = file_contents[last_start:last_end]
        width, height = extract_jpeg_dimensions(jpeg_contents)
        if width and height:
            new_filename = f"{base_name}.jpg"

            if include_size:
                new_filename = f"{base_name}_{width}x{height}.jpg"                

            jpeg_path = final_output_directory / new_filename
            
            with open(jpeg_path, 'wb') as jpeg_file:
                jpeg_file.write(jpeg_contents)
            
            print(f"JPEG image extracted and saved to {jpeg_path}")
        else:
            print("Error extracting the last JPEG image dimensions.")


def process_directory(directory_path, output_directory, db_path):
    """Recursively process all .lrprev files in a directory and save extracted JPEGs to the specified output directory."""
    path = Path(directory_path)
    if not path.exists() or not path.is_dir():
        print(f"The directory {directory_path} does not exist or is not a directory.")
        return

    files_processed = 0
    for lrprev_file in path.rglob('*.lrprev'):
        files_processed += 1
        print(f"Processing file {files_processed}: {lrprev_file}")
        extract_largest_jpeg_from_lrprev(lrprev_file, output_directory, db_path)

def parse_args():
    """Parse command-line arguments with flags."""
    parser = argparse.ArgumentParser(description="Extract the largest JPEG from .lrprev files.")
    parser.add_argument('-d', '--input-dir', type=str, required=False, help='Path to your lightroom directory(.lrdata)')
    parser.add_argument('-f', '--input-file', type=str, required=False, help='Path to your file(.lrprev)')
    parser.add_argument('-o', '--output-directory', type=str, required=True, help='Path to output directory')
    parser.add_argument('-l', '--lightroom-db', type=str, required=False, help='Path to the lightroom catalog(.lrcat)')
    parser.add_argument('--include-size', action='store_true', help='Include image size information in the file name output')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    # Check if neither input_dir nor input_file is supplied
    if not args.input_dir and not args.input_file:
        raise ValueError("Either --input-dir or --input-file must be supplied.")
    
    # Check if both input_dir and input_file are supplied
    if args.input_dir and args.input_file:
        raise ValueError("Both --input-dir and --input-file were supplied. Only one is allowed at a time.")


    input_path = args.input_dir or args.input_file
    output_directory = args.output_directory
    include_size = args.include_size
    db_path = args.lightroom_db

    path = Path(input_path)
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)  # Ensure the output directory exists

    if path.is_dir():
        process_directory(path, output_directory, db_path)
    elif path.is_file():
        extract_largest_jpeg_from_lrprev(path, output_directory, db_path)
    else:
        print("The provided path does not exist or is not a directory or file.")


#!/usr/bin/env python3

# copyscripts.py

import os
import sys
import argparse
from datetime import datetime
import shutil
from collections import defaultdict

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Generate a .GPT file containing contents of specified scripts."
    )
    parser.add_argument(
        '-e', '--extensions',
        nargs='+',
        help='Additional file extensions to include (e.g., -e txt md)'
    )
    parser.add_argument(
        '-f', '--folders',
        nargs='+',
        help='Additional subdirectories to search for files (e.g., -f utils helpers)'
    )
    return parser.parse_args()

def get_current_directory():
    return os.getcwd()

def get_directory_name(path):
    return os.path.basename(os.path.normpath(path))

def get_timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def backup_existing_gpt_files(current_dir, work_dir_name):
    """
    Renames existing .GPT files to .GPTBAK and moves them to the backup directory.
    """
    backup_base = r'C:\code\backups'
    backup_dir = os.path.join(backup_base, work_dir_name, 'copyscript-backups')

    # Create backup directory if it doesn't exist
    try:
        os.makedirs(backup_dir, exist_ok=True)
        print(f"Backup directory ensured at '{backup_dir}'.")
    except Exception as e:
        print(f"Error creating backup directory '{backup_dir}': {e}")
        sys.exit(1)

    # List all .GPT files in the current directory
    for item in os.listdir(current_dir):
        if item.lower().endswith('.gpt'):
            original_path = os.path.join(current_dir, item)
            bak_filename = os.path.splitext(item)[0] + '.GPTBAK'
            backup_path = os.path.join(backup_dir, bak_filename)

            try:
                # Rename the file to .GPTBAK
                os.rename(original_path, os.path.join(current_dir, bak_filename))
                print(f"Renamed '{item}' to '{bak_filename}'.")

                # Move the .GPTBAK file to the backup directory
                shutil.move(os.path.join(current_dir, bak_filename), backup_path)
                print(f"Moved '{bak_filename}' to '{backup_path}'.")
            except Exception as e:
                print(f"Error backing up '{item}': {e}")
                continue

def collect_files(base_dirs, extensions, excluded_filenames, exclude_subdirs_map):
    """
    Collects files from base directories based on extensions and excludes specified filenames.
    Returns a dictionary mapping lowercase filenames to their file paths.
    """
    filename_map = defaultdict(list)

    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            print(f"Warning: The directory '{base_dir}' does not exist and will be skipped.")
            continue

        # Determine which subdirectories to exclude for this base_dir
        exclude_subdirs = exclude_subdirs_map.get(base_dir, [])

        for root, dirs, files in os.walk(base_dir):
            # Exclude specified subdirectories
            dirs[:] = [d for d in dirs if d not in exclude_subdirs and not d.startswith('.')]

            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                # Check if the file should be excluded
                if file.lower() in excluded_filenames:
                    continue
                # Check file extension
                if any(file.lower().endswith(ext.lower()) for ext in extensions):
                    full_path = os.path.join(root, file)
                    filename_map[file.lower()].append(full_path)

    return filename_map

def alert_duplicate_filenames(duplicate_files):
    """
    Alerts the user about duplicate filenames with detailed comparisons.
    """
    print("\n=== Duplicate Filenames Detected ===\n")
    for filename, paths in duplicate_files.items():
        print(f"Duplicate Filename: {filename}")
        print("-----------------------------------")
        for idx, path in enumerate(paths, start=1):
            try:
                size = os.path.getsize(path)
                ctime = datetime.fromtimestamp(os.path.getctime(path)).strftime('%Y-%m-%d %H:%M:%S')
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    num_lines = len(lines)
            except Exception as e:
                print(f"Error retrieving information for '{path}': {e}")
                size = 'N/A'
                ctime = 'N/A'
                mtime = 'N/A'
                num_lines = 'N/A'
            print(f"File {idx}:")
            print(f"  Path           : {path}")
            print(f"  Size           : {size} bytes")
            print(f"  Created        : {ctime}")
            print(f"  Last Modified  : {mtime}")
            print(f"  Lines of Code  : {num_lines}")
            print()
        print("-----------------------------------\n")
    print("Please resolve duplicate filenames to ensure each script is uniquely identified.\n")

def generate_output(collected_files):
    header = "I've listed all the scripts in this project below. Please provide a complete fix for the error shown. If any scripts need modification, provide me with the complete, untruncated, working revision, without any placeholders or missing code or example code or hypothetical code. Everything you provide must be fully working, error-free and production-ready.\n\n==================================\n\n"
    content = header
    for idx, (filename, path) in enumerate(collected_files, start=1):
        # Determine location
        relative_path = os.path.relpath(path, start=current_dir)
        if os.path.commonpath([path, scripts_dir]) == scripts_dir:
            location = "located in the 'scripts' subdirectory"
        else:
            location = "located in the working directory"

        # Read file contents
        file_contents = read_file_contents(path)

        # Append to content
        content += f"{idx}) {os.path.basename(relative_path)} ({location}):\n\n{file_contents}\n\n==================================\n\n"
    return content

def read_file_contents(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return "[Error reading file]"

def write_output_file(output_path, content):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully created '{output_path}'.")
    except Exception as e:
        print(f"Error writing to file '{output_path}': {e}")

if __name__ == "__main__":
    # Get current working directory
    current_dir = get_current_directory()
    work_dir_name = get_directory_name(current_dir)
    scripts_dir = os.path.join(current_dir, "scripts")

    # Backup existing .GPT files before doing anything else
    backup_existing_gpt_files(current_dir, work_dir_name)

    # Parse command-line arguments
    args = parse_arguments()

    # Generate timestamp and output filename
    timestamp = get_timestamp()
    output_filename = f"{work_dir_name}-{timestamp}.GPT"
    output_path = os.path.join(current_dir, output_filename)

    # Get the filename of the running script to exclude it
    script_filename = os.path.basename(__file__).lower()

    # Define a set of filenames to exclude (in lowercase for case-insensitive comparison)
    excluded_filenames = {script_filename}

    # Define default extensions and folders
    extensions = ['.py']
    if args.extensions:
        # Ensure extensions start with a dot and convert to lowercase
        additional_ext = [ext.lower() if ext.startswith('.') else f".{ext.lower()}" for ext in args.extensions]
        extensions.extend(additional_ext)

    # Initialize base_dirs with unique directories
    # Exclude 'scripts' from being traversed when processing current_dir
    base_dirs = [current_dir, scripts_dir]
    # Remove duplicates if any
    base_dirs = list(dict.fromkeys(base_dirs))

    # Handle additional folders
    # Ensure that additional folders are not already included
    if args.folders:
        for folder in args.folders:
            additional_dir = os.path.join(current_dir, folder)
            if additional_dir not in base_dirs:
                base_dirs.append(additional_dir)

    # Define which subdirectories to exclude for each base_dir
    # For current_dir, exclude 'scripts'
    # For other base_dirs, no exclusions
    exclude_subdirs_map = {
        current_dir: ['scripts']
    }

    # Collect files
    filename_map = collect_files(base_dirs, extensions, excluded_filenames, exclude_subdirs_map)

    # Detect duplicates across different directories
    duplicate_filenames = {fname: paths for fname, paths in filename_map.items() if len(paths) > 1}

    if duplicate_filenames:
        alert_duplicate_filenames(duplicate_filenames)
        # Remove duplicates from filename_map
        for fname in duplicate_filenames.keys():
            del filename_map[fname]

    # Prepare list of unique files to include
    unique_files = []
    for fname, paths in filename_map.items():
        # Since no duplicates, paths has only one item
        unique_files.append((fname, paths[0]))

    if not unique_files:
        print("No files found matching the specified criteria or all have duplicates.")
        sys.exit(0)

    # Generate output content
    output_content = generate_output(unique_files)

    # Write to output file
    write_output_file(output_path, output_content)

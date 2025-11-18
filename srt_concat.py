#!/usr/bin/env python3
"""
SRT Concat - Concatenate multiple SRT files

This script concatenates multiple SRT subtitle files, adjusting timestamps
so they follow sequentially. This is useful when combining videos from multiple
drone recordings.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta


def parse_timestamp(timestamp_str):
    """
    Parse SRT timestamp string to timedelta.
    
    Args:
        timestamp_str: String in format HH:MM:SS,mmm
        
    Returns:
        timedelta object
    """
    # Replace comma with period for milliseconds
    timestamp_str = timestamp_str.replace(',', '.')
    
    parts = timestamp_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_parts = parts[2].split('.')
    seconds = int(seconds_parts[0])
    milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
    
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


def format_timestamp(td):
    """
    Format timedelta as SRT timestamp.
    
    Args:
        td: timedelta object
        
    Returns:
        String in format HH:MM:SS,mmm
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = td.microseconds // 1000
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def get_video_duration(video_path):
    """
    Get video duration using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Duration in seconds (float) or None if error
    """
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return None


def parse_srt_block(block):
    """
    Parse a single SRT subtitle block.
    
    Args:
        block: String containing one SRT subtitle entry
        
    Returns:
        Dictionary with frame_num, start_time, end_time, and content
    """
    lines = block.strip().split('\n')
    if len(lines) < 3:
        return None
    
    try:
        frame_num = int(lines[0])
    except ValueError:
        return None
    
    timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', lines[1])
    if not timestamp_match:
        return None
    
    start_time = parse_timestamp(timestamp_match.group(1))
    end_time = parse_timestamp(timestamp_match.group(2))
    content = '\n'.join(lines[2:])
    
    return {
        'frame_num': frame_num,
        'start_time': start_time,
        'end_time': end_time,
        'content': content
    }


def read_srt_file(srt_path):
    """
    Read and parse an SRT file.
    
    Args:
        srt_path: Path to SRT file
        
    Returns:
        List of parsed subtitle blocks
    """
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content.strip())
    parsed_blocks = []
    
    for block in blocks:
        parsed = parse_srt_block(block)
        if parsed:
            parsed_blocks.append(parsed)
    
    return parsed_blocks


def concatenate_srt_files(input_list_path, output_path):
    """
    Concatenate multiple SRT files.
    
    Args:
        input_list_path: Path to text file listing SRT files and their corresponding videos
        output_path: Path for output concatenated SRT file
    """
    # Read input list
    srt_files = []
    video_files = []
    
    with open(input_list_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Support format: file 'path/to/video.MP4'
            # We need to extract both video and corresponding SRT
            if line.startswith('file'):
                # Extract path from quotes
                match = re.search(r"file\s+['\"](.+?)['\"]", line)
                if match:
                    video_path = match.group(1)
                    # Derive SRT path from video path
                    srt_path = os.path.splitext(video_path)[0] + '.SRT'
                    
                    if not os.path.exists(srt_path):
                        # Try lowercase
                        srt_path = os.path.splitext(video_path)[0] + '.srt'
                    
                    if os.path.exists(srt_path):
                        srt_files.append(srt_path)
                        video_files.append(video_path)
                    else:
                        print(f"Warning: SRT file not found for {video_path}")
            else:
                # Assume it's a direct SRT path
                if os.path.exists(line):
                    srt_files.append(line)
                    video_files.append(None)
    
    if not srt_files:
        print(f"Error: No SRT files found in {input_list_path}")
        return False
    
    print(f"Concatenating {len(srt_files)} SRT files...")
    
    # Concatenate SRT files
    all_blocks = []
    time_offset = timedelta(0)
    frame_offset = 0
    
    for idx, srt_file in enumerate(srt_files):
        print(f"Processing {srt_file}...")
        
        blocks = read_srt_file(srt_file)
        if not blocks:
            print(f"Warning: No valid blocks found in {srt_file}")
            continue
        
        # Adjust timestamps and frame numbers
        for block in blocks:
            adjusted_block = {
                'frame_num': block['frame_num'] + frame_offset,
                'start_time': block['start_time'] + time_offset,
                'end_time': block['end_time'] + time_offset,
                'content': block['content']
            }
            all_blocks.append(adjusted_block)
        
        # Update offsets for next file
        if blocks:
            last_block = blocks[-1]
            frame_offset += len(blocks)
            
            # Try to get accurate video duration
            if video_files[idx] and os.path.exists(video_files[idx]):
                duration = get_video_duration(video_files[idx])
                if duration:
                    time_offset += timedelta(seconds=duration)
                else:
                    # Fallback to last timestamp
                    time_offset += last_block['end_time']
            else:
                # Fallback to last timestamp
                time_offset += last_block['end_time']
    
    # Write concatenated SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, block in enumerate(all_blocks, 1):
            # Renumber sequentially
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(block['start_time'])} --> {format_timestamp(block['end_time'])}\n")
            f.write(f"{block['content']}\n")
            f.write("\n")
    
    print(f"Successfully created concatenated SRT file: {output_path}")
    print(f"Total frames: {len(all_blocks)}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Concatenate multiple SRT subtitle files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python srt_concat.py -i concat_files.txt -o output.srt

Input file format (concat_files.txt):
  file '/path/to/video1.MP4'
  file '/path/to/video2.MP4'
  
Or simply list SRT files directly:
  /path/to/video1.SRT
  /path/to/video2.SRT
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                        help='Path to input list file')
    parser.add_argument('-o', '--output', required=True,
                        help='Path to output concatenated SRT file')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Concatenate files
    success = concatenate_srt_files(args.input, args.output)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

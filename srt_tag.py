#!/usr/bin/env python3
"""
SRT Tag - Geotag video frames using SRT subtitle files

This script reads GPS data from DJI drone SRT files and applies geolocation
metadata to extracted video frames using ExifTool.
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta


def parse_srt_file(srt_path):
    """
    Parse SRT file and extract GPS and telemetry data.
    
    Args:
        srt_path: Path to the SRT file
        
    Returns:
        List of dictionaries containing frame data
    """
    frames = []
    
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to separate subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # Parse frame number
        try:
            frame_num = int(lines[0])
        except ValueError:
            continue
        
        # Parse timestamp
        timestamp_line = lines[1]
        timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', timestamp_line)
        if not timestamp_match:
            continue
        
        start_time = timestamp_match.group(1).replace(',', '.')
        
        # Parse telemetry data
        telemetry = {}
        for line in lines[2:]:
            # Look for GPS coordinates
            lat_match = re.search(r'latitude\s*:\s*([-+]?\d+\.?\d*)', line, re.IGNORECASE)
            lon_match = re.search(r'longitude\s*:\s*([-+]?\d+\.?\d*)', line, re.IGNORECASE)
            alt_match = re.search(r'altitude\s*:\s*([-+]?\d+\.?\d*)', line, re.IGNORECASE)
            
            # Alternative format: [latitude: XX.XXXX] [longitude: YY.YYYY]
            if not lat_match:
                lat_match = re.search(r'\[latitude:\s*([-+]?\d+\.?\d*)\]', line, re.IGNORECASE)
            if not lon_match:
                lon_match = re.search(r'\[longitude:\s*([-+]?\d+\.?\d*)\]', line, re.IGNORECASE)
            if not alt_match:
                alt_match = re.search(r'\[altitude:\s*([-+]?\d+\.?\d*)\]', line, re.IGNORECASE)
            
            if lat_match:
                telemetry['latitude'] = float(lat_match.group(1))
            if lon_match:
                telemetry['longitude'] = float(lon_match.group(1))
            if alt_match:
                telemetry['altitude'] = float(alt_match.group(1))
        
        if 'latitude' in telemetry and 'longitude' in telemetry:
            frames.append({
                'frame_num': frame_num,
                'timestamp': start_time,
                'latitude': telemetry['latitude'],
                'longitude': telemetry['longitude'],
                'altitude': telemetry.get('altitude', 0)
            })
    
    return frames


def tag_images(srt_path, images_dir, fps_original, extension, fps_extracted):
    """
    Tag images with GPS data from SRT file.
    
    Args:
        srt_path: Path to SRT file
        images_dir: Directory containing extracted frames
        fps_original: Original video frame rate
        extension: Image file extension (jpg, png, etc.)
        fps_extracted: Frame rate used for extraction (frames per second)
    """
    print(f"Parsing SRT file: {srt_path}")
    frames_data = parse_srt_file(srt_path)
    
    if not frames_data:
        print("Error: No GPS data found in SRT file")
        return False
    
    print(f"Found {len(frames_data)} frames with GPS data in SRT file")
    
    # Check for exiftool
    try:
        subprocess.run(['exiftool', '-ver'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: exiftool not found. Please install it from https://exiftool.org/")
        return False
    
    # Get list of image files
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(f'.{extension}')])
    
    if not image_files:
        print(f"Error: No .{extension} files found in {images_dir}")
        return False
    
    print(f"Found {len(image_files)} image files to tag")
    
    # Calculate frame mapping
    # fps_extracted is frames per second, so interval between frames
    frame_interval = fps_original / fps_extracted
    
    tagged_count = 0
    for idx, image_file in enumerate(image_files):
        # Calculate which SRT frame this image corresponds to
        # Image index 0 -> SRT frame 1 (first frame)
        # With fps_extracted=1 and fps_original=30, each image is 30 frames apart
        srt_frame_num = int(idx * frame_interval) + 1
        
        # Find the closest frame data
        closest_frame = None
        min_diff = float('inf')
        
        for frame in frames_data:
            diff = abs(frame['frame_num'] - srt_frame_num)
            if diff < min_diff:
                min_diff = diff
                closest_frame = frame
        
        if closest_frame is None:
            print(f"Warning: No GPS data found for {image_file}")
            continue
        
        # Tag the image with GPS data
        image_path = os.path.join(images_dir, image_file)
        
        try:
            # Set GPS coordinates
            cmd = [
                'exiftool',
                '-overwrite_original',
                f'-GPSLatitude={closest_frame["latitude"]}',
                f'-GPSLongitude={closest_frame["longitude"]}',
                f'-GPSAltitude={closest_frame["altitude"]}',
                '-GPSLatitudeRef=' + ('N' if closest_frame["latitude"] >= 0 else 'S'),
                '-GPSLongitudeRef=' + ('E' if closest_frame["longitude"] >= 0 else 'W'),
                '-GPSAltitudeRef=0',
                image_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                tagged_count += 1
                if tagged_count % 10 == 0:
                    print(f"Tagged {tagged_count}/{len(image_files)} images...")
            else:
                print(f"Warning: Failed to tag {image_file}: {result.stderr}")
                
        except Exception as e:
            print(f"Error tagging {image_file}: {e}")
    
    print(f"\nSuccessfully tagged {tagged_count} out of {len(image_files)} images")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Geotag video frames using SRT subtitle files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python srt_tag.py -s video.SRT -d frames/ -p 30 -x jpg -f 1
  python srt_tag.py -s DJI_0123.SRT -d output_frames/ -p 30 -x png -f 0.5
        """
    )
    
    parser.add_argument('-s', '--srt', required=True,
                        help='Path to SRT subtitle file')
    parser.add_argument('-d', '--directory', required=True,
                        help='Directory containing extracted frames')
    parser.add_argument('-p', '--fps-original', type=float, required=True,
                        help='Original video frame rate (e.g., 30 for 30fps)')
    parser.add_argument('-x', '--extension', required=True,
                        help='Image file extension (jpg, png, etc.)')
    parser.add_argument('-f', '--fps-extracted', type=float, required=True,
                        help='Frame extraction rate (e.g., 1 for 1 frame per second, 0.5 for 1 frame every 2 seconds)')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.srt):
        print(f"Error: SRT file not found: {args.srt}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        sys.exit(1)
    
    if args.fps_original <= 0:
        print(f"Error: Original FPS must be greater than 0, got {args.fps_original}")
        sys.exit(1)
    
    if args.fps_extracted <= 0:
        print(f"Error: Extracted FPS must be greater than 0, got {args.fps_extracted}")
        sys.exit(1)
    
    # Tag images
    success = tag_images(
        args.srt,
        args.directory,
        args.fps_original,
        args.extension,
        args.fps_extracted
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

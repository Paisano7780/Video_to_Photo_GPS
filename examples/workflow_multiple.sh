# Workflow Example - Multiple Videos (Concatenation)
# This shows the complete workflow for processing multiple drone videos

echo "=== Video to Photo GPS - Multiple Videos Workflow ==="
echo ""
echo "Prerequisites:"
echo "- FFmpeg installed"
echo "- Python 3 installed"
echo "- ExifTool installed"
echo ""

# Variables (EDIT THESE)
FILES_LIST="files.txt"       # List of videos to concatenate
OUTPUT_VIDEO="output.mp4"    # Concatenated video output
OUTPUT_SRT="output.srt"      # Concatenated SRT output
FRAMES_DIR="frames"          # Output directory for frames
FPS_ORIGINAL=30              # Original video frame rate
FPS_EXTRACT=1                # Extract 1 frame per second
IMAGE_EXT="jpg"              # jpg or png

echo "Configuration:"
echo "  Input list: $FILES_LIST"
echo "  Output video: $OUTPUT_VIDEO"
echo "  Output SRT: $OUTPUT_SRT"
echo "  Frames dir: $FRAMES_DIR"
echo "  Original FPS: $FPS_ORIGINAL"
echo "  Extract FPS: $FPS_EXTRACT"
echo "  Format: $IMAGE_EXT"
echo ""

# Step 1: Create files list
echo "Step 1: Create files list (if not exists)..."
if [ ! -f "$FILES_LIST" ]; then
    echo "Creating example $FILES_LIST..."
    cat > "$FILES_LIST" << 'EOF'
file '/path/to/DJI_0251.MP4'
file '/path/to/DJI_0252.MP4'
file '/path/to/DJI_0253.MP4'
EOF
    echo "Please edit $FILES_LIST with your video paths!"
else
    echo "Using existing $FILES_LIST"
fi

# Step 2: Concatenate videos
echo "Step 2: Concatenating videos..."
echo "Command: ffmpeg -f concat -safe 0 -i $FILES_LIST -c copy $OUTPUT_VIDEO"
# Uncomment to run:
# ffmpeg -f concat -safe 0 -i "$FILES_LIST" -c copy "$OUTPUT_VIDEO"

# Step 3: Concatenate SRT files
echo "Step 3: Concatenating SRT files..."
echo "Command: python srt_concat.py -i $FILES_LIST -o $OUTPUT_SRT"
# Uncomment to run:
# python srt_concat.py -i "$FILES_LIST" -o "$OUTPUT_SRT"

# Step 4: Extract frames
echo "Step 4: Extracting frames from concatenated video..."
mkdir -p "$FRAMES_DIR"
echo "Command: ffmpeg -i $OUTPUT_VIDEO -vf fps=$FPS_EXTRACT $FRAMES_DIR/%04d.$IMAGE_EXT"
# Uncomment to run:
# ffmpeg -i "$OUTPUT_VIDEO" -vf fps=$FPS_EXTRACT "$FRAMES_DIR/%04d.$IMAGE_EXT"

# Step 5: Geotag frames
echo "Step 5: Geotagging frames with GPS data..."
echo "Command: python srt_tag.py -s $OUTPUT_SRT -d $FRAMES_DIR/ -p $FPS_ORIGINAL -x $IMAGE_EXT -f $FPS_EXTRACT"
# Uncomment to run:
# python srt_tag.py -s "$OUTPUT_SRT" -d "$FRAMES_DIR/" -p $FPS_ORIGINAL -x $IMAGE_EXT -f $FPS_EXTRACT

echo ""
echo "=== Workflow Complete ==="
echo "Your geotagged frames are in: $FRAMES_DIR/"
echo "Upload them to WebODM to create orthophotos and 3D models!"

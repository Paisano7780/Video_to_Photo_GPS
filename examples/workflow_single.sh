# Workflow Example - Single Video
# This shows the complete workflow for processing a single drone video

echo "=== Video to Photo GPS - Single Video Workflow ==="
echo ""
echo "Prerequisites:"
echo "- FFmpeg installed"
echo "- Python 3 installed"
echo "- ExifTool installed"
echo ""

# Variables (EDIT THESE)
VIDEO_FILE="DJI_0123.MP4"
SRT_FILE="DJI_0123.SRT"
OUTPUT_DIR="frames"
FPS_ORIGINAL=30    # Original video frame rate
FPS_EXTRACT=1      # Extract 1 frame per second
IMAGE_EXT="jpg"    # jpg or png

echo "Configuration:"
echo "  Video: $VIDEO_FILE"
echo "  SRT: $SRT_FILE"
echo "  Output: $OUTPUT_DIR"
echo "  Original FPS: $FPS_ORIGINAL"
echo "  Extract FPS: $FPS_EXTRACT"
echo "  Format: $IMAGE_EXT"
echo ""

# Step 1: Create output directory
echo "Step 1: Creating output directory..."
mkdir -p "$OUTPUT_DIR"

# Step 2: Extract frames
echo "Step 2: Extracting frames from video..."
echo "Command: ffmpeg -i $VIDEO_FILE -vf fps=$FPS_EXTRACT $OUTPUT_DIR/%04d.$IMAGE_EXT"
# Uncomment to run:
# ffmpeg -i "$VIDEO_FILE" -vf fps=$FPS_EXTRACT "$OUTPUT_DIR/%04d.$IMAGE_EXT"

# Step 3: Geotag frames
echo "Step 3: Geotagging frames with GPS data..."
echo "Command: python srt_tag.py -s $SRT_FILE -d $OUTPUT_DIR/ -p $FPS_ORIGINAL -x $IMAGE_EXT -f $FPS_EXTRACT"
# Uncomment to run:
# python srt_tag.py -s "$SRT_FILE" -d "$OUTPUT_DIR/" -p $FPS_ORIGINAL -x $IMAGE_EXT -f $FPS_EXTRACT

echo ""
echo "=== Workflow Complete ==="
echo "Your geotagged frames are in: $OUTPUT_DIR/"
echo "Upload them to WebODM to create orthophotos and 3D models!"

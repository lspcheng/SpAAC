#!/bin/sh

# To run (macOS): sh mk_spkr_dir.sh speaker

# hard path
path="../02-stimuli/P0-norming/n2/03-recordings"

# input speaker code
speaker=$1 # e.g., S07

# make audio dirs
mkdir -p "$path/$speaker/1_audio/1_original" "$path/$speaker/1_audio/2_processed" && cat <<EOF > "$path/$speaker/1_audio/2_processed/records.txt"
# Audacity settings

noise reduction =
sensitivity =
frequency smoothing =
EOF

# make textgird dirs
mkdir -p "$path/$speaker/2_textgrid/1_original" "$path/$speaker/2_textgrid/2_manual/temp" && cat <<EOF > "$path/$speaker/2_textgrid/1_original/records.txt"
# Praat settings

silence threshold =
silence duration (min) =
sounding duration (min) =
EOF

#!/bin/bash

INPUT_FILE="file_urls.txt"
TARGET_DIR="../../examplary_data"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: $INPUT_FILE not found!"
    exit 1
fi

mkdir -p "$TARGET_DIR"

while IFS= read -r url; do
    echo "Downloading $url..."
    curl -o "$TARGET_DIR/$(basename "$url")" "$url"
done < "$INPUT_FILE"

echo "All files downloaded to $TARGET_DIR."


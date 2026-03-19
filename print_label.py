#!/usr/bin/env python3
"""
Brother QL-800 label printer script for 62x29mm labels.

Usage:
    python3 print_label.py "Your text"
    python3 print_label.py "Line one\\nLine two"
    python3 print_label.py "Your text" --size 40
    python3 print_label.py "Your text" --bold
    python3 print_label.py "Your text" --italic
    python3 print_label.py "Your text" --bold --italic
    python3 print_label.py "Your text" --preview
    python3 print_label.py "Your text" --preview --print
"""

import argparse
import subprocess
from PIL import Image, ImageDraw, ImageFont

# --- Settings ---
LABEL_WIDTH = 696
LABEL_HEIGHT = 271
MARGIN = 20  # pixels padding from edges

FONT_REGULAR     = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD        = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_ITALIC      = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
FONT_BOLD_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"

MAX_FONT_SIZE = 180
MIN_FONT_SIZE = 10

OUTPUT_FILE = "label.png"

PRINTER_BACKEND = "pyusb"
PRINTER_MODEL   = "QL-800"
PRINTER_USB     = "usb://0x04f9:0x209b"
PRINTER_LABEL   = "62x29"


def pick_font_path(bold, italic):
    if bold and italic:
        return FONT_BOLD_ITALIC
    if bold:
        return FONT_BOLD
    if italic:
        return FONT_ITALIC
    return FONT_REGULAR


def fit_font_size(draw, text, font_path, max_width, max_height, start_size):
    """Find the largest font size where text fits within max_width x max_height."""
    size = start_size
    while size >= MIN_FONT_SIZE:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= max_width and h <= max_height:
            return size, font
        size -= 1
    font = ImageFont.truetype(font_path, MIN_FONT_SIZE)
    return MIN_FONT_SIZE, font


def make_label(text, font_size, bold, italic, auto_size):
    font_path = pick_font_path(bold, italic)

    image = Image.new("RGB", (LABEL_WIDTH, LABEL_HEIGHT), color="white")
    draw = ImageDraw.Draw(image)

    max_w = LABEL_WIDTH  - 2 * MARGIN
    max_h = LABEL_HEIGHT - 2 * MARGIN

    if auto_size:
        font_size, font = fit_font_size(draw, text, font_path, max_w, max_h, MAX_FONT_SIZE)
        print(f"Auto font size: {font_size}")
    else:
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.multiline_textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) > max_w or (bbox[3] - bbox[1]) > max_h:
            print(f"Warning: text may overflow at size {font_size}. Try omitting --size to auto-fit.")

    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    text_width  = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (LABEL_WIDTH  - text_width)  // 2
    y = (LABEL_HEIGHT - text_height) // 2

    draw.multiline_text((x, y), text, fill="black", font=font, align="center")

    bw = image.convert("1")
    bw.save(OUTPUT_FILE)
    print(f"Label saved to {OUTPUT_FILE} (size {font_size})")


def preview_label():
    subprocess.Popen(["xdg-open", OUTPUT_FILE])


def print_label():
    cmd = [
        "brother_ql",
        "--backend", PRINTER_BACKEND,
        "--model",   PRINTER_MODEL,
        "--printer", PRINTER_USB,
        "print",
        "-l", PRINTER_LABEL,
        OUTPUT_FILE,
    ]
    print("Sending to printer...")
    subprocess.run(cmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print a text label on Brother QL-800")
    parser.add_argument("text",
        help='Text to print. Use \\n for multiple lines, e.g. "Line 1\\nLine 2"')
    parser.add_argument("--size", type=int, default=None,
        help="Font size. Omit to auto-fit text to label.")
    parser.add_argument("--bold",    action="store_true", help="Bold text")
    parser.add_argument("--italic",  action="store_true", help="Italic text")
    parser.add_argument("--preview", action="store_true", help="Open label preview before printing")
    parser.add_argument("--print",   dest="do_print", action="store_true", help="Send to printer")

    args = parser.parse_args()

    text = args.text.replace("\\n", "\n")
    auto_size = args.size is None
    font_size  = args.size if args.size else MAX_FONT_SIZE

    make_label(text, font_size, args.bold, args.italic, auto_size)

    if args.preview:
        preview_label()

    if args.do_print:
        print_label()
    elif not args.preview:
        print("Tip: use --preview to check the label, --print to send to printer.")

# ql-800_label_print
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

This script requires installation and configuration of the label printer before it will work. For installation of Brother ql-800 on your Gnu/Linux system, use this guide https://github.com/ICTools/ql-800-ubuntu

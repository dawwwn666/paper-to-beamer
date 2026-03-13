#!/usr/bin/env python3
import sys
from pdf2image import convert_from_path

def extract_pages(pdf_path, pages, output_prefix):
    images = convert_from_path(pdf_path, dpi=150, first_page=pages[0], last_page=pages[-1])
    for i, page_num in enumerate(pages):
        if i < len(images):
            images[i].save(f"{output_prefix}_page{page_num}.png", "PNG")
            print(f"Saved: {output_prefix}_page{page_num}.png")

if __name__ == "__main__":
    # Chinese version - OperatingLease
    print("Extracting Chinese version...")
    extract_pages("demo/OperatingLease_CEA_LiGang.pdf", [1, 2, 3, 10, 15], "demo/screenshots/cn")

    # English version - CAPM
    print("Extracting English version...")
    extract_pages("demo/CAPM_Size_Factor.pdf", [1, 2, 3, 18, 20], "demo/screenshots/en")

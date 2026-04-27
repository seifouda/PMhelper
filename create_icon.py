"""
PMhelper Edu — Icon Generator
Creates a multi-resolution .ico file for embedding in the executable.
Uses only the Python standard library + Pillow (pip install Pillow).

Usage:
    python create_icon.py

Output:
    assets/pmhelper_edu.ico (256x256, 128x128, 64x64, 48x48, 32x32, 16x16)
"""

import os
import struct
import sys
import math


def create_pmhelper_icon_raw():
    """
    Generate a professional PMhelper icon as raw RGBA pixel data.
    Creates a blue gradient background with white "PM" text.
    No external dependencies required.
    """
    sizes = [256, 128, 64, 48, 32, 16]
    images = {}

    for size in sizes:
        pixels = bytearray(size * size * 4)  # RGBA

        for y in range(size):
            for x in range(size):
                idx = (y * size + x) * 4

                # Rounded rectangle background
                margin = max(1, size // 16)
                corner_r = max(2, size // 8)

                # Check if inside rounded rect
                in_rect = True
                if x < margin or x >= size - margin or y < margin or y >= size - margin:
                    in_rect = False
                elif x < margin + corner_r and y < margin + corner_r:
                    if (x - margin - corner_r) ** 2 + (y - margin - corner_r) ** 2 > corner_r ** 2:
                        in_rect = False
                elif x >= size - margin - corner_r and y < margin + corner_r:
                    if (x - (size - margin - corner_r - 1)) ** 2 + (y - margin - corner_r) ** 2 > corner_r ** 2:
                        in_rect = False
                elif x < margin + corner_r and y >= size - margin - corner_r:
                    if (x - margin - corner_r) ** 2 + (y - (size - margin - corner_r - 1)) ** 2 > corner_r ** 2:
                        in_rect = False
                elif x >= size - margin - corner_r and y >= size - margin - corner_r:
                    if (x - (size - margin - corner_r - 1)) ** 2 + (y - (size - margin - corner_r - 1)) ** 2 > corner_r ** 2:
                        in_rect = False

                if in_rect:
                    # Blue gradient: top=#2563EB → bottom=#1E40AF
                    t = y / max(1, size - 1)
                    r = int(37 * (1 - t) + 30 * t)
                    g = int(99 * (1 - t) + 64 * t)
                    b = int(235 * (1 - t) + 175 * t)
                    a = 255

                    # Draw "PM" letters for sizes >= 32
                    if size >= 32:
                        # Normalized coordinates (0-1)
                        nx = x / size
                        ny = y / size

                        in_letter = False
                        lw = 0.06  # line width

                        # Letter P (left side: x=0.15-0.48, y=0.25-0.75)
                        # Vertical stroke
                        if 0.15 <= nx <= 0.15 + lw and 0.25 <= ny <= 0.75:
                            in_letter = True
                        # Top horizontal
                        if 0.15 <= nx <= 0.40 and 0.25 <= ny <= 0.25 + lw:
                            in_letter = True
                        # Middle horizontal
                        if 0.15 <= nx <= 0.40 and 0.47 <= ny <= 0.47 + lw:
                            in_letter = True
                        # Right curve of P (simplified as vertical)
                        if 0.40 - lw <= nx <= 0.40 and 0.25 <= ny <= 0.47 + lw:
                            in_letter = True

                        # Letter M (right side: x=0.50-0.85, y=0.25-0.75)
                        # Left vertical
                        if 0.50 <= nx <= 0.50 + lw and 0.25 <= ny <= 0.75:
                            in_letter = True
                        # Right vertical
                        if 0.82 - lw <= nx <= 0.82 and 0.25 <= ny <= 0.75:
                            in_letter = True
                        # Left diagonal (down-right from top-left)
                        cx_diag = 0.50 + lw / 2 + (nx - 0.50) * 1.0
                        mid_x = 0.66
                        if 0.50 <= nx <= mid_x and 0.25 <= ny <= 0.55:
                            expected_y = 0.25 + (nx - 0.50) / (mid_x - 0.50) * 0.30
                            if abs(ny - expected_y) < lw * 1.2:
                                in_letter = True
                        # Right diagonal (down-left from top-right)
                        if mid_x <= nx <= 0.82 and 0.25 <= ny <= 0.55:
                            expected_y = 0.55 - (nx - mid_x) / (0.82 - mid_x) * 0.30
                            if abs(ny - expected_y) < lw * 1.2:
                                in_letter = True

                        if in_letter:
                            r, g, b = 255, 255, 255  # White text
                else:
                    r, g, b, a = 0, 0, 0, 0  # Transparent

                pixels[idx] = r
                pixels[idx + 1] = g
                pixels[idx + 2] = b
                pixels[idx + 3] = a

        images[size] = bytes(pixels)

    return images


def create_ico_file(images, output_path):
    """
    Write a .ico file from raw RGBA image data.
    ICO format: header + directory entries + BMP image data for each size.
    """
    num_images = len(images)

    # ICO header: reserved(2) + type(2) + count(2)
    header = struct.pack('<HHH', 0, 1, num_images)

    # Calculate offsets
    dir_entry_size = 16
    data_offset = 6 + num_images * dir_entry_size

    directory = b''
    image_data = b''

    for size in sorted(images.keys(), reverse=True):
        rgba = images[size]
        w = size
        h = size

        # BMP info header (BITMAPINFOHEADER) — height is doubled for ICO (image + mask)
        bmp_header = struct.pack(
            '<IiiHHIIiiII',
            40,        # biSize
            w,         # biWidth
            h * 2,     # biHeight (doubled: image + AND mask)
            1,         # biPlanes
            32,        # biBitCount (RGBA)
            0,         # biCompression (BI_RGB)
            0,         # biSizeImage (can be 0 for BI_RGB)
            0,         # biXPelsPerMeter
            0,         # biYPelsPerMeter
            0,         # biClrUsed
            0,         # biClrImportant
        )

        # Convert RGBA top-down to BGRA bottom-up (BMP is bottom-up)
        pixel_data = bytearray()
        for y in range(h - 1, -1, -1):
            for x in range(w):
                idx = (y * w + x) * 4
                r = rgba[idx]
                g = rgba[idx + 1]
                b = rgba[idx + 2]
                a = rgba[idx + 3]
                pixel_data.extend([b, g, r, a])  # BGRA

        # AND mask (1-bit, all zeros = fully opaque where alpha says so)
        # Each row is padded to 4-byte boundary
        mask_row_bytes = ((w + 31) // 32) * 4
        and_mask = b'\x00' * (mask_row_bytes * h)

        bmp_data = bmp_header + bytes(pixel_data) + and_mask
        bmp_size = len(bmp_data)

        # ICO directory entry
        icon_w = 0 if w == 256 else w  # 0 means 256
        icon_h = 0 if h == 256 else h
        entry = struct.pack(
            '<BBBBHHII',
            icon_w,      # width (0=256)
            icon_h,      # height (0=256)
            0,           # color palette
            0,           # reserved
            1,           # color planes
            32,          # bits per pixel
            bmp_size,    # size of image data
            data_offset + len(image_data),  # offset
        )

        directory += entry
        image_data += bmp_data

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(header + directory + image_data)


def main():
    output_path = os.path.join('assets', 'pmhelper_edu.ico')

    # Try Pillow first (better quality if available)
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("Using Pillow for high-quality icon generation...")
        create_with_pillow(output_path)
    except ImportError:
        print("Pillow not found — generating icon with built-in renderer...")
        images = create_pmhelper_icon_raw()
        create_ico_file(images, output_path)

    if os.path.isfile(output_path):
        size = os.path.getsize(output_path)
        print(f"Icon created: {output_path} ({size:,} bytes)")
    else:
        print("ERROR: Icon file was not created!", file=sys.stderr)
        sys.exit(1)


def create_with_pillow(output_path):
    """Generate a professional icon using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    sizes = [256, 128, 64, 48, 32, 16]
    icon_images = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        margin = max(1, size // 16)
        r = max(2, size // 8)

        # Draw rounded rectangle background with gradient
        for y in range(size):
            t = y / max(1, size - 1)
            color_r = int(37 * (1 - t) + 30 * t)
            color_g = int(99 * (1 - t) + 64 * t)
            color_b = int(235 * (1 - t) + 175 * t)
            draw.line(
                [(margin, y), (size - margin - 1, y)],
                fill=(color_r, color_g, color_b, 255),
            )

        # Mask to rounded rectangle
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle(
            [margin, margin, size - margin - 1, size - margin - 1],
            radius=r,
            fill=255,
        )
        img.putalpha(mask)

        # Re-draw gradient inside mask
        img2 = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw2 = ImageDraw.Draw(img2)
        for y in range(margin, size - margin):
            t = y / max(1, size - 1)
            cr = int(37 * (1 - t) + 30 * t)
            cg = int(99 * (1 - t) + 64 * t)
            cb = int(235 * (1 - t) + 175 * t)
            draw2.line([(margin, y), (size - margin - 1, y)], fill=(cr, cg, cb, 255))
        img2.putalpha(mask)

        # Draw "PM" text
        if size >= 32:
            font_size = int(size * 0.45)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except (OSError, IOError):
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                except (OSError, IOError):
                    font = ImageFont.load_default()

            text = "PM"
            bbox = draw2.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = (size - tw) // 2
            ty = (size - th) // 2 - bbox[1]
            draw2.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

        icon_images.append(img2)

    # Save as multi-resolution .ico
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    icon_images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=icon_images[1:],
    )


if __name__ == '__main__':
    main()

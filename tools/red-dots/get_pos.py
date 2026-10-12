"""Convert red document markers into LODOP coordinates or JSON."""

import argparse
import json
from pathlib import Path
import sys

import cv2
import numpy as np

SUPPORTED_IMAGES = {'.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp'}


def find_dots(image, width=794, height=1123, min_area=3):
    """Return (top, left) centroids in page units, sorted in reading order."""
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise ValueError('Expected a readable three-channel image')
    if width <= 0 or height <= 0 or min_area < 1:
        raise ValueError('Page dimensions and minimum marker area must be positive')
    # OpenCV uses BGR. Retain the original red threshold, but group whole
    # connected markers instead of guessing duplicates from individual pixels.
    mask = cv2.inRange(image, np.array([0, 0, 200], dtype=np.uint8),
                      np.array([20, 20, 255], dtype=np.uint8))
    count, _, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    image_height, image_width = image.shape[:2]
    dots = []
    for index in range(1, count):
        if stats[index, cv2.CC_STAT_AREA] < min_area:
            continue
        x, y = centroids[index]
        dots.append((round(float(y) * height / image_height),
                     round(float(x) * width / image_width)))
    return sorted(dots)


def collect_images(inputs):
    """Preserve explicit input order; sort images within each directory."""
    images = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            found = sorted(p for p in path.iterdir()
                           if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGES)
            if not found:
                raise ValueError(f'No supported images in {path}')
            images.extend(found)
        elif path.is_file():
            images.append(path)
        else:
            raise ValueError(f'Input does not exist: {path}')
    return images


def render_js(pages):
    lines = []
    for index, page in enumerate(pages):
        if index:
            lines.append('LODOP.NEWPAGE();')
        lines.append(f'// Page: {index + 1}')
        for number, (top, left) in enumerate(page['dots'], start=1):
            lines.append(f'LODOP.ADD_PRINT_TEXT({top}, {left}, 100, 20, "{number}");')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('images', nargs='+', help='Image files or directories of page images')
    parser.add_argument('--width', type=int, default=794, help='Page width in LODOP units (default: 794)')
    parser.add_argument('--height', type=int, default=1123, help='Page height in LODOP units (default: 1123)')
    parser.add_argument('--offset-y', type=int, default=-7, help='Vertical calibration offset (default: -7)')
    parser.add_argument('--offset-x', type=int, default=0, help='Horizontal calibration offset (default: 0)')
    parser.add_argument('--min-area', type=int, default=3, help='Minimum red marker area in source pixels')
    parser.add_argument('--format', choices=['js', 'json'], default='js')
    parser.add_argument('--output', type=Path, help='Write to a file instead of standard output')
    args = parser.parse_args(argv)
    try:
        if args.width <= 0 or args.height <= 0 or args.min_area < 1:
            raise ValueError('Page dimensions and minimum marker area must be positive')
        pages = []
        for path in collect_images(args.images):
            image = cv2.imread(str(path))
            if image is None:
                raise ValueError(f'Unable to read image: {path}')
            dots = find_dots(image, args.width, args.height, args.min_area)
            if not dots:
                raise ValueError(f'No red markers detected in {path}; use solid RGB(255, 0, 0) dots')
            pages.append({
                'image': str(path), 'width': args.width, 'height': args.height,
                'dots': [[top + args.offset_y, left + args.offset_x] for top, left in dots],
            })
        output = json.dumps(pages, indent=2, ensure_ascii=False) + '\n' if args.format == 'json' else render_js(pages)
        if args.output:
            args.output.write_text(output, encoding='utf-8')
        else:
            sys.stdout.write(output)
    except (ValueError, OSError, cv2.error) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

# Red dot coordinate finder

Imported from [Herts/RedDotsFinder](https://github.com/Herts/RedDotsFinder), commit
`61c8fe6f5b9e0572226bc0bb713c4270431da4b2` (also recorded in the subtree commit).
The original contract fixtures are preserved under `resource/`.

This CLI groups connected red markers, calculates their centroids, and scales
them using each image's actual dimensions. It produces numbered LODOP calls or
JSON coordinates. It does not inspect PDF or DOCX files directly: render each
page to an image first.

## Run from the repository root

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/red-dots/requirements.txt
.venv/bin/python tools/red-dots/get_pos.py tools/red-dots/resource/pics
```

Windows: use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

```sh
# JSON for downstream tools; different paper dimensions and calibration
.venv/bin/python tools/red-dots/get_pos.py page.png \
  --format json --width 794 --height 1123 --offset-y -7 --offset-x 0 \
  --output coordinates.json

# Explicit page order
.venv/bin/python tools/red-dots/get_pos.py page1.png page2.png
```

Use solid RGB(255, 0, 0) markers with at least three red pixels. PNG avoids JPEG
artifacts. The detector accepts red pixels with red >= 200 and green/blue <= 20.
`--min-area` filters small components in source pixels. Each distinct marker
should be a connected shape; overlapping markers are detected as one.

Defaults match the original A4 demo: width 794, height 1123, vertical offset -7.
Positions are `(top, left)` in LODOP units. Adjust offsets using a physical test
print. Directory inputs are sorted by filename; use zero-padded page numbers or
explicit file arguments. Labels restart on each page, with `LODOP.NEWPAGE()`
between pages. Invalid or markerless inputs fail with a readable error.

The JavaScript output provides numbered calibration placeholders. Replace them
with your data fields when adding the coordinates to `static/js/demo.js`; verify
the field-to-position mapping against your form.

## Test

```sh
.venv/bin/python -m unittest discover -s tools/red-dots -p 'test_*.py'
```

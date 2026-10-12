# Contract printing with Go and LODOP

A small Go web demo for placing contract data at calibrated positions on
preprinted paper. The integrated [red dot coordinate finder](tools/red-dots/README.md)
turns marked page images into LODOP coordinates.

## Start the demo

Requires Go 1.26 or later. The Go server has no third-party dependencies.

```sh
git clone https://github.com/Herts/LodopWithGolang-Demo.git
cd LodopWithGolang-Demo
go run .
```

Open **http://127.0.0.1:1084/print/**, enter any contract number, and choose
**Design** or **Preview**. The number selects a demo page; all printed content
comes from `static/json/demo.json`, not a database. The example field mapping in
`static/js/demo.js` is illustrative and should be adapted to your actual form.

The server listens on localhost by default. To change the address:

```sh
go run . -addr 127.0.0.1:8080
```

Static assets and templates are embedded, so a compiled executable can run from
any directory. After editing them, rebuild or restart `go run .`.

### LODOP setup

The web page loads without the printing plugin; Design and Preview require a
local LODOP/C-Lodop installation and access to a printer for physical output.
Download the installer and check browser/OS compatibility at the
[official download page](https://www.lodop.net/download.html). Install on the
computer running the browser. This repository does not distribute installers.

The original template targets A4 paper. Browser rendering and server tests do
not establish printing accuracy; paper size, printer margins, driver scaling,
and calibration offsets affect physical placement. Verify with a test sheet.
The Go server and coordinate generator can run independently of the plugin.

## From a marked document to a print template

1. Put solid red markers where the field baselines should be in your source form.
2. Render each page to a PNG, retaining its full page bounds.
3. Install the coordinate tool and run the included sample:

   ```sh
   python3 -m venv .venv
   .venv/bin/python -m pip install -r tools/red-dots/requirements.txt
   .venv/bin/python tools/red-dots/get_pos.py tools/red-dots/resource/pics
   ```

4. Use the generated positions in `static/js/demo.js`, replacing numbered
   placeholders with fields from your JSON data. See the
   [coordinate tool documentation](tools/red-dots/README.md) for JSON output,
   multiple pages, paper dimensions, offsets, and Windows commands.
5. Open Design/Preview and calibrate against a physical test print.

## Repository layout

| Path | Purpose |
| --- | --- |
| `server.go` | Go server and embedded assets. |
| `static/html_templates/` | Contract selection and preview/design pages. |
| `static/js/demo.js` | Field bindings and print coordinates. |
| `static/js/LodopFuncs.js` | Existing LODOP integration helper. |
| `static/json/demo.json` | Sample contract data. |
| `tools/red-dots/` | Coordinate CLI, original fixtures, and Python tests. |
| `tests/printing.test.cjs` | Printing bindings tested with a mock plugin. |

RedDotsFinder was imported using `git subtree --squash`; the subtree commit
records the source revision and the original repository retains its history.
Future development belongs here.

## Development checks

```sh
go test -race -cover ./...
go vet ./...
node --test tests/printing.test.cjs
.venv/bin/python -m unittest discover -s tools/red-dots -p 'test_*.py'
```

Node.js 22+ is needed only for the JavaScript tests; Python 3.10+ is needed for
the coordinate tool. Plugin dialogs and physical print alignment require manual
testing on a compatible machine.

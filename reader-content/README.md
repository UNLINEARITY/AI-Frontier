# TextFold source packages

These packages supply OCR full text to the existing AI Frontier reading pages. The source-language text is parsed with [TextFold](https://github.com/chenxiachan/textfold), pinned to the commit recorded in `index.json`. Folding selects the original opening sentence and word excerpts; no model calls or translations are used.

`index.json` records PDF and OCR checksums, compressed document checksums, image checksums, and any source-bound table recovery. Each `<publisher>/<slug>/document.json.gz` contains the native TextFold reader data; `images/` contains the corresponding website images. Website builds validate and render these files without local PDFs or OCR dependencies.

Prepare or resume the packages from the repository root:

```sh
uv run --with-requirements requirements-textfold.txt python scripts/prepare_textfold.py
```

The ignored `ocr/` directory remains the persistent input layer. Official report links and existing summaries retain their own provenance. Report content remains under its original rights holders' terms; TextFold's Apache-2.0 code and the KaTeX MIT assets retain their respective licenses and notices in the vendored directories.

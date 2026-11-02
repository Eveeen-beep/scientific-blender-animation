# Automated checks

From the repository root, with Python 3.11:

```sh
python -m pip install Pillow PyYAML
python -m unittest discover -s tests -v
```

The tests generate small image and metadata fixtures in temporary directories.
They check PNG decoding, missing and damaged frames, dimensions, advisory dark
frames, provenance requirements, report safeguards, and unchanged input content.
Package checks validate skill frontmatter and local Markdown links without
fetching external links.

The `inspect_blend.py` tests use an intentionally unusable `bpy` stub to check
argument refusal before scene access. They do **not** run Blender, inspect a real
scene, evaluate animation, render frames, or validate scientific correctness.
Successful Blender inventory still requires a separate Blender runtime check.

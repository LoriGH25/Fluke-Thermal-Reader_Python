
## Publishing to PyPI

1. **Install build tools**
   ```bash
   pip install build twine
   ```

2. **Bump version** in `pyproject.toml` and `fluke_thermal_reader/__init__.py` (e.g. `0.2.1`).

3. **Build the package** (from repo root)
   ```bash
   python -m build
   ```
   This creates `dist/` with a `.tar.gz` (sdist) and a `.whl` (wheel).

4. **Check archives** (optional)
   ```bash
   twine check dist/*
   ```

5. **Upload to PyPI**
   ```bash
   twine upload dist/*
   ```
   Use your PyPI credentials (create an API token at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/); username `__token__`, password = token).

After upload, users can install with:
```bash
pip install fluke-thermal-reader
```

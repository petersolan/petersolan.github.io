# petersolan.github.io

Portfolio site: https://petersolan.github.io

All content lives in [`site.yml`](site.yml) (profile, links, projects, skills). On every push to
`main`, GitHub Actions runs [`scripts/build.py`](scripts/build.py) to render `_site/index.html` and
deploys it to GitHub Pages.

- **Add a project:** add an entry under `projects:` in `site.yml`, and its card image to `assets/img/`.
- **Card images:** put a screenshot in `assets/img/src/` (not committed) and run
  `python scripts/prepare_images.py` to make a 16:10 WebP card (optional crop boxes in the script).
- **Preview locally:** `pip install pyyaml`, `python scripts/build.py`, then
  `python -m http.server --directory _site 8000` and open http://localhost:8000.
- **Contact links:** fill `profile.links` in `site.yml`; empty links are not shown.

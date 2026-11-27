.PHONY: check site

# Check lesson sections, phone numbers against WHERE-TO-GO.md, and internal links.
check:
	python3 scripts/check.py

# Rebuild the GitHub Pages site in docs/ from the Markdown (needs the markdown package).
site:
	python3 site/build.py

.PHONY: check

# Check lesson sections, phone numbers against WHERE-TO-GO.md, and internal links.
check:
	python3 scripts/check.py

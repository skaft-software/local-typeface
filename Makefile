.PHONY: build validate checksums

build:
	fontforge -script sources/scripts/build_from_sfd_052.py
	python sources/scripts/build_variable_052.py

validate:
	python sources/scripts/validate_release_052.py

checksums:
	shasum -a 256 $$(find fonts sources specimens web LICENSES -type f | sort)


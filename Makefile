.PHONY: build validate package checksums

build:
	fontforge -script sources/scripts/build_from_sfd_053.py
	python sources/scripts/build_variable_053.py

validate:
	python sources/scripts/validate_release_053.py

package:
	python sources/scripts/package_release_053.py

checksums:
	shasum -a 256 $$(find fonts sources specimens web LICENSES -type f | sort)

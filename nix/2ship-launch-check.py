#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Check the packaged wrapper's native archive gate without retail assets."""

from pathlib import Path
import json
import runpy
import sys
import tempfile
import zipfile


def main():
    manifest = json.loads((Path(sys.argv[1]) / "manifest.json").read_text())
    wrapper = runpy.run_path(manifest["files"]["2ship"], run_name="archive_gate_check")
    current_archive = wrapper["current_archive"]
    records = {
        "version": bytes.fromhex("015354631c"),
        "portVersion": bytes.fromhex("01000500000001"),
        "objects/object_mag/gTitleScreenZeldaLogoTex": b"synthetic title",
        "objects/object_link_child/gLinkHumanSkel": b"synthetic player",
        "text/message_data_static/message_data_static": b"synthetic text",
    }
    with tempfile.TemporaryDirectory(prefix="2ship-archive-gate-") as temporary:
        archive = Path(temporary) / "mm.o2r"

        def write(entries):
            with zipfile.ZipFile(archive, "w") as data:
                for name, contents in entries.items():
                    data.writestr(name, contents)

        assert not current_archive(archive)
        write(records)
        assert current_archive(archive), "Packaged launcher must select native 5.0.1"
        for version in ("01000300000001", "01000500000000", "01000500010001"):
            write(dict(records, portVersion=bytes.fromhex(version)))
            assert not current_archive(archive), "Old/different native archives must regenerate"
        write(dict(records, version=bytes.fromhex("015354631d")))
        assert not current_archive(archive)
        for name in records:
            write({key: value for key, value in records.items() if key != name})
            assert not current_archive(archive), f"Missing {name} must fail"
            write(dict(records, **{name: b""}))
            assert not current_archive(archive), f"Empty {name} must fail"
        write(records)
        # Preserve ZIP structure but corrupt a resource's CRC-covered payload.
        contents = archive.read_bytes().replace(b"synthetic title", b"corrupted title")
        archive.write_bytes(contents)
        assert not current_archive(archive), "CRC failure must regenerate"
    print("Packaged 5.0.1 native archive versions, mandatory resources and CRC gate passed")


if __name__ == "__main__":
    main()

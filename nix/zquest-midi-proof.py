#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p 'python3.withPackages (ps: [ ps.numpy ])'
"""Private QST editing proof. This does not sanitize or license a whole quest.

Uses the pinned zquest-data producer's MIDI schema and serializer. Unparsed
sections stay byte-identical. Outputs are refused inside any Git checkout.
The caller supplies a privately downloaded input and an already built reader.
No candidate data is shipped with this tool. It performs no download,
editor build, deployment, or publication.
"""

import argparse
import hashlib
import logging
from pathlib import Path
import subprocess
import sys
import tempfile

READER_REVISION = "a52b5d19cb73439137ef281110c8831774000c5e"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def private_output(directory, input_path):
    directory = directory.resolve()
    if directory == input_path.parent or input_path.is_relative_to(directory):
        raise ValueError("Output must not contain the source quest")
    if any((parent / ".git").exists() for parent in (directory, *directory.parents)):
        raise ValueError("Candidate outputs must stay outside Git checkouts")
    if directory.exists():
        raise ValueError("Output directory already exists; choose a fresh directory")
    return directory


def load_reader(root):
    revision = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True, timeout=10
    ).strip()
    if revision != READER_REVISION:
        raise ValueError(f"Reader revision differs: {revision}")
    sys.path[:0] = [str(root), str(root / "src")]
    from zquest.extract import ZeldaClassicReader
    from zquest.section_utils import SECTION_IDS, serialize_section
    from decode_wrapper import py_encode

    return ZeldaClassicReader, SECTION_IDS, serialize_section, py_encode


def sections(reader):
    """Whole raw section records, including their native headers."""
    return {
        section_id: bytes(
            reader.b.data[header.offset : header.data_offset + header.size]
        )
        for section_id, header in reader.section_headers.items()
    }


def encode_payload(payload, output, encode):
    # Method -1 is the upstream encoder's unencrypted compressed PACKFILE.
    # It avoids that encoder's shared /tmp/qst.compressed legacy workspace.
    with tempfile.NamedTemporaryFile() as raw:
        raw.write(payload)
        raw.flush()
        result = encode(raw.name, str(output), -1, 0)
    if result != 0 or not output.is_file() or output.stat().st_size == 0:
        raise ValueError(f"Encoding failed for {output}: {result}")


def read_midi(path, reader_type, ids):
    reader = reader_type(str(path), {"only_sections": [ids.MIDIS]})
    reader.read_qst()
    if reader.is_too_old:
        raise ValueError("Pre-section QST format is outside this proof")
    if not reader.section_ok.get(ids.HEADER) or not reader.section_ok.get(ids.MIDIS):
        raise ValueError(f"Header or MIDI parsing failed: {reader.errors}")
    if reader.section_headers[ids.MIDIS].version != 4:
        raise ValueError("Only the observed MIDI section version 4 is supported")
    return reader


def prove(input_path, expected_hash, reader_root, output_dir, slot):
    input_path = input_path.resolve(strict=True)
    source_file = input_path.read_bytes()
    if digest(source_file) != expected_hash:
        raise ValueError("Input SHA-256 differs from the supplied receipt")
    if not 0 <= slot < 252:
        raise ValueError("MIDI slot must be between 0 and 251")
    output_dir = private_output(output_dir, input_path)
    reader_type, ids, serialize_section, encode = load_reader(reader_root.resolve())
    original = read_midi(input_path, reader_type, ids)
    if original.midis[slot] is None:
        raise ValueError(f"MIDI slot {slot} is already empty")

    midi_header = original.section_headers[ids.MIDIS]
    original_section = sections(original)[ids.MIDIS]
    if bytes(serialize_section(original, ids.MIDIS)) != original_section:
        raise ValueError("Unchanged MIDI serialization is not byte-identical")
    before = bytes(original.b.data)
    before_sections = sections(original)
    before_slots = [i for i, midi in enumerate(original.midis) if midi is not None]
    before_midi = dict(vars(original.midis[slot]))

    output_dir.mkdir(parents=True, mode=0o700)
    roundtrip_path = output_dir / "roundtrip.qst"
    encode_payload(before, roundtrip_path, encode)
    roundtrip = read_midi(roundtrip_path, reader_type, ids)
    if bytes(roundtrip.b.data) != before:
        raise ValueError("Unchanged save/reload altered the decoded payload")
    if sections(roundtrip) != before_sections:
        raise ValueError("Unchanged save/reload altered a native section")

    # Keep the 252-slot array. Do not renumber the remaining tracks.
    original.midis[slot] = None
    new_section = bytes(serialize_section(original, ids.MIDIS))
    after = (
        before[: midi_header.offset]
        + new_section
        + before[midi_header.data_offset + midi_header.size :]
    )
    removed_path = output_dir / f"slot-{slot}-removed.qst"
    encode_payload(after, removed_path, encode)
    removed = read_midi(removed_path, reader_type, ids)
    if bytes(removed.b.data) != after:
        raise ValueError("Edited save/reload altered the intended payload")
    after_sections = sections(removed)
    if list(before_sections) != list(after_sections):
        raise ValueError("Native section order changed")
    changed = [
        key for key in before_sections if before_sections[key] != after_sections[key]
    ]
    if changed != [ids.MIDIS]:
        raise ValueError(f"Unexpected changed sections: {changed}")
    after_slots = [i for i, midi in enumerate(removed.midis) if midi is not None]
    if after_slots != [i for i in before_slots if i != slot]:
        raise ValueError("Remaining MIDI slot identities changed")
    for i in after_slots:
        if vars(roundtrip.midis[i]) != vars(removed.midis[i]):
            raise ValueError(f"Remaining MIDI slot {i} changed")
    if input_path.read_bytes() != source_file:
        raise ValueError("Source quest changed")

    lines = [
        "PRIVATE EDITING PROOF ONLY. OTHER MEDIA AND RIGHTS REMAIN UNRESOLVED.",
        f"reader_revision {READER_REVISION}",
        f"input {input_path}",
        f"input_sha256 {digest(source_file)}",
        f"decoded_payload_sha256 {digest(before)}",
        f"roundtrip {roundtrip_path}",
        f"roundtrip_sha256 {digest(roundtrip_path.read_bytes())}",
        "roundtrip_decoded_payload_identical true",
        f"removed {removed_path}",
        f"removed_sha256 {digest(removed_path.read_bytes())}",
        f"removed_slot {slot}",
        f"removed_title {before_midi['title']!r}",
        f"populated_slots_before {before_slots}",
        f"populated_slots_after {after_slots}",
        "changed_sections MIDI",
        f"unchanged_other_sections {len(before_sections) - 1}",
        "source_unchanged true",
        "section_hashes_before_after",
    ]
    for section_id in before_sections:
        lines.append(
            f"{section_id!r} {digest(before_sections[section_id])} "
            f"{digest(after_sections[section_id])}"
        )
    receipt = output_dir / "receipt.txt"
    receipt.write_text("\n".join(lines) + "\n")
    print(receipt.read_text(), end="")
    return output_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--reader-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--remove-slot", required=True, type=int)
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR)
    try:
        prove(
            args.input,
            args.expected_sha256,
            args.reader_root,
            args.output_dir,
            args.remove_slot,
        )
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Proof failed: {error}\n")


if __name__ == "__main__":
    main()

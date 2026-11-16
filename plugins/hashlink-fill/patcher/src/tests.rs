use super::*;
use std::os::unix::fs::PermissionsExt;

fn fix() -> Fix {
    serde_json::from_str(include_str!("../../fixes/deadcells.json")).unwrap()
}

fn synthetic(matches: usize, debug: bool, wide: bool) -> Vec<u8> {
    let mut out = b"HLB\x04".to_vec();
    for n in [i32::from(debug), 0, 0, 2, 2, 0, 0, 1, 0, 0] {
        out.extend(encode_index(n));
    }
    let strings = b"Main\0onResize\0";
    out.extend((strings.len() as u32).to_le_bytes());
    out.extend(strings);
    out.extend([4, 8]);
    if debug {
        out.extend([1, 2, 0, 0, 0, b'x', 0, 1]); // one debug filename
    }
    out.push(3); // i32 type
    out.push(11); // Main object
    for n in [0, -1, 0, 0, 1, 0, 1, 0, -1] {
        out.extend(encode_index(n));
    }
    let w = if wide { 128 } else { 2 };
    let regs = w + 2;
    for n in [0, 0, regs, (matches * 5) as i32] {
        out.extend(encode_index(n));
    }
    out.extend(vec![0; regs as usize]);
    for _ in 0..matches {
        for (opcode, args) in [
            (62, vec![1, 0]),
            (49, vec![1, w, 2]),
            (0, vec![3, 1]),
            (58, vec![1]),
            (0, vec![3, w]),
        ] {
            out.push(opcode);
            for n in args {
                out.extend(encode_index(n));
            }
        }
    }
    if debug {
        out.extend([1, 0]); // select debug file 0
        out.extend(vec![4; matches * 5]); // line increments
        out.extend([1, 1, 0]); // one assignment: string 1, instruction 0
    }
    out
}

#[test]
fn lossless_roundtrip_and_exact_two_operand_edit() {
    for debug in [false, true] {
        for wide in [false, true] {
            let raw = synthetic(2, debug, wide);
            let code = bytecode::read(&raw, "Main", "onResize").unwrap();
            assert_eq!(code.serialized, raw);
            let out = patch(&raw, &fix()).unwrap();
            let patched = bytecode::read(&out, "Main", "onResize").unwrap();
            assert_eq!(patched.serialized, out);
            for (i, op) in patched.method.iter().enumerate() {
                if i % 5 == 1 {
                    assert_eq!(op.operands[0].value, op.operands[1].value);
                }
            }
            if !wide {
                assert_eq!(raw.iter().zip(&out).filter(|(a, b)| a != b).count(), 2);
            }
            assert!(patch(&out, &fix()).is_err());
        }
    }
}

#[test]
fn rejects_mismatch_ambiguous_or_missing_target_and_malformed_input() {
    for matches in [0, 1, 3] {
        assert!(patch(&synthetic(matches, false, false), &fix()).is_err());
    }
    let raw = synthetic(2, false, false);
    for length in 0..raw.len() {
        assert!(patch(&raw[..length], &fix()).is_err(), "length {length}");
    }
    for offset in [0, 3] {
        let mut corrupt = raw.clone();
        corrupt[offset] = 255;
        assert!(patch(&corrupt, &fix()).is_err());
    }
    let mut trailing = raw.clone();
    trailing.push(0);
    assert!(patch(&trailing, &fix()).is_err());
    let mut other = fix();
    other.class = "NotMain".into();
    assert!(patch(&raw, &other).is_err());
    other = fix();
    other.method = "other".into();
    assert!(patch(&raw, &other).is_err());
    // Same byte patterns outside the named method are not sufficient.
    let mut corrupt = raw.clone();
    let instruction = bytecode::read(&raw, "Main", "onResize")
        .unwrap()
        .method
        .remove(1);
    corrupt[instruction.operands[2].span.start] = 3;
    assert!(patch(&corrupt, &fix()).is_err());
}

#[test]
fn index_boundaries_and_noncanonical_encoding() {
    for n in [
        0,
        127,
        128,
        8191,
        8192,
        0x1fff_ffff,
        -1,
        -8191,
        -8192,
        -0x1fff_ffff,
    ] {
        let encoded = encode_index(n);
        assert_eq!(
            encoded.len(),
            if (0..128).contains(&n) {
                1
            } else if n.unsigned_abs() < 8192 {
                2
            } else {
                4
            }
        );
    }
    let mut raw = synthetic(2, false, false);
    raw.splice(4..5, [0x80, 0]); // flags 0 encoded noncanonically
    assert!(patch(&raw, &fix())
        .unwrap_err()
        .to_string()
        .contains("round-trip"));
}

#[test]
fn data_pattern_edit_and_hash_gates_are_enforced() {
    let raw = synthetic(2, false, false);
    let mut f = fix();
    f.pattern[2].operands[1] = Value::Literal(9);
    assert!(patch(&raw, &f).is_err());
    f = fix();
    f.known[0].original = hash(&raw);
    assert!(patch(&raw, &f)
        .unwrap_err()
        .to_string()
        .contains("known pair"));
    f = fix();
    f.file = "../hlboot.dat".into();
    assert!(f.validate().is_err());
    f = fix();
    f.edit.operand = 3;
    assert!(patch(&raw, &f).is_err());
}

#[test]
fn backup_atomic_mode_owner_preservation_and_verified_unknown_hash_idempotence() {
    let temp = tempfile::tempdir().unwrap();
    let home = temp.path().join("steam with spaces '; $() #");
    let f = fix();
    let target = home.join(&f.file);
    fs::create_dir_all(target.parent().unwrap()).unwrap();
    let original = synthetic(2, true, false);
    fs::write(&target, &original).unwrap();
    fs::set_permissions(&target, fs::Permissions::from_mode(0o750)).unwrap();
    let metadata = fs::metadata(&target).unwrap();
    let cache = home.join(".korri/hashlink-fill");
    assert!(prepare(&f, &home, "588650", &cache)
        .unwrap()
        .starts_with("patched "));
    assert_eq!(fs::read(cache.join(hash(&original))).unwrap(), original);
    let patched = fs::read(&target).unwrap();
    assert_eq!(patched, patch(&original, &f).unwrap());
    let meta = fs::metadata(&target).unwrap();
    assert_eq!(meta.mode() & 0o7777, 0o750);
    assert_eq!((meta.uid(), meta.gid()), (metadata.uid(), metadata.gid()));
    assert!(prepare(&f, &home, "588650", &cache)
        .unwrap()
        .starts_with("already patched"));
    assert_eq!(fs::metadata(&target).unwrap().ino(), meta.ino());
    assert_eq!(
        fs::metadata(&target).unwrap().mtime_nsec(),
        meta.mtime_nsec()
    );
    assert_eq!(fs::read(&target).unwrap(), patched);
    fs::write(cache.join(hash(&original)), b"bad backup").unwrap();
    assert!(prepare(&f, &home, "588650", &cache).is_err());
    fs::write(&target, &original).unwrap();
    assert!(prepare(&f, &home, "588650", &cache).is_err());
    assert_eq!(fs::read(&target).unwrap(), original);
}

#[test]
fn unrelated_missing_and_corrupt_files_are_not_modified() {
    let temp = tempfile::tempdir().unwrap();
    let cache = temp.path().join("cache");
    let f = fix();
    assert!(prepare(&f, Path::new("/absent"), "123", &cache).is_ok());
    assert!(prepare(&f, temp.path(), "588650", &cache).is_err());
    let target = temp.path().join(&f.file);
    fs::create_dir_all(target.parent().unwrap()).unwrap();
    fs::write(&target, b"not HLB").unwrap();
    assert!(prepare(&f, temp.path(), "588650", &cache).is_err());
    assert_eq!(fs::read(&target).unwrap(), b"not HLB");
    assert!(!cache.exists());
}

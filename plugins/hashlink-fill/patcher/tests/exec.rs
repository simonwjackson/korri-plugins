use std::{fs, process::Command};

#[test]
fn refusal_invalid_options_and_unrelated_apps_still_exec_with_exact_argv_and_exit_status() {
    let temp = tempfile::tempdir().unwrap();
    let fix = temp.path().join("fix.json");
    fs::write(&fix, include_bytes!("../../fixes/deadcells.json")).unwrap();
    let args = [
        "prepare",
        "--fix",
        fix.to_str().unwrap(),
        "--steam-home",
        temp.path().to_str().unwrap(),
        "--app",
        "588650",
        "--cache",
        temp.path().to_str().unwrap(),
    ];
    let output = Command::new(env!("CARGO_BIN_EXE_hl-fill"))
        .args(args)
        .args([
            "--",
            "/bin/sh",
            "-c",
            "printf '%s' \"$1\"; exit 23",
            "sh",
            "a '; $(exit 99) #",
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(23));
    assert_eq!(output.stdout, b"a '; $(exit 99) #");
    assert!(String::from_utf8_lossy(&output.stderr).contains("launching unchanged"));
    let output = Command::new(env!("CARGO_BIN_EXE_hl-fill"))
        .args(["bad-option", "--", "/bin/sh", "-c", "exit 17"])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(17));
    let output = Command::new(env!("CARGO_BIN_EXE_hl-fill"))
        .args([
            "prepare",
            "--fix",
            fix.to_str().unwrap(),
            "--steam-home",
            "/absent",
            "--app",
            "123",
            "--cache",
            "/absent",
            "--",
            "/bin/sh",
            "-c",
            "exit 19",
        ])
        .output()
        .unwrap();
    assert_eq!(output.status.code(), Some(19));
    assert!(String::from_utf8_lossy(&output.stderr).contains("no fix"));
}

#[test]
fn exec_replaces_the_wrapper_process() {
    let temp = tempfile::tempdir().unwrap();
    let child = Command::new(env!("CARGO_BIN_EXE_hl-fill"))
        .args(["invalid", "--", "/bin/sh", "-c", "printf '%s' $$"])
        .stdout(std::process::Stdio::piped())
        .spawn()
        .unwrap();
    let pid = child.id();
    let out = child.wait_with_output().unwrap();
    assert!(out.status.success());
    assert_eq!(String::from_utf8(out.stdout).unwrap(), pid.to_string());
    assert_eq!(fs::read_dir(temp.path()).unwrap().count(), 0);
}

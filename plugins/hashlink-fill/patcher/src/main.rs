use hl_fill::{prepare, Fix};
use std::{
    env,
    ffi::OsString,
    os::unix::process::CommandExt,
    path::{Path, PathBuf},
    process::Command,
};

fn options(args: &[OsString]) -> Result<(PathBuf, PathBuf, String, PathBuf), String> {
    if args.first().and_then(|s| s.to_str()) != Some("prepare") {
        return Err(
            "usage: hl-fill prepare --fix FILE --steam-home DIR --app ID --cache DIR -- COMMAND..."
                .into(),
        );
    }
    let mut fix = None;
    let mut home = None;
    let mut app = None;
    let mut cache = None;
    let mut rest = args[1..].chunks_exact(2);
    for pair in &mut rest {
        let slot = match pair[0].to_str() {
            Some("--fix") => &mut fix,
            Some("--steam-home") => &mut home,
            Some("--app") => &mut app,
            Some("--cache") => &mut cache,
            _ => return Err("unknown prepare option".into()),
        };
        if slot.replace(pair[1].clone()).is_some() {
            return Err("duplicate prepare option".into());
        }
    }
    if !rest.remainder().is_empty() {
        return Err("missing option value".into());
    }
    Ok((
        fix.ok_or("missing --fix")?.into(),
        home.ok_or("missing --steam-home")?.into(),
        app.ok_or("missing --app")?
            .into_string()
            .map_err(|_| "invalid --app")?,
        cache.ok_or("missing --cache")?.into(),
    ))
}

fn main() {
    let args: Vec<_> = env::args_os().skip(1).collect();
    let Some(separator) = args.iter().position(|a| a == "--") else {
        eprintln!("hl-fill: missing -- COMMAND; nothing to exec");
        std::process::exit(2);
    };
    let command = &args[separator + 1..];
    let Some(program) = command.first() else {
        eprintln!("hl-fill: missing COMMAND; nothing to exec");
        std::process::exit(2);
    };
    let result = options(&args[..separator])
        .map_err(|e| -> Box<dyn std::error::Error> { e.into() })
        .and_then(|(fix, home, app, cache)| {
            let fix = Fix::load(Path::new(&fix))?;
            prepare(&fix, &home, &app, &cache)
        });
    match result {
        Ok(status) => eprintln!("hl-fill: {status}"),
        Err(error) => {
            let status = format!("HashLink Fill skipped: {error}");
            eprintln!("hl-fill: {status}; launching unchanged");
            if env::var_os("NOTIFY_SOCKET").is_some() {
                let _ = Command::new("systemd-notify")
                    .arg("--no-block")
                    .arg(format!("--status={status}"))
                    .status();
            }
        }
    }
    let error = Command::new(program).args(&command[1..]).exec();
    eprintln!(
        "hl-fill: cannot exec {}: {error}",
        program.to_string_lossy()
    );
    std::process::exit(127);
}

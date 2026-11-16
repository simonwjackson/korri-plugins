pub mod bytecode;

use bytecode::{encode_index, OPCODES};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs,
    io::Write,
    os::unix::fs::{chown, MetadataExt},
    path::{Component, Path},
};
use tempfile::NamedTempFile;

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Fix {
    pub app: String,
    pub file: String,
    #[serde(rename = "type")]
    pub class: String,
    pub method: String,
    pub pattern: Vec<Pattern>,
    pub expected_matches: usize,
    pub edit: Edit,
    pub known: Vec<Known>,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Pattern {
    opcode: String,
    operands: Vec<Value>,
}
#[derive(Deserialize)]
#[serde(untagged)]
enum Value {
    Literal(i32),
    Bind(String),
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Edit {
    instruction: usize,
    operand: usize,
    from_operand: usize,
}
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Known {
    original: String,
    patched: String,
}

pub fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

impl Fix {
    pub fn load(path: &Path) -> Result<Self> {
        let fix: Self = serde_json::from_slice(&fs::read(path)?)?;
        fix.validate()?;
        Ok(fix)
    }
    fn validate(&self) -> Result<()> {
        if self.app.is_empty()
            || !self.app.bytes().all(|b| b.is_ascii_digit())
            || self.file.is_empty()
            || !Path::new(&self.file)
                .components()
                .all(|p| matches!(p, Component::Normal(_)))
            || self.class.is_empty()
            || self.method.is_empty()
            || self.expected_matches == 0
            || self.pattern.is_empty()
        {
            return Err("invalid fix target or expected match count".into());
        }
        for pattern in &self.pattern {
            let (_, arity) = OPCODES
                .iter()
                .find(|(name, _)| *name == pattern.opcode)
                .ok_or("unknown pattern opcode")?;
            if *arity < 0 || *arity as usize != pattern.operands.len() {
                return Err("pattern requires fixed-arity operands".into());
            }
            for value in &pattern.operands {
                if let Value::Bind(name) = value {
                    if name != "_" && (name.len() < 2 || !name.starts_with('$')) {
                        return Err("pattern binding must be $name or _".into());
                    }
                }
            }
        }
        let edit_op = self
            .pattern
            .get(self.edit.instruction)
            .ok_or("invalid edit instruction")?;
        if self.edit.operand >= edit_op.operands.len()
            || self.edit.from_operand >= edit_op.operands.len()
            || self.edit.operand == self.edit.from_operand
        {
            return Err("invalid edit operand".into());
        }
        for pair in &self.known {
            if [&pair.original, &pair.patched].iter().any(|s| {
                s.len() != 64
                    || !s
                        .bytes()
                        .all(|b| b.is_ascii_hexdigit() && !b.is_ascii_uppercase())
            }) || pair.original == pair.patched
            {
                return Err("invalid known SHA-256 pair".into());
            }
        }
        Ok(())
    }
}

/// Apply a data-defined pattern only inside the uniquely named method.
/// The reader has already proved the full no-edit byte-exact round trip.
pub fn patch(raw: &[u8], fix: &Fix) -> Result<Vec<u8>> {
    fix.validate()?;
    let code = bytecode::read(raw, &fix.class, &fix.method)?;
    let mut edits = Vec::new();
    let mut last_end = 0;
    for (start, window) in code.method.windows(fix.pattern.len()).enumerate() {
        let mut bindings = BTreeMap::new();
        let matches = window.iter().zip(&fix.pattern).all(|(op, pattern)| {
            op.name == pattern.opcode
                && op.operands.len() == pattern.operands.len()
                && op
                    .operands
                    .iter()
                    .zip(&pattern.operands)
                    .all(|(operand, value)| match value {
                        Value::Literal(n) => operand.value == *n,
                        Value::Bind(name) if name == "_" => true,
                        Value::Bind(name) => {
                            operand.value >= 0
                                && *bindings.entry(name).or_insert(operand.value) == operand.value
                        }
                    })
        });
        if !matches {
            continue;
        }
        if !edits.is_empty() && start < last_end {
            return Err("overlapping pattern matches".into());
        }
        last_end = start + window.len();
        let op = &window[fix.edit.instruction];
        let from = &op.operands[fix.edit.from_operand];
        let to = &op.operands[fix.edit.operand];
        if from.value == to.value {
            return Err("edit is already applied or has no effect".into());
        }
        edits.push((to.span.clone(), encode_index(from.value)));
    }
    if edits.len() != fix.expected_matches {
        return Err(format!(
            "expected {} matches in {}.{}, found {}",
            fix.expected_matches,
            fix.class,
            fix.method,
            edits.len()
        )
        .into());
    }
    let mut out = code.serialized;
    for (span, bytes) in edits.into_iter().rev() {
        out.splice(span, bytes);
    }
    bytecode::read(&out, &fix.class, &fix.method)?;
    if let Some(pair) = fix.known.iter().find(|pair| pair.original == hash(raw)) {
        if hash(&out) != pair.patched {
            return Err("patched hash does not match known pair".into());
        }
    }
    Ok(out)
}

/// Verified cache receipts are tied to the exact fix bytes and revalidated
/// against a content-addressed original. They never authorize arbitrary hashes.
fn verified(raw: &[u8], fix: &Fix, cache: &Path) -> bool {
    let receipt = cache.join(format!("{}.verified", hash(raw)));
    let Ok(original_hash) = fs::read_to_string(receipt) else {
        return false;
    };
    if original_hash.len() != 64 || !original_hash.bytes().all(|b| b.is_ascii_hexdigit()) {
        return false;
    }
    let Ok(original) = fs::read(cache.join(&original_hash)) else {
        return false;
    };
    hash(&original) == original_hash && patch(&original, fix).is_ok_and(|patched| patched == raw)
}

pub fn prepare(fix: &Fix, steam_home: &Path, app: &str, cache: &Path) -> Result<String> {
    if fix.app != app {
        return Ok(format!("app {app}: no fix, launch unchanged"));
    }
    let home = steam_home.canonicalize()?;
    let target = home.join(&fix.file);
    if fs::symlink_metadata(&target)?.file_type().is_symlink()
        || !target.canonicalize()?.starts_with(&home)
    {
        return Err("target must be a regular file within Steam home".into());
    }
    let meta = fs::metadata(&target)?;
    if !meta.is_file() || meta.len() > 256 * 1024 * 1024 {
        return Err("invalid or oversized target".into());
    }
    let original = fs::read(&target)?;
    let original_hash = hash(&original);
    if fix.known.iter().any(|pair| pair.patched == original_hash) || verified(&original, fix, cache)
    {
        return Ok(format!("already patched {original_hash}"));
    }
    let patched = patch(&original, fix)?;
    let patched_hash = hash(&patched);
    fs::create_dir_all(cache)?;
    let backup = cache.join(&original_hash);
    // Persist without clobbering an existing original, even across processes.
    let mut saved = NamedTempFile::new_in(cache)?;
    saved.write_all(&original)?;
    saved.as_file().sync_all()?;
    match saved.persist_noclobber(&backup) {
        Ok(_) => (),
        Err(error) if error.error.kind() == std::io::ErrorKind::AlreadyExists => (),
        Err(error) => return Err(error.into()),
    }
    if fs::read(&backup)? != original {
        return Err("existing backup does not match original".into());
    }
    fs::File::open(cache)?.sync_all()?;
    let parent = target.parent().ok_or("target has no parent")?;
    let mut temp = NamedTempFile::new_in(parent)?;
    temp.write_all(&patched)?;
    chown(temp.path(), Some(meta.uid()), Some(meta.gid()))?;
    temp.as_file().set_permissions(meta.permissions())?;
    temp.as_file().sync_all()?;
    if fs::read(temp.path())? != patched {
        return Err("temporary file verification failed".into());
    }
    if fs::read(&target)? != original {
        return Err("target changed during patch; leaving it unchanged".into());
    }
    temp.persist(&target)?;
    fs::File::open(parent)?.sync_all()?;
    if hash(&fs::read(&target)?) != patched_hash {
        return Err("installed file verification failed".into());
    }
    let mut receipt = NamedTempFile::new_in(cache)?;
    receipt.write_all(original_hash.as_bytes())?;
    receipt.as_file().sync_all()?;
    receipt.persist(cache.join(format!("{patched_hash}.verified")))?;
    fs::File::open(cache)?.sync_all()?;
    Ok(format!(
        "patched {original_hash} -> {patched_hash}; backup {}",
        backup.display()
    ))
}

#[cfg(test)]
mod tests;

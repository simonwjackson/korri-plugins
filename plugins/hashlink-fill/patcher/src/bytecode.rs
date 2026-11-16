//! A lossless HLB v4 reader. Layout follows HashLink's src/code.c and opcodes.h.
//! Only method lookup and instruction operands are interpreted. Raw pools and
//! debug encodings are retained, not normalized. Every index is re-encoded and
//! the complete no-edit serialization must equal the input before any edit.
use std::ops::Range;

pub type Result<T> = std::result::Result<T, String>;

pub const OPCODES: &[(&str, i8)] = &[
    ("Mov", 2),
    ("Int", 2),
    ("Float", 2),
    ("Bool", 2),
    ("Bytes", 2),
    ("String", 2),
    ("Null", 1),
    ("Add", 3),
    ("Sub", 3),
    ("Mul", 3),
    ("SDiv", 3),
    ("UDiv", 3),
    ("SMod", 3),
    ("UMod", 3),
    ("Shl", 3),
    ("SShr", 3),
    ("UShr", 3),
    ("And", 3),
    ("Or", 3),
    ("Xor", 3),
    ("Neg", 2),
    ("Not", 2),
    ("Incr", 1),
    ("Decr", 1),
    ("Call0", 2),
    ("Call1", 3),
    ("Call2", 4),
    ("Call3", 5),
    ("Call4", 6),
    ("CallN", -1),
    ("CallMethod", -1),
    ("CallThis", -1),
    ("CallClosure", -1),
    ("StaticClosure", 2),
    ("InstanceClosure", 3),
    ("VirtualClosure", 3),
    ("GetGlobal", 2),
    ("SetGlobal", 2),
    ("Field", 3),
    ("SetField", 3),
    ("GetThis", 2),
    ("SetThis", 2),
    ("DynGet", 3),
    ("DynSet", 3),
    ("JTrue", 2),
    ("JFalse", 2),
    ("JNull", 2),
    ("JNotNull", 2),
    ("JSLt", 3),
    ("JSGte", 3),
    ("JSGt", 3),
    ("JSLte", 3),
    ("JULt", 3),
    ("JUGte", 3),
    ("JNotLt", 3),
    ("JNotGte", 3),
    ("JEq", 3),
    ("JNotEq", 3),
    ("JAlways", 1),
    ("ToDyn", 2),
    ("ToSFloat", 2),
    ("ToUFloat", 2),
    ("ToInt", 2),
    ("SafeCast", 2),
    ("UnsafeCast", 2),
    ("ToVirtual", 2),
    ("Label", 0),
    ("Ret", 1),
    ("Throw", 1),
    ("Rethrow", 1),
    ("Switch", -1),
    ("NullCheck", 1),
    ("Trap", 2),
    ("EndTrap", 1),
    ("GetI8", 3),
    ("GetI16", 3),
    ("GetMem", 3),
    ("GetArray", 3),
    ("SetI8", 3),
    ("SetI16", 3),
    ("SetMem", 3),
    ("SetArray", 3),
    ("New", 1),
    ("ArraySize", 2),
    ("Type", 2),
    ("GetType", 2),
    ("GetTID", 2),
    ("Ref", 2),
    ("Unref", 2),
    ("Setref", 2),
    ("MakeEnum", -1),
    ("EnumAlloc", 2),
    ("EnumIndex", 2),
    ("EnumField", 4),
    ("SetEnumField", 3),
    ("Assert", 0),
    ("RefData", 2),
    ("RefOffset", 3),
    ("Nop", 0),
    ("Prefetch", 3),
    ("Asm", 3),
];

#[derive(Debug)]
pub struct Operand {
    pub value: i32,
    pub span: Range<usize>,
}
#[derive(Debug)]
pub struct Instruction {
    pub name: &'static str,
    pub operands: Vec<Operand>,
}
pub struct Bytecode {
    pub serialized: Vec<u8>,
    pub method: Vec<Instruction>,
}

pub fn encode_index(value: i32) -> Vec<u8> {
    let n = value.unsigned_abs();
    let sign = if value < 0 { 0x20 } else { 0 };
    if value >= 0 && n < 0x80 {
        vec![n as u8]
    } else if n < 0x2000 {
        vec![0x80 | sign | (n >> 8) as u8, n as u8]
    } else {
        vec![
            0xc0 | sign | (n >> 24) as u8,
            (n >> 16) as u8,
            (n >> 8) as u8,
            n as u8,
        ]
    }
}

struct Reader<'a> {
    data: &'a [u8],
    pos: usize,
    output: Vec<u8>,
}
impl<'a> Reader<'a> {
    fn raw(&mut self, size: usize) -> Result<&'a [u8]> {
        let end = self.pos.checked_add(size).ok_or("size overflow")?;
        let bytes = self.data.get(self.pos..end).ok_or("truncated HLB")?;
        self.output.extend_from_slice(bytes);
        self.pos = end;
        Ok(bytes)
    }
    fn byte(&mut self) -> Result<u8> {
        Ok(self.raw(1)?[0])
    }
    fn index(&mut self) -> Result<i32> {
        let start = self.pos;
        let b = self.byte()?;
        let n = if b < 0x80 {
            i32::from(b)
        } else if b < 0xc0 {
            (i32::from(b & 31) << 8) | i32::from(self.byte()?)
        } else {
            (i32::from(b & 31) << 24)
                | (i32::from(self.byte()?) << 16)
                | (i32::from(self.byte()?) << 8)
                | i32::from(self.byte()?)
        };
        let value = if b >= 0x80 && b & 0x20 != 0 { -n } else { n };
        self.output.truncate(start);
        self.output.extend(encode_index(value));
        Ok(value)
    }
    fn count(&mut self) -> Result<usize> {
        let n = usize::try_from(self.index()?).map_err(|_| "negative count/index")?;
        // No record count can exceed the entire file. Reject before allocating.
        if n > self.data.len() {
            return Err("count exceeds file size".into());
        }
        Ok(n)
    }
    fn indices(&mut self, n: usize) -> Result<()> {
        for _ in 0..n {
            self.index()?;
        }
        Ok(())
    }
    fn strings(&mut self, count: usize) -> Result<Vec<&'a [u8]>> {
        let size = u32::from_le_bytes(self.raw(4)?.try_into().unwrap()) as usize;
        let data = self.raw(size)?;
        let mut at = 0usize;
        let mut strings = Vec::new();
        for _ in 0..count {
            let size = self.count()?;
            let end = at.checked_add(size).ok_or("string size overflow")?;
            if data.get(end) != Some(&0) {
                return Err("invalid string terminator".into());
            }
            strings.push(data.get(at..end).ok_or("invalid string length")?);
            at = end + 1;
        }
        if at != data.len() {
            return Err("unused string pool bytes".into());
        }
        Ok(strings)
    }
    fn string(&mut self, strings: &[&'a [u8]]) -> Result<&'a [u8]> {
        strings
            .get(self.count()?)
            .copied()
            .ok_or("invalid string index".into())
    }
    fn type_ref(&mut self, ntypes: usize) -> Result<()> {
        if self.count()? >= ntypes {
            return Err("invalid type index".into());
        }
        Ok(())
    }
    fn fields(&mut self, n: usize, strings: &[&'a [u8]], ntypes: usize) -> Result<()> {
        for _ in 0..n {
            self.string(strings)?;
            self.type_ref(ntypes)?;
        }
        Ok(())
    }
    fn instruction(&mut self) -> Result<Instruction> {
        let code = self.byte()?;
        let &(name, arity) = OPCODES.get(usize::from(code)).ok_or("unsupported opcode")?;
        let mut operands = Vec::new();
        let mut operand = |r: &mut Self| -> Result<()> {
            let start = r.pos;
            let value = r.index()?;
            operands.push(Operand {
                value,
                span: start..r.pos,
            });
            Ok(())
        };
        if arity >= 0 {
            for _ in 0..arity {
                operand(self)?;
            }
        } else if code == 70 {
            operand(self)?; // switch register
            let count = self.count()?;
            for _ in 0..=count {
                operand(self)?;
            } // cases, then end
        } else {
            operand(self)?;
            operand(self)?;
            let count = usize::from(self.byte()?); // call argument count is one byte
            for _ in 0..count {
                operand(self)?;
            }
        }
        Ok(Instruction { name, operands })
    }
    fn debug(&mut self, nops: usize, nfiles: usize) -> Result<()> {
        let mut ops = 0;
        while ops < nops {
            let b = self.byte()?;
            if b & 1 != 0 {
                let file = (usize::from(b >> 1) << 8) | usize::from(self.byte()?);
                if file >= nfiles {
                    return Err("invalid debug file".into());
                }
            } else if b & 2 != 0 {
                let count = usize::from((b >> 2) & 15);
                if count == 0 {
                    return Err("empty debug run".into());
                }
                ops += count;
            } else if b & 4 != 0 {
                ops += 1;
            } else {
                self.raw(2)?;
                ops += 1;
            }
        }
        if ops != nops {
            return Err("debug run exceeds op count".into());
        }
        let assigns = self.count()?;
        self.indices(assigns.checked_mul(2).ok_or("assignment size overflow")?)
    }
}

pub fn read(data: &[u8], class: &str, method: &str) -> Result<Bytecode> {
    let mut r = Reader {
        data,
        pos: 0,
        output: Vec::with_capacity(data.len()),
    };
    if r.raw(4)? != b"HLB\x04" {
        return Err("requires HLB version 4".into());
    }
    let flags = r.count()?;
    if flags & !1 != 0 {
        return Err("unsupported HLB flags".into());
    }
    let nints = r.count()?;
    let nfloats = r.count()?;
    let nstrings = r.count()?;
    let ntypes = r.count()?;
    let nglobals = r.count()?;
    let nnatives = r.count()?;
    let nfunctions = r.count()?;
    let nconstants = r.count()?;
    r.count()?; // entrypoint
    r.raw(nints.checked_mul(4).ok_or("integer pool overflow")?)?;
    r.raw(nfloats.checked_mul(8).ok_or("float pool overflow")?)?;
    let strings = r.strings(nstrings)?;
    let ndebug = if flags & 1 != 0 {
        let count = r.count()?;
        r.strings(count)?;
        count
    } else {
        0
    };
    let mut target = None;
    for _ in 0..ntypes {
        match r.byte()? {
            0..=9 | 12 | 13 | 16 => (),
            10 | 20 => {
                let n = usize::from(r.byte()?);
                for _ in 0..=n {
                    r.type_ref(ntypes)?;
                }
            }
            11 | 21 => {
                let name = r.string(&strings)?;
                let parent = r.index()?;
                if parent < -1 || parent >= ntypes as i32 {
                    return Err("invalid superclass".into());
                }
                r.count()?; // global
                let fields = r.count()?;
                let protos = r.count()?;
                let bindings = r.count()?;
                r.fields(fields, &strings, ntypes)?;
                for _ in 0..protos {
                    let name_method = r.string(&strings)?;
                    let function = r.count()?;
                    r.index()?; // virtual slot, may be -1
                    if name == class.as_bytes()
                        && name_method == method.as_bytes()
                        && target.replace(function).is_some()
                    {
                        return Err("ambiguous method".into());
                    }
                }
                r.indices(bindings.checked_mul(2).ok_or("binding size overflow")?)?;
            }
            14 | 19 | 22 => r.type_ref(ntypes)?,
            15 => {
                let n = r.count()?;
                r.fields(n, &strings, ntypes)?;
            }
            17 => {
                r.string(&strings)?;
            }
            18 => {
                r.string(&strings)?;
                r.count()?;
                let n = r.count()?;
                for _ in 0..n {
                    r.string(&strings)?;
                    let params = r.count()?;
                    for _ in 0..params {
                        r.type_ref(ntypes)?;
                    }
                }
            }
            _ => return Err("unsupported type kind".into()),
        }
    }
    let target = target.ok_or("method not found")?;
    for _ in 0..nglobals {
        r.type_ref(ntypes)?;
    }
    for _ in 0..nnatives {
        r.string(&strings)?;
        r.string(&strings)?;
        r.type_ref(ntypes)?;
        r.count()?;
    }
    let mut found = None;
    for _ in 0..nfunctions {
        r.type_ref(ntypes)?;
        let index = r.count()?;
        let nregs = r.count()?;
        let nops = r.count()?;
        for _ in 0..nregs {
            r.type_ref(ntypes)?;
        }
        let mut instructions = Vec::new();
        for _ in 0..nops {
            let op = r.instruction()?;
            if index == target {
                instructions.push(op);
            }
        }
        if index == target && found.replace(instructions).is_some() {
            return Err("duplicate function index".into());
        }
        if flags & 1 != 0 {
            r.debug(nops, ndebug)?;
        }
    }
    for _ in 0..nconstants {
        if r.count()? >= nglobals {
            return Err("invalid constant global".into());
        }
        let fields = r.count()?;
        r.indices(fields)?;
    }
    if r.pos != data.len() {
        return Err("trailing bytes in HLB".into());
    }
    if r.output != data {
        return Err("HLB does not round-trip byte-exactly".into());
    }
    Ok(Bytecode {
        serialized: r.output,
        method: found.ok_or("method function not found")?,
    })
}

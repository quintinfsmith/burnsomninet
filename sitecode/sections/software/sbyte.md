# Sbyte
An in-console byte editor.

[Git Project](/project/sbyte)
[Crates.io](https://crates.io/crates/sbyte)

## Table of Contents
- [About](#abt)
    - [Features](#abt_a)
    - [Planned Features](#abt_b)
- [Downloads](#dls)

- [Controls](#ctrls)
    - [Default](#ctrls_a)
    - [Overwrite](#ctrls_b)
- [Shell Commands](#shell)
- [Regex Modifications](#rgx)
    - [Byte Wildcarding](#rgx_a)


<a name="abt"></a>
## About
It's a byte editor. It's console-based. I don't *think* it sucks.

<a name="abt_a"></a>
### Features
- Hexadecimal, Binary and Decimal views
- Configurable controls
- Vi-ish environment
- Regex-ish searching


<a name="abt_b"></a>
### Planned Features
- Extensibility with Python
- Relative-sequence-based searching (ie. You don't know the initial value but you know the [pro|pre]ceeding relative bytes)
- Data marking: Set a byte or chunk as a checksum, pointer, etc.
- Scriptability: Use the functionality of sbyte just by running a script.

<a name="dls"></a>
## Downloads
### Packages
- [Arch](https://github.com/quintinfsmith/sbyte/releases/download/v0.1.0/sbyte-0.1.0.tar.gz)
- [Debian/Ubuntu](https://github.com/quintinfsmith/sbyte/releases/download/v0.1.0/sbyte-0.1.0.deb)

### Crates.io:
```bash
cargo install sbyte
sbyte <filename>
```

<a name="ctrls"></a>
## Controls
The current defaults *(while prone to change until v1.0.0 is released)* are as follows:

**NOTE**: If the register is set, user actions are applied that many times
#### While in default mode
<a name="ctrls_a"></a>
- `0-9` add digit to register
- `=` cycle between hex/binary/decimal views
- `x` cut selection
- `p` paste
##### Movement & Selection
- `h` Move Cursor Left
- `j` Move Cursor Down
- `k` Move Cursor Up
- `l` Move Cursor Right
- `H` Decrease length of selection
- `J` Increase length of selection by a line
- `K` Decrease length of selection by a line
- `L` Increase length of selection
- `R` Jump to index denoted by selection (Big Endian)
- `T` Jump to index denoted by selection (Little Endian)
- `/` search

##### Mode Switching
- `o` switch to mode overwrite
- `i` switch to mode insert
- `:` switch to shell

##### History & Automation
- `u` undo action
- `ctrl+r` redo action
- `q` start/stop recording user actions
- `@` play back recorded user actions

##### Masking
- `~` apply NOT to cursor selection
- `&` apply AND to cursor selection
- `|` apply OR to cursor selection
- `^` apply XOR to cursor selection

##### Math
- `+` increment selection (ignore overflow)
- `-` decrement selection (ignore overflow)

#### While in overwrite mode
<a name="ctrls_b"></a>
**Note:** Depending on which view is enabled, different numerals will be active.
- `0-9 a-f` overwrite digit
- `p` paste
- `x` cut selection
- `h` Move sub-cursor to next digit
- `l` Move sub-cursor to previous digit
- `esc` return to default mode

<a name="shell"></a>
## Shell Commands
- `find <pattern>` Search for, and jump to, a pattern
- `fr <pattern> <replacewith>` Search for all instances of pattern and replace them
- `insert <pattern>` Insert pattern
- `overwrite <pattern>` Overwrite with pattern
- `q` Quit
- `w` Save
- `w <path>` Save to *path*
- `wq` Save & Quit

#### Bitwise Masks
- `and <mask>`
- `nand <mask>`
- `or <mask>`
- `nor <mask>`
- `xor <mask>`
- `not`

#### Record & Play
- `rec <keyword>` Start recording user actions and save playback to *keyword*
- `rec` If recording, stop the recording
- `play <keyword>` Replay user actions saved to *keyword*


<a name="rgx"></a>
## Regex modifications
Regex is supported in searches, however some modifications have been made to make it more useful in the context of all bytes rather than just the human-readable ones.
<a name="rgx_a"></a>
### Byte Wildcarding
Use a `.` to indicate a wildcard within a byte.

#### Examples
This will find all bytes from \x90 to \x9F:
```
find \x9.
```

This can also be done in binary:
```
find \b1001....
```
and doesn't need to be sequential
```
find \b100100.0
```
will match \x90 & \x92


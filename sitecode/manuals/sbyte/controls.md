# Controls
The current defaults *(while prone to change until v1.0.0 is released)* are as follows:

**NOTE**: If the register is set, user actions are applied that many times
## While in default mode
<a name="ctrls_a"></a>
- `0-9` add digit to register
- `=` cycle between hex/binary/decimal views
- `x` cut selection
- `p` paste
### Movement & Selection
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

### Mode Switching
- `o` switch to mode overwrite
- `i` switch to mode insert
- `:` switch to shell

### History & Automation
- `u` undo action
- `ctrl+r` redo action
- `q` start/stop recording user actions
- `@` play back recorded user actions

### Masking
- `~` apply NOT to cursor selection
- `&` apply AND to cursor selection
- `|` apply OR to cursor selection
- `^` apply XOR to cursor selection

### Math
- `+` increment selection (ignore overflow)
- `-` decrement selection (ignore overflow)

## While in overwrite mode
**Note:** Depending on which view is enabled, different numerals will be active.
- `0-9 a-f` overwrite digit
- `p` paste
- `x` cut selection
- `h` Move sub-cursor to next digit
- `l` Move sub-cursor to previous digit
- `esc` return to default mode


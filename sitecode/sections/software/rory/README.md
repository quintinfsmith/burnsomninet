# Rory
Learn Piano using MIDI files and a MIDI Keyboard

[Git Project](/project/rory/)
[Pypi](https://pypi.org/project/rory/)

## Table of Contents
- [About](#abt)
- [Installation & Usage](#inst)
    - [Packages](#inst_a)
    - [Running](#inst_b)
- [The Interface](#intrf)
- [Features](#funcs)
    - [The Help Window](#funcs_help)
    - [The Register](#funcs_a)
    - [Position Control](#funcs_b)
    - [Loop Control](#funcs_c)
    - [Ignoring Channels](#funcs_d)
    - [Quitting](#funcs_e)

<a name="abt"></a>
## About
It may look like a game, but Rory is a tool made to help in learning to play piano. The idea isn't to replace notation, but to free a new player from having to learn 2 skills at once (physically playing *and* sight reading). With Rory, you can focus on just getting the muscle memory.

![Rory](/content/rory_screenshot.png)

At every new note, the roll will stop and wait for the correct input from the midi device.

Highlighted notes are sharps, otherwise they are naturals.

Each track will display as a different color. This allows for delineation between left and right hands.

The active line will be a double line when it lands on a beat and a single line otherwise.

Rory will attempt to to label any chords played. This feature is still a work in progress.






<a name="inst"></a>
## Installation & Usage
<a name="inst_a"></a>
### Packages
Currently, Rory is only distributed through pypi.
```bash
pip install rory
```

<a name="inst_b"></a>
### Running
Make sure the terminal is at least at a width of 106 characters.<br/>
From the terminal:
```bash
rory /path/to/file.mid
```

<a name="funcs"></a>
## Features
<a name="funcs_help"></a>
### The Help Window
`h` will bring up the help window, showing all possible controls

<a name="funcs_a"></a>
### The Register
There is a number register that gets passed to user functions.<br/>
Type the number to set the register.<br/>
Then hit the desired key *or* esc to clear the register.

<a name="funcs_b"></a>
### Position Control
- `p` to jump to the position specified by the register.<br/>
- `j` to move to the next position, or the next nth position if there is a number in the register.<br/>
- `k` to move to the previous position, or the next nth position if there is a number in the register.

<a name="funcs_c"></a>
### Loop Control
Boundaries can be set to practice a single section of a piece.  As the player position passes the end boundary, it will jump back to the start boundary.<br/>
- `[` to set the start boundary specified by the registry<br/>
- `]` to set the end boundary specified by the registry<br/>
- `\` to reset the boundaries

<a name="funcs_d"></a>
### Ignoring channels
You can ignore a channel in order to focus on one hand<br/>
`i` will set ignore the channel set in the register<br/>
`u` will stop ignoring all ignored channels

<a name="funcs_e"></a>
### Quitting
- `q` to quit

### Planned Features
- cropping out the unused sections of the keyboard

### Possible Features
- Fingering calculator



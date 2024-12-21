# How Tuning Works

## Equal Temperament Tuning
Simply put, this means each note is **double** the frequency of the same note one octave lower.

Mathematically speaking, equal temperament is defined thusly:

```
    base_frequency * (2 ^ ( x / radix ))
```

Where, relative to western music:

```
    base_frequency = 27.5
    radix = 12
```

27.5Hz is the frequency of the **A<sub>0</sub>** on a piano and there are **12** *keys per octave*



## Using The Tuning Table
The tuning table has 3 parts:

### Radix
Changing the Radix changes the *number of notes per octave*. The *note tunings* will default to **equal temperament** when this gets changed.
This means you could set the radix to 24 and use the even notes as normal and the odd notes as micro-tones. Or you could experiment with different sized octaves.

### Note Tunings
Instead of using "cents" and "semi_tones", Pagan uses *ratios* and *offsets*.

The **Offset** is the index of the note given a list of notes. (See [How to Read](#how_to_read)).

The **Ratios** are the ```(x / radix)``` part of the function in equal temperament tuning.

This means that if you want to tune a key *up*, you need to have a ratio between ```(offset / radix)``` and ```((offset + 1) / radix)```

If you are unfamiliar with a "cent", a cent is a 1/100th step between each note. This means that in order to tune a note **Up One Cent**, the ratio would be:
```
((offset * 100) + 1) / (radix * 100)
```

### Transpose

Pagan defaults to **<sub>0</sub>0 = 27.5Hz** (or A<sub>0</sub>).

The transpose is which offset you want to start at.

So if you wanted to set <sub>0</sub>0 to **C**, you would change Transpose to 3. (A:0, A#:1, B:2, C:3)





# The Standard
### Notes are expressed in two parts: 'The Octave' and 'The Offset'
This is why I call it radix notation. Notes are just being express as n-base numbers. If you use 12 tones, you get 12 digits.
<b>   3rd octave --> 2 5 <-- 6th note (D) </b>

** Note how the values seem to be off by one, if that doesn't make sense to you consider this: the *first* 10 numbers don't have a*1* before them.

Here's a quick reference to convert western notes:
<table style="text-align: center;">
<tr><th>Western Note </th><th>Radix </th></tr>
<tr><td>A1           </td><td>00    </td></tr>
<tr><td>A#1          </td><td>01    </td></tr>
<tr><td>B1           </td><td>02    </td></tr>
<tr><td>C1           </td><td>03    </td></tr>
<tr><td>C#1          </td><td>04    </td></tr>
<tr><td>D1           </td><td>05    </td></tr>
<tr><td>D#1          </td><td>06    </td></tr>
<tr><td>E1           </td><td>07    </td></tr>
<tr><td>F1           </td><td>08    </td></tr>
<tr><td>F#1          </td><td>09    </td></tr>
<tr><td>G1           </td><td>0A    </td></tr>
<tr><td>G#1          </td><td>0B    </td></tr>
<tr><td>A2           </td><td>10    </td></tr>
</table>

Keep in mind that I'm just using 12 as an example. **Any** number of tones can be expressed if you have the instrument to play it or the software supports it (its in the works).

<hr>

### No Time signature, no measures. Only beats.
Every `|` delimits a beat.

``` { 43 | 43 | 43 | 43 } ```

is the equivalent of this:

<img src="/content/manuals/radixulous/4cs.png">
<hr>

### Subdivisions
Every piece starts and ends with `{` & `}`

Every `[` and `]` delimit a subdivison

Every beat or subdivision is split by commas

``` { 43 | 43, [53,4B] | 43, 43, 43  | .. } ```

is the equivalent of this:

<img src="/content/manuals/radixulous/divisions.png">
<hr>



### One note per line

More than one line can exist, but only one note can be placed simultaneously per line

```
    {50 |50 |50 |50 }
    {53 |54 |53 |.. }
    {57 |57 |.. |60 }
```

is the equivalent of this:

<img src="/content/manuals/radixulous/single.png">
<hr>

### Relative Notes

`+`/`-`/`v`/`^` can be used to denote a note is relative

`+N` means that this note is **N** steps **up** from the previous

`-N` means that this note is **N** steps **down** from the previous

`^N` means that this note is **N** octaves **up** from previous

`vN` means that this note is **N** octaves **down** from previous

``` { 43 | ^1, v1 | +4, +3 | -4, -3 } ```

is the equivalent of:

<img src="/content/manuals/radixulous/relative.png">
<hr>


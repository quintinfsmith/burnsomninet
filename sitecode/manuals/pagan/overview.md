# Controls Overview

## The Opus Config Menu
Can be dragged out from the left side of the screen.
From here you can:
    1. Set the opus's name
    2. Transpose the Opus
    3. Set the Opus's Tempo
    4. Add/Remove New Channels (Instruments) to the Opus
    5. Save the Opus
    6. Move to a copy of the current opus
    7. Delete the Opus
    8. Export the Opus to a Midi file

## The Line Control Menu
Can be opened by tapping any line label on the left side of the screen.
From here you can:
    1. Control the line's volume.
    2. Add a line to the channel (to add a channel see the Opus Config Menu)
    3. Remove a line from the channel. This button will *not* be visible when there is only 1 line in the given channel.

## The Column Control Menu
Can be opened by tapping any column label on the top of the screen.
From here you can:
    1. Add more beats to the column. (Short tap for 1. Hold to input a number)
    2. Remove beats from the column. (Short tap for 1. Hold to input a number)

## The Note Control Menu
Can be opened by tapping on a Cell in the Editor.
From here you can:
    1. Split a cell into finite divisions. (Hold to input a number)
    2. Insert an empty cell after the currently selected one. (Hold to input a number)
    3. Remove the selected cell. (Hold to remove all cell at the current level)
    4. Unset a note.
    5. Set a note's duration (Hold to reset to x1)
    6. Set a note's octave
    7. Set a note's offset (This is equivalent to abcdefg etc) Note that the options are in radix-12, so A = 10 and B = 11
    8. *Change to Relative/Absolute Note Input Mode*. This can be toggled from the settings menu. see "Relative Notes" for more information

## Split a rest/note
Tap the position you want to divide.
Then tap the split (![](/manuals/pagan/svgs/split.svg)) button.
Hold it to specify how many pieces you want to split it into.

## Insert a rest/note
Tap the position immediately before where you want to insert.
Then tap the insert (![](/manuals/pagan/svgs/insert.svg)) button.
Hold it to specify how many rests you want to insert.

## Remove a rest/note
Tap the position you want to remove.
Then tap the remove (![](/manuals/pagan/svgs/delete.svg)) button.
Hold it to remove all immediate siblings and as well.

## Unset a note
Tap the note you want to unset.
Then tap the unset (![](/manuals/pagan/svgs/unset.svg)) button.

## Set a note
Tap where you want to place a note.
Then use the **top row** of the note-picker to set the **octave**,
and the **bottom row** to set the **key**.

### Relative Notes
Tap either the **+** or the **-** next to the note-picker.
Setting the note now will make the note that value above or below the previous note.
* This is hidden by default and can be enabled from the settings menu

### Absolute Notes
Tap the **|N|** button next to the note-picker.
This is the default mode

## Add beats to the opus
Tap the label of the column where you want to insert a beat.
Then tap the insert beat (![](/manuals/pagan/svgs/insert_beat.svg)) button.
Hold it to specify how many new beats you want to insert.

## Remove beats from the opus
Tap the label of the column you want to remove.
Then tap the insert beat (![](/manuals/pagan/svgs/remove_beat.svg)) button.
Hold it to specify how many new beats you want to remove.

## Add Channels (instruments) to the opus
Pull the config drawer open by swiping from the left side of the screen.
Tap **Add Channel**.

## Remove Channels (instruments) from the opus
Pull the config drawer open by swiping from the left side of the screen.
Tap **X** on the channel you want to remove

## Quick Navigation
*If your opus is too long to manually swipe through*
Tap the playback (&#9654;) button in the top bar
Use the crub bar to select a beat
Tap the &#8618; button


# Concepts

## Channels and Lines
The Pagan Editor uses different "Channels" for each instrument. You can add or remove channels and change their instruments in the **config drawer**

Each Channel can have any number off "lines". Lines can be used to create chords or other counter-melodies. Lines can be added to a channel by **tapping any row label** of the channel you want to use and **tapping the insert-line button** (![](/manuals/pagan/svgs/insert_line.svg)) Long-press to insert multiple lines at once

If you want to create an opus more than 4 beats long, you'll want to **insert beats**. This can be done by **tapping the column label** of the column where you want to insert beats and **tapping the insert-button <icon> button**. Long-press to insert multiple beats at once


### Absolute and Relative Notes
Each note can be either absolute or relative. An absolute note (<icon>) is exactly what you would think it is. if you set a note to be 23, it will be understood as 23.
However a relative note is an offset from the last note. +03 will be 3 steps above the previous note and -10 will be an octave down.

### The Note Picker
The note picker is used to set a note's octave and offset. The top line is the octave. the bottom is the offset. Keep in mind this uses Radix-12 to denote a note. So if you are familar with western notation this translations (in 12-tone equal temper tuning) would be
- 0 -> A
- 1 -> A#
- 2 -> B
- 3 -> C
- 4 -> C#
- 5 -> D
- 6 -> D#
- 7 -> E
- 8 -> F
- 9 -> F#
- A -> G
- B -> G#

### Splitting
You can split a note/rest into any number of division such that all of the new sub-divisions will take the same amount of time to play as the initial, undivided note.
This can be done at any level to create rhythms (& polyrythms) more interesting that straight 1/4, 1/8, 1/16, 1/32 etc

### Inserting/Removing a note
a note/rest can be inserted or remove in the case that you accidentally split it's parent the wrong number of times or changed your mind about a rhythm. It's a quicked alternative than clearing the parent and resplitting

### Percussion
Instead of using the standard selector, each percussion instrument can only be mapped to a single line and each note is treated as either on or off.

### Linking Beats
Multiple beats can be linked together so that any changes applied to one will apply to all of them. Ranges can be linked as well to account for longer sections.
To link two beats, first double tap any leaf in a beat, then single tap another. the second beat will be overwritten and linked
to link a **range** of beats, first double tap 2 beats to act as corners of the range, then single tap the top-left corner of where you want to link.
to link an entire row repeatedly, start the same as you would to link a single beat or range, then tap the row-label. the row (or rows) will be overwritten with the beat (or range) selected

### The Config Menu
Here you can change the project name, tempo and transposition of your opus, as well as manage channels and their corresponding instruments. This is also where you can save, export, copy & trash your opus.


### Column Controls
By tapping any column's label, the column should be selected and 2 buttons should appear; the Insert and Remove Beat Buttons.  Tap these to extend or shorten your opus by a beat or tap and hold to specify how many beats to insert or remove.

### Row Controls
By tappping any row's label, the row should be selected and the insert/remove line button should be visible as well as the line volume control
If the row's channel is assigned to percussion, an extra drop-down menu will be visible. Each line in a percussion channel is assigned to a specific percussion instrument and this is how to change it.



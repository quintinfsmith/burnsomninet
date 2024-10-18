# Controls Overview
## The App

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/mainlayout.png",
        "entries": [
            [0.65, 0.04, "Start Playback. Tap again to stop. Also tap anywhere to stop"],
            [0.80, 0.04, "Undo last action. (max history size is 100 actions)"],
            [0.0, 0.06, "Quick Navigate"],
            [0.35, 0.06, "Select column and open up column menu"],
            [0.0, 0.20, "Select line and open up line menu. The numbers indicate the channel and the line. (eg, 0::4 means channel 0, line 4)"],
            [0.0, 0.36, "Select percussion line. the \"!\" denotes the line belongs to the percussion channel and the number is the drum assigned to the line."],
            [0.53, 0.13, "Select a note. Brings up note menu. Tap and hold to link, copy or move beats."],
            [0.0, 0.50, "Set the initial tempo."],
            [0.50, 0.50, "Set a tempo change."]
        ]
    }
}

## The Config Menu

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/configlayout.png",
        "entries": [
            [0.54, 0.00, "Set the song's name"],
            [0.20, 0.05, "Open The Tuning Table. This is where you can set the transposition and manually tweak the tuning."],
            [0.65, 0.05, "Add New Channels (Instruments) to the Song"],
            [0.21, 0.16, "Change Channel Instrument"],
            [0.64, 0.16, "Remove Channel"],
            [0.21, 0.265, "Set Drum"],
            [0.64, 0.265, "Toggle Drum visibility"],
            [0.10, 0.88, "Save the current project. Long press to \"save as\""],
            [0.28, 0.88, "Move to a copy of the current project"],
            [0.45, 0.88, "Delete the project"],
            [0.61, 0.88, "Export the project to .wav or .mid. Can only export to midi when Radix is 12."]
        ]
    }
}

## The Tuning Table

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/tuningtablelayout.png",
        "entries": [
            [0.35, 0.05, "Transpose the project by the given note. Maximum is the Radix - 1"],
            [0.65, 0.05, "Set the number of notes-per-octave to use in the project. Default is 12"],
            [0.4, 0.4, "Tune the notes using ratios rather than 'cents'. Default values are the pegged note values. In order to use cents, multiply the values by 100 then add the desired number of cents to the numerator"]
        ]
    }
}

## The Line Control Menu

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/linemenulayout.png",
        "entries": [
            [0.23, 0.88, "Control the line's volume"],
            [0.0, 0.79, "Set line's drum. (Exclusive to the Percussion Channel)"],
            [0.73, 0.78, "Remove a line from the channel. This button will *not* be visible when there is only 1 line in the given channel"],
            [0.90, 0.78, "Add a line to the channel (to add a channel see the Config Menu)"]
        ]
    }
}

## The Column Control Menu

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/columnmenulayout.png",
        "entries": [
            [0.73, 0.9, "Remove beats from the column. (Short tap for 1. Hold to input a number)"],
            [0.9, 0.9, "Add more beats to the column. (Short tap for 1. Hold to input a number)"]
        ]
    }
}

## The Note Control Menu

~SLUG{
    "slug": "NumberedDiagram",
    "class": "slug-NumberedDiagram",
    "data-json": {
        "img": "/content/manuals/pagan/imgs/1.5.9/cellmenulayout.png",
        "entries": [
            [0.00, 0.72, "Change to Relative/Absolute Note Input Mode. This can be toggled from the settings menu."],
            [0.14, 0.72, "Split a cell into finite divisions. (Hold to input a number)"],
            [0.30, 0.72, "Insert an empty cell after the currently selected one. (Hold to input a number)"],
            [0.48, 0.72, "Remove the selected cell. (Hold to remove all cell at the current level)"],
            [0.67, 0.72, "Unset a note."],
            [0.85, 0.72, "Set a note's duration (Hold to reset to x1)"],
            [0.3, 0.83, "Set a note's octave"],
            [0.6, 0.88, "Set a note's offset"]
        ]
    }
}



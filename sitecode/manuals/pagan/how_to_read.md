# Reading The Layout

## The Rhythm
Pagan is laid-out on a beat-by-beat basis, rather than by groups of beats (measures). So a time signature wouldn't really make sense to use here.

Each column represents a single beat, regardless of visual width.
So the equivalent of a quarter note or crotchet in 4/4, would be a column's width
The equivalent of, an eigth note or quaver in 4/4 time would be a column divided in 2
A triplet would be a column divided in 3 and so on

Rests are implicated by the lack of an active note in any given position.

These two images represent the same thing:
<img alt="Some random progression in Pagan" src="/content/manuals/pagan/imgs/1.5.9/measure_pagan.png" style="height: 6em;"/>
<img alt="The same progression in Musescore" src="/content/manuals/pagan/imgs/1.5.9/measure_musescore.png" style="height: 6em;"/>

## The Notes
Instead of using letters with sharps and flats, Pagan uses the <b>index</b> of the note in the octave.
<table>
    <tr>
        <th>00</th>
        <th>01</th>
        <th>02</th>
        <th>03</th>
        <th>04</th>
        <th>05</th>
        <th>06</th>
        <th>07</th>
        <th>08</th>
        <th>09</th>
        <th>10</th>
        <th>11</th>
    </tr>
    <tr>
        <td>A</td>
        <td>A#</td>
        <td>B</td>
        <td>C</td>
        <td>C#</td>
        <td>D</td>
        <td>D#</td>
        <td>E</td>
        <td>F</td>
        <td>F#</td>
        <td>G</td>
        <td>G#</td>
    </tr>
</table>

...and the octave is represented by the subscripted prefix.

<span style="font-size: 24px; text-decoration:bold;">
    <sub style="font-size:15px">octave</sub>Index
</span>


Octaves are counted starting at A (0) rather than C (3). So <b>A0 remains <sub>0</sub>0</b>, but the proceding <strong>C is not <sub>1</sub>C</strong>, but rather <span style="font-size:20px"><b><u><sub>0</sub>3</u></b></span>

So middle C (C4) would be written as <sub>3</sub>3

## The Instruments
On the left side of the Pagan interface, you'll notice labels that look something like 0::0 or 0!

<u>The lines written like <b>0::0</b> are <i><b>Pitched Instrument Lines</b></i></u>.
<div style="font-weight: 300; padding-left: 1em;">
    The first number indicates the <b>channel (or instrument)</b>.
    The second represents the line number of the instrument
    So the <b>first instrument</b>'s <b>second line</b> would look like <span style="font-size:20px"><b>0::1</b></span>
</div>

<style>
    .gm_perc_table { width: 100%; }
</style>

<u>The lines written as a number with an exclamation mark <b>(0!)</b> are <i><b>Percussion Lines</b></i></u>.

<div style="font-weight: 300; padding-left: 1em;">
    The numbers identify the percussion instruments being used. It varies based on the soundfont being used, but soundfonts that adhere to the <b>General MIDI Standard</b> will follow this table:
    <table class="gm_perc_table">
        <tr><td>08</td><td>Acoustic Bass Drum</td><td>09</td><td>Bass Drum 1</td><td>10</td><td>Side Stick</td></tr>
        <tr><td>11</td><td>Acoustic Snare</td><td>12</td><td>Hand Clap</td><td>13</td><td>Electric Snare</td><td>14</td><td>Low Floor Tom</td></tr>
        <tr><td>15</td><td>Closed Hi Hat</td><td>16</td><td>High Floor Tom</td><td>17</td><td>Pedal Hi-Hat</td><td>18</td><td>Low Tom</td></tr>
        <tr><td>19</td><td>Open Hi-Hat</td><td>20</td><td>Low-Mid Tom</td><td>21</td><td>Hi Mid Tom</td><td>22</td><td>Crash Cymbal 1</td></tr>
        <tr><td>23</td><td>High Tom</td><td>24</td><td>Ride Cymbal 1</td><td>25</td><td>Chinese Cymbal</td><td>26</td><td>Ride Bell</td></tr>
        <tr><td>27</td><td>Tambourine</td><td>28</td><td>Splash Cymbal</td><td>29</td><td>Cowbell</td><td>30</td><td>Crash Cymbal 2</td></tr>
        <tr><td>31</td><td>Vibraslap</td><td>32</td><td>Ride Cymbal 2</td><td>33</td><td>Hi Bongo</td><td>34</td><td>Low Bongo</td></tr>
        <tr><td>35</td><td>Mute Hi Conga</td><td>36</td><td>Open Hi Conga</td><td>37</td><td>Low Conga</td><td>38</td><td>High Timbale</td></tr>
        <tr><td>39</td><td>Low Timbale</td><td>40</td><td>High Agogo</td><td>41</td><td>Low Agogo</td><td>42</td><td>Cabasa</td></tr>
        <tr><td>43</td><td>Maracas</td><td>44</td><td>Short Whistle</td><td>45</td><td>Long Whistle</td><td>46</td><td>Short Guiro</td></tr>
        <tr><td>47</td><td>Long Guiro</td><td>48</td><td>Claves</td><td>49</td><td>Hi Wood Block</td><td>50</td><td>Low Wood Block</td></tr>
        <tr><td>51</td><td>Mute Cuica</td><td>52</td><td>Open Cuica</td><td>53</td><td>Mute Triangle</td><td>54</td><td>Open Triangle</td></tr>
    </table>
</div>




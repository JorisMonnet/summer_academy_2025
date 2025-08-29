# Composing with MIDI in Python

## Documentation

- [MIDI](https://midi.org/specs)
- [Mido](https://mido.readthedocs.io/en/latest/)

## MIDI Boilerplate

We give you basic data structures and midi functions to get you started with MIDI in Python.
We use the [Mido](https://mido.readthedocs.io/en/latest/) library to handle MIDI messages and files.
You are free to use another library if you prefer, as Music21, pretty_midi, or others.

### Mido Usage

We provide two examples to show you how to use the Mido library, one where you can [output](output_example.py) a melody
to a midi instrument,
and another one where you can get [input](input_example.py) midi messages from a midi controller.

### NoteList

On the other hand, we provide a more [complex example](src/complex_example/main.py) that uses custom data structures to
handle the midi messages more easily.
In this example, we use a `Note` class that represents a note with its pitch, velocity, and time.
This class is used to create a `NoteList` that contains several notes. This class has a wide range of methods to
manipulate the notes, such as adding, removing, and sorting them. Feel free to add any method you need to this class, or
create your own data structures to handle the MIDI messages.
Similar classes have been partially implemented for `ControlChange` messages, and you can extend them as needed.

### MidiControllers

Finally, we provide a MidiInputController and MidiOutputController to handle MIDI input and output ports. These classes
allow you to easily send and receive MIDI messages, and they can be extended to add more functionality as needed.
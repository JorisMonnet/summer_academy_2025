import time

import mido

from midi_boilerplate.src.data_structures.note import Note
from midi_boilerplate.src.data_structures.note_list import NoteList

if __name__ == "__main__":
    outputs = mido.get_output_names()
    print("MIDI Outputs:")
    for o in outputs:
        print(o)

    # Open the first available MIDI output, you can change the index if needed
    midi_output = mido.open_output(outputs[0])

    melody = NoteList([
        Note(60 + i, i * 0.5, 0.25, 100) for i in range(8)
    ])

    last_note_time = 0
    for note in melody:
        time.sleep(note.time - last_note_time)
        last_note_time = note.time
        midi_output.send(mido.Message('note_on', note=note.pitch, velocity=note.velocity))
        time.sleep(note.duration)
        midi_output.send(mido.Message('note_off', note=note.pitch, velocity=0))

    midi_output.close()

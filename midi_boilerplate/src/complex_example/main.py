import time

import mido

from midi_boilerplate.src.complex_example.midi_input_controller import MidiInputController
from midi_boilerplate.src.complex_example.midi_output_controller import MidiOutputController
from midi_boilerplate.src.data_structures.event_list import EventList
from midi_boilerplate.src.data_structures.note import Note
from midi_boilerplate.src.data_structures.note_list import NoteList


def transform_note_list(nl: NoteList, el: EventList) -> tuple[NoteList, EventList]:
    """
    Transforms the note list and event list.
    This is a placeholder for any transformation logic you want to apply. TODO: Implement your transformation logic.
    :param nl: A list of Note objects.
    :param el: A list of MidiEvent objects.
    :return: Transformed note_list and event_list.
    """
    # For now, we just return the input lists reversed.
    pitches = nl.get_pitches()
    pitches.reverse()
    new_nl = []
    for i in range(len(nl)):
        new_note = nl[i]
        new_note.pitch = pitches[i]
        new_nl.append(new_note)
    return NoteList(new_nl), el


if __name__ == "__main__":
    input_controller = MidiInputController()
    output_controller = MidiOutputController()

    input_port_names = mido.get_input_names()
    output_port_names = mido.get_output_names()

    if input_port_names:
        input_controller.set_ports([input_port_names[0]])  # You can set multiple ports if needed
    else:
        print("No MIDI input ports available.")
    if output_port_names:
        output_controller.set_port(output_port_names[0])
    else:
        print("No MIDI output ports available.")

    last_time = time.time()

    try:
        while True:
            current_time = time.time()
            if current_time - last_time > 1.0:  # Check every second
                last_time = current_time
                if input_controller.has_events():
                    note_list, event_list = input_controller.prepare_to_output()
                    transformed_note_list, transformed_event_list = transform_note_list(note_list, event_list)
                    output_controller.send(transformed_note_list, transformed_event_list)
                    input_controller.reset()
            time.sleep(0.2)  # Sleep to avoid busy waiting
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        input_controller.close()
        output_controller.close()
        print("MIDI controllers closed.")

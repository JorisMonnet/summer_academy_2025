import mido

from compositions.midi_boilerplate.src.data_structures.note import Note

inputs = mido.get_input_names()
outputs = mido.get_output_names()
print("MIDI Inputs:")
for i in inputs:
    print(i)
print("\nMIDI Outputs:")
for o in outputs:
    print(o)

midi_input = mido.open_input(inputs[0])  # Open the first available MIDI input, you can change the index if needed
midi_output = mido.open_output(outputs[0])  # Open the first available MIDI output, you can change the index if needed


def handle_message(message: mido.Message) -> None:
    """
    Echoes back the received MIDI message to the output port.
    :param message: The MIDI message received from the input port.
    :return: None
    """
    print(f"Received message: {message}")
    # Here you can process the message and send a response if needed
    # For example, sending the note back
    midi_output.send(message)


received_messages = {}


def handle_message_2(message: mido.Message) -> Note | None:
    """
    Creates a Note object from the received MIDI messages.
    :param message:
    :return:
    """
    global received_messages
    print(f"Received message: {message}", received_messages)
    if message.type == 'note_on' and message.velocity > 0:
        received_messages[message.note] = message.dict()
    elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):
        if message.note in received_messages:
            note_on_message = received_messages.pop(message.note)
            note = Note(midi_onset_msg=note_on_message, midi_offset_msg=message.dict())
            print(f"Processed Note: {note}")
            return note
    else:
        print(f"Unhandled message type: {message.type}")
    return None


midi_input.callback = handle_message_2

if __name__ == "__main__":
    try:
        print("Listening for MIDI messages...")
        while True:
            pass  # Keep the script running to listen for MIDI messages
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        midi_input.close()
        midi_output.close()
        print("Closed MIDI ports.")

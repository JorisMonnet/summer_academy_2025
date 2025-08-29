"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch


    IMPORTANT: This file contains internal midit functions and should be modified by midit developers only.
    Users of the midit library and authors of midit algorithms may poke in these internals at their own risk.
"""

from compositions.midi_boilerplate.src.data_structures.event_list import EventList
from compositions.midi_boilerplate.src.data_structures.note_list import NoteList, MAX_MIDI_PITCH, MIN_MIDI_PITCH
from compositions.midi_boilerplate.src.data_structures.pedal_event import SustainPedalEvent


def create_message_list_for_output(note_list: NoteList, event_list: EventList) -> list[dict]:
    """
    Creates a list of messages from a list of notes.
    This list will have the first message at time 0 and the rest of the messages will have the time relative to the
    previous message.
    :param note_list: A list of Note objects.
    :param event_list: A list of MidiEvent objects.
    :return: A list of mido.Message objects.
    """
    return prepare_message_list_for_output(create_message_list_with_absolute_times(note_list, event_list))


def prepare_message_list_for_output(message_list: list[dict]) -> list[dict]:
    """
    Prepares the message list for output.
    Message 0 will have time 0 and the rest of the messages will have a time relative to the previous message.
    :param message_list: A list of mido.Message objects.
    :return: A list of mido.Message objects.
    """
    message_list.sort(key=lambda m: m['time'], reverse=False)
    for i in range(len(message_list) - 1, 0, -1):
        message_list[i]['time'] = message_list[i]['time'] - message_list[i - 1]['time']
    return message_list


def create_message_list_with_absolute_times(note_list: NoteList, event_list: EventList) -> list[dict]:
    """
    Creates a list of messages from a list of notes. The offset times are absolute.
    :param note_list: A list of Note objects.
    :param event_list: A list of MidiEvent objects.
    :return: A list of mido.Message objects.
    """
    note_list = note_list.deep_copy()
    # Note-to-dict-to-mido conversion.
    note_list = note_list.deep_copy()
    message_list = []
    for note in note_list:
        if note.pitch > MAX_MIDI_PITCH or note.pitch < MIN_MIDI_PITCH:
            print(f'Note pitch {note.pitch} is out of range. Skipping note.')
            continue
        if note.onset_message['time'] < 0:
            print(f'Note onset time {note.time} is negative. Skipping note.')
            continue
        if note.duration <= 0:
            print(f'Note duration {note.duration} is negative. Skipping note.')
            continue
        if not isinstance(note.velocity, int):
            note.velocity = int(note.velocity)
        # Conversion of offset times from durations to absolute values.
        message_list.append(note.onset_message)
        message_list.append(note.offset_message)
    pedal_list = []
    for event in event_list:
        if isinstance(event, SustainPedalEvent):
            pedal_on, pedal_off = event.to_midi()
            pedal_list.append(pedal_on)
            pedal_list.append(pedal_off)
        else:
            continue

    message_list += pedal_list
    message_list.sort(key=lambda m: m['time'], reverse=False)  # Message list sort by absolute time.
    return message_list

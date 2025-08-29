"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
import logging

import mido
from mido.midifiles.midifiles import DEFAULT_TEMPO, DEFAULT_TICKS_PER_BEAT

from compositions.midi_boilerplate.src.data_structures.note import Note
from compositions.midi_boilerplate.src.data_structures.note_list import NoteList

log = logging.getLogger(__name__)


def midi_file_to_note_list(midi_file_path: str) -> NoteList:
    """
    Converts a MIDI file into a list of notes.

    :param midi_file_path: The MIDI file path to convert.
    :return: A list of notes.
    """
    note_list = NoteList()
    mido_file = mido.MidiFile(midi_file_path)
    for track in mido_file.tracks:
        note_state = [{}] * 127
        for message in track:
            message = message.dict()
            match message['type']:
                case 'note_on':
                    if note_state[message['note']] == {}:
                        message['time'] = mido.tick2second(message['time'], DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO)
                        note_state[message['note']] = message
                case 'note_off':
                    if note_state[message['note']] == {}:
                        log.warning("Note is already off! " + str(message))
                    else:
                        message['time'] = mido.tick2second(message['time'], DEFAULT_TICKS_PER_BEAT, DEFAULT_TEMPO)
                        new_note = Note(midi_onset_msg=note_state[message['note']], midi_offset_msg=message)
                        note_list.append(new_note)
                        note_state[message['note']] = {}
    note_list.sort(key=lambda n: n.time, reverse=False)
    return note_list


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Converts a MIDI file into a list of notes.')
    parser.add_argument('midi_file_path', type=str, help='The path of the MIDI file.')
    args = parser.parse_args()

    print(midi_file_to_note_list(args.midi_file_path))

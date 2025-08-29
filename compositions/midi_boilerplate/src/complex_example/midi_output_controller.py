"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
import threading
import time

import mido
from mido.messages import Message
from tabulate import tabulate

from compositions.midi_boilerplate.src.data_structures.event_list import EventList
from compositions.midi_boilerplate.src.data_structures.note_list import NoteList
from compositions.midi_boilerplate.src.utils.utilities import create_message_list_with_absolute_times, \
    prepare_message_list_for_output


def prepare_to_output(note_list: NoteList, event_list: EventList) -> list[Message]:
    """
    Prepare the output port for playback.
    :param note_list: A list of Note objects.
    :param event_list: A list of MidiEvent objects.
    """
    note_list.filter_erroneous_notes()

    if note_list.is_empty():
        print('No notes to play.')
    else:
        # Find the last note and stop all events after it.
        event_list.stop_events(note_list.get_end_time())

    event_list.filter_close_events()

    message_list = create_message_list_with_absolute_times(note_list, event_list)

    message_list = prepare_message_list_for_output(message_list)

    print(f'NoteList converted to messages and post-processed '
          f'(sorted, normalized, with time diffs):\n'
          f'{tabulate(message_list, headers="keys")}')

    return list(map(lambda m: mido.Message(**m), message_list))


class MidiOutputController:
    def __init__(self):
        self.output_port_name = None
        self.output_port = None
        self.output_port_lock = threading.Lock()
        self.first_output_time = None

    def set_port(self, output_port_name: str) -> bool:
        """
        Sets the output port.
        :param output_port_name: The name of the output port.
        :return: True if the port is set, False otherwise (port already changed by another thread).
        """
        if self.output_port_lock.acquire(timeout=60):
            self.output_port_name = output_port_name
            if self.output_port is not None:
                self.output_port.panic()
                self.output_port.send(mido.Message('control_change', control=64, value=0, time=0))
                self.output_port.close()

            # noinspection PyUnresolvedReferences
            if output_port_name is not None and output_port_name in mido.get_output_names():
                # noinspection PyUnresolvedReferences
                self.output_port = mido.open_output(output_port_name)
            else:
                print(f'Output port {output_port_name} not found.')
                self.output_port = None
                self.output_port_name = None
            self.output_port_lock.release()
            return True
        return False

    def close_abruptly(self) -> None:
        """
        Closes the output port abruptly.
        """
        if self.output_port is not None:
            self.output_port.panic()
            self.output_port.reset()
            # Put Pedals back up.
            self.output_port.send(mido.Message('control_change', control=64, value=0, time=0))

    def send(self, note_list: NoteList, event_list: EventList) -> None:
        """
        Send the midi output.
        :param note_list: A list of Note objects.
        :param event_list: A list of MidiEvent objects.
        """
        if self.output_port is None:
            print('Output port is not set.')
            return
        if self.first_output_time is None:
            self.first_output_time = time.time()

        message_list = prepare_to_output(note_list, event_list)
        # mido message playback.
        print(f'Sending {len(message_list)} messages to output device.')
        for message in message_list:
            time.sleep(message.time)
            try:
                self.output_port.send(message)
            except:
                print("MIDO Error: ")
                print(message)
                print(self.output_port)

    def close(self) -> None:
        """
        Resets the output port.
        """
        if self.output_port is not None:
            self.output_port.reset()

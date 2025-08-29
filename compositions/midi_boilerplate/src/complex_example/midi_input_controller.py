"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
import copy
import time

import mido

from compositions.midi_boilerplate.src.data_structures.event_list import EventList
from compositions.midi_boilerplate.src.data_structures.note import Note
from compositions.midi_boilerplate.src.data_structures.note_list import NoteList, MAX_MIDI_PITCH


class MidiInputController:
    """
    A class handling all the Midi events coming from the input devices.
    """

    def __init__(self):
        self.ports = None
        self.port_names = []
        self.event_list = EventList()
        self.note_list = NoteList()
        self.note_state = [{}] * MAX_MIDI_PITCH
        self.ultimate_time = time.time()
        self.first_input_time = None
        self.note_on_off_balance = 0

    def handle_message_with_error(self, message: mido.Message) -> None:
        """
        Handles a message from the input device.
        :param message: The mido message to handle.
        :return: None
        :raises Exception: If the message is not handled properly.
        """
        try:
            self.handle_message(message)
        except Exception as e:
            print(f"Error while handling message: {e}")

    def handle_message(self, message: mido.Message) -> None:
        """
        Handles a message from the input device.
        :param message: The mido message to handle.
        :return: None
        """
        message = message.dict()
        if not self.first_input_time:
            self.first_input_time = time.time()
        # Message timing information.
        self.ultimate_time = time.time()
        message["time"] = self.ultimate_time - self.first_input_time
        # Handle the message depending on its type.
        if message['type'] == 'note_on' and message['velocity'] > 0:
            self.handle_note_on(message)
        elif message['type'] == 'note_off':
            self.handle_note_off(message)
        elif message['type'] == 'note_on' and message['velocity'] == 0:
            if 'velocity' not in self.note_state[message['note']]:
                print('\tNote is already off! ' + str(message))
            else:
                message['type'] = 'note_off'
                message['velocity'] = self.note_state[message['note']]['velocity']
                self.handle_note_off(message)
        elif message['type'] in ['control_change', 'program_change', 'aftertouch', 'pitchwheel', 'polytouch']:
            _ = self.event_list.add_midi_message(message)
        else:
            print(f'\tUnrecognized message type: {message["type"]} for message {message}.')

    def handle_note_on(self, message: dict) -> None:
        """
        Handles a note_on message from the input device.
        :param message: The note_on message to handle.
        :return: None
        """
        if self.note_state[message['note']] == {}:
            self.note_state[message['note']] = message
            self.note_on_off_balance += 1  # MIDI silence bookkeeping.
        else:
            print('\tNote is already on! ' + str(message))

    def handle_note_off(self, message: dict) -> None:
        """
        Handles a note_off message from the input device.
        :param message: The note_off message to handle.
        :return: None
        """
        if self.note_state[message['note']] == 0:
            print('\tNote is already off! ' + str(message))
        else:
            # Fail silently if there is a note_off before a note_on
            if 'time' not in self.note_state[message['note']]:
                print('\tNote is off before on! ' + str(message))
                self.note_state[message['note']] = {}
            else:
                new_note = Note(midi_onset_msg=self.note_state[message['note']], midi_offset_msg=message)
                self.note_list.append(new_note)
                self.note_state[message['note']] = {}
                self.note_on_off_balance -= 1  # MIDI silence bookkeeping.

    def reset(self) -> None:
        """
        Resets the members of the input handler.
        :return: None
        """
        self.note_list = NoteList()
        self.event_list = EventList()
        self.note_state = [{}] * MAX_MIDI_PITCH

    def prepare_to_output(self) -> NoteList and EventList:
        """
        Sets the input times of the note_list and sorts it.
        :return: None
        """
        if self.note_on_off_balance != 0:
            for i in range(MAX_MIDI_PITCH):
                if self.note_state[i] != {}:
                    self.handle_note_off({'type': 'note_off', 'note': i, 'velocity': 0,
                                          'time': self.ultimate_time - self.first_input_time})

        self.note_list.sort(key=lambda n: n.time, reverse=False)
        self.note_list.set_beginning_to_zero()
        return self.note_list.deep_copy(), copy.deepcopy(self.event_list)

    def set_ports(self, port_names: list[str]) -> None:
        """
        Initializes the input ports.
        :param port_names: The name of the ports to initialize.
        """
        if port_names is None or len(port_names) == 0:
            print('No input port selected.')
            return
        if self.ports is not None:
            for port in self.ports:
                port.close()
        self.ports = []
        self.port_names = port_names
        for i in range(len(self.port_names)):
            if self.port_names[i] is not None:
                self.ports.append(mido.open_input(self.port_names[i], callback=self.handle_message_with_error))
        print(f'Accepting MIDI messages...\nInput ports:{self.ports}')

    def close(self) -> None:
        """
        Closes the input port.
        :return: None
        """
        if self.ports is not None:
            for port in self.ports:
                port.close()
        self.port_names = None
        print('Input port closed.')

    def has_events(self) -> bool:
        """
        Returns True if the event list is not empty.
        :return: True if the event list is not empty.
        """
        return not self.note_list.is_empty() or not self.event_list.is_empty()

"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
from midi_boilerplate.src.data_structures.midi_event import MidiEvent
from midi_boilerplate.src.data_structures.type_aliases import TimeType


class ControlChangeEvent(MidiEvent):
    """
    A class used to represent a control change event (MIDI).
    """

    def __init__(self, time: TimeType, duration: TimeType, channel: int, control: int, value: int):
        super().__init__(time, duration, channel)
        self.control = control
        self.value = value

    def to_midi_on(self) -> dict:
        """
        Returns the midi message corresponding to the control change event start.
        """
        return {
            'type': 'control_change',
            'time': self.time,
            'control': self.control,
            'value': self.value,
            'channel': self.channel
        }

    def to_midi_off(self) -> dict:
        """
        Returns 'off' midi message. It means a control change message with value 0 after the duration of the event.
        """
        return {
            'type': 'control_change',
            'time': self.offset,
            'control': self.control,
            'value': 0,
            'channel': self.channel
        }

    def to_midi(self) -> tuple[dict, dict]:
        """
        Returns a tuple of midi messages (on, off) as dictionaries
        """
        return self.to_midi_on(), self.to_midi_off()

    def to_midi_list(self) -> tuple[tuple[float, list[int]], tuple[float, list[int]]]:
        """
        return the on and off message as a list where each message is the tuple (time, (type, control, value))
        """
        return ((float(self.time), [0xb0 + self.channel, self.control, self.value]),
                (float(self.offset), [0xb0 + self.channel, self.control, 0]))

    def to_midi_list_on(self) -> list[int]:
        """
        return the on message as a list where each message is the tuple (time, (type, control, value))
        """
        return [float(self.time), 0xb0 + self.channel, self.control, self.value]

    def to_midi_list_off(self) -> list[int]:
        """
        return the off message as a list where each message is the tuple (time, (type, control, value))
        """
        return [float(self.offset), 0xb0 + self.channel, self.control, 0]

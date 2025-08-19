"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
from midi_boilerplate.src.data_structures.control_change_event import ControlChangeEvent
from midi_boilerplate.src.data_structures.type_aliases import TimeType


class SustainPedalEvent(ControlChangeEvent):
    """
    A class used to represent a sustain pedal event (MIDI).
    Currently, the pedal event is represented by a control change event with control 64 (sustain pedal).
    """

    def __init__(self, time: TimeType, duration: TimeType, channel: int, value: int):
        super().__init__(time, duration, channel, 64, value)

    def __str__(self) -> str:
        return (f'SustainPedalEvent: tick={self.time}, channel={self.channel}, '
                f'control={self.control}, value={self.value}')

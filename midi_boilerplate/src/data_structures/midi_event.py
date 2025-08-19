"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
from midi_boilerplate.src.data_structures.type_aliases import TimeType


class MidiEvent:
    """
    A class used to represent a MIDI event.
    self.time: The time of the event.
    self.duration: The duration of the event.
    self.channel: The channel of the event.
    """

    def __init__(self, time: TimeType, duration: TimeType, channel: int):
        self.time = time if time >= 0 else 0.  # time must be positive
        self.duration = duration if duration >= 0 else 0.  # duration must be positive
        self.channel = channel if 0 <= channel < 16 else 0  # MIDI channels are 0-15

    @property
    def offset(self) -> TimeType:
        """
        Returns the offset of the event (time + duration or onset + duration).
        """
        return self.time + self.duration

    @property
    def onset(self) -> TimeType:
        """
        Returns the onset of the event.
        """
        return self.time

    @onset.setter
    def onset(self, onset) -> None:
        if isinstance(onset, TimeType):
            self.time = onset
        else:
            raise ValueError("Onset must be a number.")

    @offset.setter
    def offset(self, offset) -> None:
        if isinstance(offset, TimeType):
            self.duration = offset - self.time
        else:
            raise ValueError("Offset must be a number.")

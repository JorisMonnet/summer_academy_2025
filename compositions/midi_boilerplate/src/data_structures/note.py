"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch


    IMPORTANT: This file contains internal midit functions and should be modified by midit developers only.
    Users of the midit library and authors of midit algorithms may poke in these internals at their own risk.
"""
import json
from numbers import Number

from compositions.midi_boilerplate.src.data_structures.type_aliases import TimeType


class Note:
    def __init__(self, pitch: int = None, time: TimeType = None, duration: TimeType = None, velocity: int = None,
                 channel: int = 0, midi_onset_msg: dict = None, midi_offset_msg: dict = None, custom: dict = None):
        """
        Initializes a Note object.
        either with 2 MIDI messages as dict or with pitch, time, duration, velocity and channel.
        :param pitch: the pitch of the note
        :param time: the onset of the note
        :param duration: the duration of the note
        :param velocity: the velocity of the note
        :param channel: the channel of the note
        :param midi_onset_msg: the MIDI onset message as a dict
        :param midi_offset_msg: the MIDI offset message as a dict
        :param custom: a dictionary of custom data
        """
        if midi_onset_msg is not None and midi_offset_msg is not None and isinstance(midi_onset_msg, dict) and \
                isinstance(midi_offset_msg, dict):
            if 'note' not in midi_onset_msg or 'time' not in midi_onset_msg or 'velocity' not in midi_onset_msg:
                raise ValueError("Onset message must contain note, time and velocity fields.")
            if 'note' not in midi_offset_msg or 'time' not in midi_offset_msg:
                raise ValueError("Offset message must contain note and time fields.")
            if midi_onset_msg['note'] != midi_offset_msg['note']:
                raise ValueError("Onset and offset messages must have the same pitch.")
            self._pitch = midi_onset_msg['note']
            self._time = midi_onset_msg['time']
            self._duration = midi_offset_msg['time'] - midi_onset_msg['time']
            self._velocity = midi_onset_msg['velocity']
            self._channel = midi_onset_msg['channel'] if 'channel' in midi_onset_msg else channel
        elif (pitch is not None and time is not None and duration is not None
              and velocity is not None and channel is not None):
            self._pitch = pitch
            self._time = time
            self._duration = duration
            self._velocity = velocity
            self._channel = channel
        else:
            raise ValueError("Note must be initialized with either MIDI messages or pitch, time, duration, velocity "
                             "and channel.")
        self._custom = custom if custom is not None else {}

    @property
    def onset_message(self) -> dict:
        return {
            'type': 'note_on',
            'note': self._pitch,
            'time': self._time,
            'velocity': self._velocity,
            'channel': self._channel
        }

    @property
    def offset_message(self) -> dict:
        return {
            'type': 'note_off',
            'note': self._pitch,
            'time': self._time + self._duration,
            'velocity': 0,
            'channel': self._channel
        }

    def note_on_list_message_with_time(self) -> list[int]:
        return [self._time, 0x90 | self._channel, self._pitch, self._velocity]

    def note_off_list_message_with_time(self) -> list[int]:
        return [self._time + self._duration, 0x80 | self._channel, self._pitch, 0]

    @property
    def pitch(self) -> int:
        return self._pitch

    @property
    def time(self) -> TimeType:
        return self._time

    @property
    def duration(self) -> TimeType:
        return self._duration

    @property
    def velocity(self) -> int:
        return self._velocity

    @property
    def channel(self) -> int:
        return self._channel

    @property
    def description(self) -> dict:
        return {
            'pitch': self._pitch,
            'time': self._time,
            'duration': self._duration,
            'velocity': self._velocity,
            'channel': self._channel
        }

    @property
    def custom(self) -> dict:
        return self._custom

    @property
    def pc(self) -> int:
        return self.get_pitch_class()

    @pitch.setter
    def pitch(self, value):
        if not isinstance(value, int):
            value = int(value)
        if 0 <= value <= 127:
            self._pitch = value

    @time.setter
    def time(self, value):
        if not isinstance(value, Number):
            value = float(value)
        if value < 0:
            # Margin of error for negative time values.
            if value >= -0.1:
                value = 0
            else:
                value = 0
        self._time = value

    @duration.setter
    def duration(self, value):
        if not isinstance(value, Number):
            value = float(value)
        if value > 0:
            self._duration = value
        else:
            self._duration = 0.1  # 1ms duration as a fallback for non-positive parameter values.

    @property
    def offset(self) -> TimeType:
        return self._time + self._duration

    @property
    def onset(self) -> TimeType:
        return self._time

    @onset.setter
    def onset(self, value):
        self.time = value

    @velocity.setter
    def velocity(self, value):
        if not isinstance(value, int):
            value = int(value)
        if 0 <= value <= 127:
            self._velocity = value
        else:
            raise ValueError("Note velocity must be an integer between 0 and 127.")

    @channel.setter
    def channel(self, value):
        if not isinstance(value, int):
            value = int(value)
        if 0 <= value <= 15:
            self._channel = value
        else:
            raise ValueError("Note channel must be an integer between 0 and 15.")

    @custom.setter
    def custom(self, value):
        if not isinstance(value, dict):
            raise ValueError("Custom note data must be a dictionary.")
        self._custom = value

    def __str__(self) -> str:
        return str(self.description)

    def __repr__(self) -> str:
        return f"{self.pitch}({self.time}, {self.duration})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Note):
            return False
        if self.description == other.description:
            return True
        elif self.pitch == other.pitch and self.duration == other.duration and \
                self.velocity == other.velocity and self.channel == other.channel:
            return abs(self.time - other.time) < 0.0001

    def __hash__(self) -> int:
        return hash(str(self))

    def __copy__(self) -> 'Note':
        return Note(self.pitch, self.time, self.duration, self.velocity, self.channel)

    def get_pitch_class(self) -> int:
        """
        Gets the pitch class of the note. (pitch % 12)
        :return: the pitch class of the note.
        """
        return self.pitch % 12

    def transpose(self, interval: int) -> None:
        """
        Transposes the note by a given interval.
        :param interval: The interval to transpose by.
        :return: None
        """
        self.pitch += interval

    def shift_time(self, shift: float) -> None:
        """
        Shifts the note time.
        :param shift: The shift amount (can be negative).
        :return: None
        """
        if self.time + shift < 0:
            # Margin of error for negative time values.
            if self.time + shift >= -0.1:
                self.time = 0.
            else:
                self.time = 0.
        else:
            self.time += shift

    def is_held_into_segment(self, start: TimeType, end: TimeType) -> bool:
        """
        Checks if a note is held into a segment.
        :param start: the beginning of the segment
        :param end: the ending of the segment
        :return: True if the note is held into the segment, False otherwise
        """
        diff = 0
        if start > end:
            start, end = end, start
        elif start == end:
            return self.time <= start <= self.offset
        if self.time < start < self.offset < end:
            diff = self.offset - start
        elif start < self.time < end < self.offset:
            diff = end - self.time
        elif self.time < start < end < self.offset:
            return True
        elif start < self.time < self.offset < end:
            diff = self.offset - self.time
        return diff / (end - start) > 0.8

    def is_simultaneous(self, reference_note: 'Note') -> bool:
        """
        Checks if the note is simultaneous to a reference note.
        :param reference_note: the reference note
        :return: True if the note is simultaneous to the reference note, False otherwise
        """
        return self.time <= reference_note.time and self.offset >= reference_note.offset

    def to_dict(self) -> dict:
        """
        Return Note as a dictionary
        :return: the Note as a dictionary
        """
        if self.custom is not None and self.custom != {}:
            return {'pitch': self.pitch, 'time': self.time,
                    'duration': self.duration, 'velocity': self.velocity,
                    'channel': self.channel, 'custom': self.custom}
        return {'pitch': self.pitch, 'time': self.time, 'duration': self.duration,
                'velocity': self.velocity, 'channel': self.channel}

    def to_json(self) -> str:
        """
        Return Note as a JSON string
        :return: the Note as a JSON string
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_note: dict) -> 'Note':
        return cls(pitch=int(json_note['pitch']), time=float(json_note['time']),
                   duration=float(json_note['duration']), velocity=int(json_note['velocity']),
                   channel=int(json_note['channel']), custom=json_note['custom'] if 'custom' in json_note else None)

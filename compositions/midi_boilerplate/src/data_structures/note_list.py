"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""

import copy
import json
from math import ceil
from typing import Union, SupportsIndex, Callable, Tuple

from tabulate import tabulate

from compositions.midi_boilerplate.src.data_structures.note import Note
from compositions.midi_boilerplate.src.data_structures.type_aliases import TimeType

MIN_MIDI_PITCH = 0
MAX_MIDI_PITCH = 127
MAX_MIDI_VALUE = 127
SAFE_MODE = False
colors_map = {  # Use ANSI escape codes for colors
    0: "\033[0;31;40m",  # Red -> C
    1: "\033[1;31;40m",  # Red Bold -> C#/Db
    2: "\033[0;32;40m",  # Green -> D
    3: "\033[1;32;40m",  # Green Bold -> D#/Eb
    4: "\033[0;33;40m",  # Yellow -> E
    5: "\033[0;34;40m",  # Blue -> F
    6: "\033[1;34;40m",  # Blue Bold -> F#/Gb
    7: "\033[0;35;40m",  # Magenta -> G
    8: "\033[1;35;40m",  # Magenta Bold -> G#/Ab
    9: "\033[0;36;40m",  # Cyan -> A
    10: "\033[1;36;40m",  # Cyan Bold -> A#/Bb
    11: "\033[0;37;40m",  # White -> B
}


class NoteList(list[Note]):
    def __init__(self, args=None):
        super().__init__(args if args is not None else [])

    def add(self, note: Note) -> None:
        """
        Adds a note to the note list.
        :param note: The note to add.
        """
        if isinstance(note, Note):
            super().append(note)
        else:
            raise TypeError("Can only add Note objects to a NoteList.")

    def get(self, index: SupportsIndex) -> Note:
        return super().__getitem__(index)

    def duration(self) -> float:
        """
        Returns the duration of the note list.
        """
        if len(self) == 0:
            return 0
        return self.get_end_time() - self.get_start_time()

    def __len__(self) -> int:
        return super().__len__()

    def __iter__(self) -> iter:
        return super().__iter__()

    def __str__(self) -> str:
        return tabulate_notes(self)

    def __repr__(self) -> str:
        return str(super())

    def __getitem__(self, key: SupportsIndex) -> Union[Note, 'NoteList']:
        if isinstance(key, slice):
            return NoteList(super().__getitem__(key))
        return super().__getitem__(key)

    def __setitem__(self, key: SupportsIndex, value: Note) -> None:
        super().__setitem__(key, value)

    def __delitem__(self, key: SupportsIndex) -> None:
        super().__delitem__(key)

    def __contains__(self, item) -> bool:
        return super().__contains__(item)

    def __add__(self, other) -> 'NoteList':
        if isinstance(other, Note):
            self.append(other)
        elif isinstance(other, NoteList):
            self.extend(other)
        return self

    def __sub__(self, other) -> 'NoteList':
        if isinstance(other, Note):
            self.remove(other)
            return self
        elif isinstance(other, NoteList):
            other = set(other)
            return NoteList(n for n in self if n not in other)
        elif isinstance(other, list) or isinstance(other, tuple) or isinstance(other, set):
            if all(isinstance(n, Note) for n in other):
                other = set(other)
                return NoteList(n for n in self if n not in other)
            else:
                raise TypeError("Can't subtract by non-Note or non-NoteList type.")
        else:
            raise TypeError("Can't subtract by non-Note or non-NoteList type.")

    def __iadd__(self, other) -> 'NoteList':
        self.extend(other)
        return self

    def __mul__(self, other) -> 'NoteList':
        return super() * other

    def __imul__(self, other) -> 'NoteList':
        if isinstance(other, int):
            self.extend(self * (other - 1))
        else:
            raise TypeError("Can't multiply by non-integer type.")
        return self

    def __rmul__(self, other) -> 'NoteList':
        return super() * other

    def __eq__(self, other) -> bool:
        if not isinstance(other, NoteList):
            if isinstance(other, list) or isinstance(other, tuple) or isinstance(other, set):
                if all(isinstance(n, Note) for n in other):
                    other = NoteList(other)
                else:
                    return False
            else:
                return False
        if len(self) != len(other):
            return False
        self.sort(key=lambda n: n.time, reverse=False)
        other.sort(key=lambda n: n.time, reverse=False)
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __copy__(self) -> 'NoteList':
        return self.deep_copy()

    def append(self, new_note: Note) -> None:
        super().append(new_note)

    def extend(self, new_note_list: Union['NoteList', list[Note]]) -> None:
        if isinstance(new_note_list, NoteList):
            super().extend(new_note_list)
        elif isinstance(new_note_list, list):
            if all(isinstance(n, Note) for n in new_note_list):
                super().extend(new_note_list)
            else:
                raise TypeError("Can only extend by a list of Note objects.")
        else:
            raise TypeError("Can only extend by a NoteList or a list of Note objects.")

    def concatenate(self, new_note_list: 'NoteList') -> None:
        super().extend(new_note_list)

    def insert(self, index: SupportsIndex, new_note: Note) -> None:
        super().insert(index, new_note)

    def remove(self, note: Note) -> None:
        super().remove(note)

    def pop(self, index: SupportsIndex = -1) -> Note:
        return super().pop(index)

    def clear(self) -> None:
        super().clear()

    def is_empty(self) -> bool:
        """
        Returns whether the note list is empty or not.
        """
        return len(self) == 0

    def copy(self) -> 'NoteList':
        return NoteList(super().copy())

    def sort(self, key=lambda n: n.time, reverse=False) -> 'NoteList':
        super().sort(key=key, reverse=reverse)
        return self

    def reverse(self) -> None:
        super().reverse()

    def index(self, note: Note = None, start: SupportsIndex = None, end: SupportsIndex = None) -> int:
        return super().index(note)

    def count(self, note: Note) -> int:
        return super().count(note)

    def overlay(self, note_list: 'NoteList') -> None:
        """
        Overlays a note list on top of the current.
        :param note_list: The note list to overlay.
        :return: None
        """
        self.extend(note_list)

    def append_chronologically(self, note_list: 'NoteList') -> None:
        """
        Appends a note list chronologically to the current.
        :param note_list: The note list to append.
        :return: None
        """
        if len(self) == 0:
            self.extend(note_list)
        else:
            last_timestamp = self.get_end_time()
            note_list.shift_time(last_timestamp)
            self.extend(note_list)

    def prepend_chronologically(self, note_list: 'NoteList') -> None:
        """
        Prepends a note list chronologically to the current.
        :param note_list: The note list to prepend.
        :return: None
        """
        if len(self) == 0:
            self.extend(note_list)
        else:
            last_timestamp = note_list.get_end_time()
            self.shift_time(last_timestamp)
            self.extend(note_list)

    def get_ambitus_values(self) -> tuple:
        """
        Returns the ambitus of the note list.
        :return: A tuple containing the lowest and highest pitches.
        """
        pitches = self.get_pitches()
        if not pitches:
            return 0, 0
        return min(pitches), max(pitches)

    def get_ambitus_difference(self) -> int:
        """
        Returns the ambitus difference of the note list.
        :return: The difference between the highest and lowest pitches.
        """
        ambitus = self.get_ambitus_values()
        return ambitus[1] - ambitus[0]

    def get_pitches(self) -> list[int]:
        """
        Returns the pitches of the note list.
        """
        return [n.pitch for n in self]

    def get_pitch_class_set(self) -> set[int]:
        """
        Returns the pitch classes of the note list.
        """
        return set([n.get_pitch_class() for n in self])

    def density(self) -> float:
        """
        Returns the density of the note list.
        with the formula : number of notes / duration
        if the duration is 0, the density is 0
        """
        if self.duration() == 0:
            return 0
        return len(self) / self.duration()

    def filter_erroneous_notes(self) -> None:
        """
        Filters out if 2 notes are exactly the same,
        i.e. they have the same pitch, time, duration, velocity and channel.

        Remove notes with pitch out of the MIDI range.

        Complexity: O(n) where n is the number of notes.
        explanation of the complexity : O(n) for set() and O(n) for list(set())
        :return: None
        """
        if SAFE_MODE:
            new_list = NoteList(n for n in set(self) if n.pitch in range(MIN_MIDI_PITCH, MAX_MIDI_PITCH + 1) and
                                n.duration >= 0 and n.time >= 0 and n.velocity in range(MAX_MIDI_VALUE + 1))
            if len(new_list) != len(self):
                self.clear()
                self.extend(new_list)

    def print_notes(self) -> None:
        """
        Print the notes in the note list with colors in the terminal.
        (The colors are defined in the constants.py file.)
        Same notes at different octaves have the same color.
        :return: None
        """
        if len(self) == 0:
            print("NoteList is empty.")
            return
        for note in self:
            color = colors_map[note.get_pitch_class()]
            print(color + str(note))
        print("\033[0m")  # Reset color to default.

    def deep_copy(self):
        """
        Returns a deep copy of the note list.
        :return: A deep copy of the note list.
        """
        return NoteList(copy.deepcopy(n) for n in self)

    def before_time(self, timestamp) -> 'NoteList':
        """
        Returns the events that are before the given timestamp.
        :param timestamp: The timestamp to compare with.
        :return: The events that are before the given timestamp in a new EventList.
        """
        return NoteList(event for event in self if event.time < timestamp)

    def after_time(self, timestamp) -> 'NoteList':
        """
        Returns the events that are after the given timestamp.
        :param timestamp: The timestamp to compare with.
        :return: The events that are after the given timestamp in a new EventList.
        """
        return NoteList(event for event in self if event.time > timestamp)

    def transpose(self, interval: int) -> None:
        """
        Transpose all the notes in the note list by a given interval.
        :param interval: The interval to transpose by.
        :return: None
        """
        if interval == 0:
            return
        self.map(lambda n: n.transpose(interval))

    def map(self, f: Callable) -> 'NoteList':
        """
        Apply a function to all notes in the note list.
        :param f: The function to apply.
        :return: The note list with the function applied.
        """
        if len(self) == 0:
            return self
        if not callable(f):
            raise TypeError("The function must be callable.")
        # Check if f return Note
        if isinstance(f(self[0]), Note):
            for i in range(len(self)):
                self[i] = f(self[i])
        else:
            for i in range(1, len(self)):
                f(self[i])
        return self

    def filter(self, f: Callable) -> 'NoteList':
        """
        Filter the notes in the note list.
        :param f: The function to filter by.
        :return: A new NoteList containing the filtered notes.
        :raises TypeError: If the function is not callable.
        """
        if not callable(f):
            raise TypeError("The function must be callable.")
        return NoteList([n for n in self if f(n)])

    def shift_time(self, shift: float) -> None:
        """
        Shift the time of all notes in the note list.
        :param shift: The time to shift by.
        :return: None
        """
        self.filter_erroneous_notes()
        self.map(lambda n: n.shift_time(shift))

    def set_beginning(self, time: float) -> None:
        """
        Set the time of the start of the note list to a given time.
        :param time: The time to set.
        :return: None
        """
        if len(self) == 0:
            return
        self.shift_time(time - self.get_start_time())

    def set_beginning_to_zero(self) -> None:
        """
        Set the time of the start of the note list to zero.
        :return: None
        """
        self.set_beginning(0)

    def get_segment_span(self) -> tuple:
        """
        Get the span of the segment.
        :return: A tuple containing the start and duration of the segment.
        """
        if len(self) == 0:
            return 0, 0
        return self.get_start_time(), self.duration()

    def get_start_time(self) -> float:
        """
        Get the minimum time of the note list.
        return 0 if the note list is empty
        :return: The minimum time of the note list.
        """
        if len(self) == 0:
            return 0
        return min([n.time for n in self])

    def get_end_time(self) -> float:
        """
        Get the last timestamp (time+duration) of the note list.
        return 0 if the note list is empty
        :return: The maximum time of the note list.
        """
        if len(self) == 0:
            return 0
        return max([n.offset for n in self])

    def transform(self, interval: int = 0, speed_factor: float = 1, velocity_factor: float = 1) -> None:
        """
        Transforms the note list.
        :param interval: The interval to transpose by.
        :param speed_factor: The speed factor.
        :param velocity_factor: The velocity factor.
        :return: None
        """
        if len(self) == 0:
            return
        if speed_factor == 1 and velocity_factor == 1:
            self.transpose(interval)
            return
        start = self.get_start_time()
        self.set_beginning_to_zero()
        for n in self:
            n.transpose(interval)
            n.time *= speed_factor
            n.duration *= speed_factor
            n.velocity *= velocity_factor
        self.set_beginning(start)

    def get_simultaneous_notes(self, time: float) -> 'NoteList':
        """
        Get the notes that are playing at a given time.
        :param time: The time to check.
        :return: The notes that are playing at the given time.
        """
        return NoteList([n for n in self if n.time <= time < n.offset])

    def create_slice(self, start: TimeType, end: TimeType) -> 'NoteList':
        """
        Create a slice of the note list. The slice is defined by a start and end time.
        :param start: The start time of the slice.
        :param end: The end time of the slice.
        :return: A new NoteList containing the slice.
        """
        return NoteList([n for n in self if start <= n.time <= end or n.time <= start <= n.offset])

    def get_salami(self, slice_size: int | float) -> list['NoteList']:
        """
        Get a list of slices of the note list.
        :param slice_size: The size of the slices.
        :return: A list of NoteList.
        """
        return [self.create_slice(i * slice_size, (i + 1) * slice_size) for i in
                range(ceil(self.duration() / slice_size))]

    def get_max_silence_and_groups(self) -> Tuple[float, tuple['NoteList', 'NoteList']]:
        """
        Get the maximum silence between notes inside the note list and return the two groups around it.
        if no silence is found, return 0 and the note list itself in the index 0 of the tuple.
        :return: The maximum silence between notes and the two groups around it as a tuple
        """
        if len(self) == 0:
            return 0, (self, NoteList())
        silence = 0.
        silence_index = -1
        self.sort()
        for i in range(len(self) - 1):
            cur_silence = self[i + 1].time - self[i].offset
            if cur_silence > silence:
                silence = cur_silence
                silence_index = i

        if silence_index != -1:
            return silence, (self[:silence_index + 1], self[silence_index + 1:])
        return silence, (self, NoteList())

    def compress_velocity(self, maximum: int, minimum: int = 0) -> None:
        """
        Compress the velocity of the notes in the note list inside a given range.
        In place operation.
        :param maximum: The maximum velocity.
        :param minimum: The minimum velocity (default is 0).
        :return: None
        """
        velocity_constant = (maximum - minimum) / MAX_MIDI_VALUE
        for n in self:
            new_velocity = int(n.velocity * velocity_constant) + minimum
            n.velocity = new_velocity

    def to_json(self) -> str:
        """
        Convert the note list to a json string.
        :return: A json string.
        """
        return json.dumps([n.to_json() for n in self])

    def save_as_json(self, path: str) -> None:
        """
        Save the note list to a file as json
        :param path: The path to save the note list to.
        :return: None
        """
        with open(path, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def from_json(cls, json_data: str) -> 'NoteList':
        """
        Create a note list from a json string.
        :param json_data: The json string
        :return a NoteList object
        """
        return NoteList([Note.from_json(json.loads(n)) for n in json.loads(json_data)])

    @classmethod
    def from_file(cls, path: str) -> 'NoteList':
        """
        Parse a Note List from a file
        :param path: The path to the file
        :return: A NoteList object
        """
        with open(path, 'r') as f:
            return cls.from_json(f.read())


def tabulate_notes(note_list: NoteList) -> str:
    """
    Tabulate a list of notes.
    :param note_list: A list of Note objects.
    :return: A string containing the tabulated notes.
    """
    return tabulate(list(map(lambda n: n.description, note_list)), headers='keys')

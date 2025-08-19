"""
    Summer Academy 2025
    (c) 2025, EPFL DCML

    
    joris.monnet@epfl.ch

"""
from midi_boilerplate.src.data_structures.midi_event import MidiEvent
from midi_boilerplate.src.data_structures.pedal_event import SustainPedalEvent
from midi_boilerplate.src.data_structures.type_aliases import TimeType


class EventList(list[MidiEvent]):
    def __init__(self):
        super().__init__()
        self.last_pedal_message = None

    def append(self, event: MidiEvent) -> None:
        super().append(event)

    def __str__(self) -> str:
        return f'EventList({super()})'

    def __repr__(self) -> str:
        return str(self)

    def get_end_time(self) -> TimeType:
        """
        Returns the last offset of the event list.
        :return: The end time of the event list.
        """
        return max([event.offset for event in self])

    def get_start_time(self) -> TimeType:
        """
        Returns the start time of the event list.
        :return: The start time of the event list.
        """
        return min([event.time for event in self])

    def is_empty(self) -> bool:
        """
        Returns whether the event list is empty or not.
        :return: True if the event list is empty, False otherwise.
        """
        return len(self) == 0

    def before_time(self, timestamp: TimeType) -> 'EventList':
        """
        Returns the events that are before the given timestamp.
        :param timestamp: The timestamp to compare with.
        :return: The events that are before the given timestamp in a new EventList.
        """
        result = EventList()
        result.extend([event for event in self if event.time < timestamp])
        return result

    def after_time(self, timestamp: TimeType) -> 'EventList':
        """
        Returns the events that are after the given timestamp.
        :param timestamp: The timestamp to compare with.
        :return: The events that are after the given timestamp in a new EventList.
        """
        result = EventList()
        result.extend([event for event in self if event.time > timestamp])
        return result

    def get_number_of_pedal_events(self) -> int:
        """
        Returns the number of pedal events in the event list.
        :return: The number of pedal events.
        """
        return sum([1 for event in self if isinstance(event, SustainPedalEvent)])

    def add_pedal_event(self, time: TimeType, duration: TimeType, channel: int,
                        value: int) -> SustainPedalEvent:
        """
        Adds a pedal event to the event list.
        :param time: The time of the event.
        :param duration: The duration of the event.
        :param channel: The channel of the event.
        :param value: The value of the event.
        :return: The pedal event added.
        """
        pedal_event = SustainPedalEvent(time, duration, channel, value)
        self.append(pedal_event)
        return pedal_event

    def stop_events(self, last_timestamp: TimeType) -> None:
        """
        Stops the last pedal event.
        :param last_timestamp: The last note off time.
        :return: None
        """
        if self.last_pedal_message is not None and self.last_pedal_message['value'] != 0 \
                and last_timestamp - self.last_pedal_message['time'] > 0:
            self.add_pedal_event(self.last_pedal_message['time'], last_timestamp - self.last_pedal_message['time'],
                                 self.last_pedal_message['channel'],
                                 self.last_pedal_message['value'])
            self.last_pedal_message = None

    def filter_close_events(self) -> None:
        """
        Filters out events that are dangerous to be played back-to-back (0 to 127 to 0 for example).
        """
        result = EventList()
        pedal_events = [event for event in self if isinstance(event, SustainPedalEvent)]
        other_events = [event for event in self if not isinstance(event, SustainPedalEvent)]
        if len(pedal_events) > 0:
            result.append(pedal_events[0])
            for i in range(1, len(pedal_events) - 1):
                result.append(pedal_events[i])
            result.append(pedal_events[-1])
        self.clear()
        self.extend(other_events)
        self.extend(result)

    def add_midi_message(self, message: dict) -> MidiEvent | None:
        """
        Adds a midi message to the event list as A custom object (MidiEvent).
        IMPORTANT: This method is not complete. It only adds pedal events at this moment, but it can be extended to add
        other types of events.
        :param message: The message to add. (Can be a dictionary or a mido.Message)
        :return: MidiEvent
        """
        if message.message.is_control_change():
            # Args = control, value, channel
            if message.message.controller_value() == 64:
                # Wait for the next message to determine the duration if the pedal is pressed
                if self.last_pedal_message is None:  # FIXME
                    if message['value'] != 0:
                        self.last_pedal_message = message
                    return None
                else:  # Add the pedal event to the event list
                    pedal_event = self.add_pedal_event(self.last_pedal_message['time'],
                                                       message['time'] - self.last_pedal_message['time'],
                                                       self.last_pedal_message['channel'],
                                                       self.last_pedal_message['value'])
                    # Keep track of the last pedal message if it's still pressed
                    if message['value'] == 0:
                        self.last_pedal_message = None
                    else:
                        self.last_pedal_message = message
                    return pedal_event
            else:
                pass
        elif message['type'] == 'program_change':
            # Args = program, channel
            pass
        elif message['type'] == 'pitchwheel':
            # Args = pitch, channel
            pass
        elif message['type'] == 'aftertouch':
            # Args = value, channel
            pass
        elif message['type'] == 'polytouch':
            # Args = note, value, channel
            pass
        return MidiEvent(message['time'], 0, message['channel'])

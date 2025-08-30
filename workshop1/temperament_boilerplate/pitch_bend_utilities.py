import math

import mido

PITCH_BEND_RANGE = 2  # semitones


def midi_note_to_freq(note: int, base: float = 440.0) -> float:
    return base * (2 ** ((note - 69) / 12))


def freq_to_pitch_bend(target_freq: float, midi_note: int) -> int:
    equal_freq = midi_note_to_freq(midi_note)
    diff_semitones = 12 * math.log2(target_freq / equal_freq)
    bend = int((diff_semitones / PITCH_BEND_RANGE) * 8192)
    return max(-8192, min(8191, bend))


def tuned_frequency_absolute(midi_note: int, correction_factors: list[float]) -> float:
    """Return tuned frequency without reference to tonic.
    correction_factors[i] = ratio / ET for pitch class i.
    """
    pc = midi_note % 12
    base_freq = midi_note_to_freq(midi_note)
    return base_freq * correction_factors[pc]


def apply_temperament_absolute(mid: mido.MidiFile, correction_factors: list[float]) -> mido.MidiFile:
    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        set_pitch_bend_range(new_track, semitones=PITCH_BEND_RANGE, channel=0)

        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                tuned_freq = tuned_frequency_absolute(msg.note, correction_factors)
                bend = freq_to_pitch_bend(tuned_freq, msg.note)
                new_track.append(mido.Message('pitchwheel', pitch=bend, time=msg.time, channel=msg.channel))
                new_track.append(msg.copy(time=0))

            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                new_track.append(msg.copy())
                ch = getattr(msg, 'channel', 0)
                new_track.append(mido.Message('pitchwheel', pitch=0, time=0, channel=ch))

            else:
                new_track.append(msg.copy())

    return new_mid


def set_pitch_bend_range(track: mido.MidiTrack, semitones: int = 2, channel: int = 0):
    track.append(mido.Message('control_change', control=101, value=0, channel=channel, time=0))
    track.append(mido.Message('control_change', control=100, value=0, channel=channel, time=0))
    track.append(mido.Message('control_change', control=6, value=semitones, channel=channel, time=0))
    track.append(mido.Message('control_change', control=38, value=0, channel=channel, time=0))
    track.append(mido.Message('control_change', control=101, value=127, channel=channel, time=0))
    track.append(mido.Message('control_change', control=100, value=127, channel=channel, time=0))


ET = [2 ** (i / 12) for i in range(12)]


def make_corrections(ratios: list[float]) -> list[float]:
    """Return correction factors relative to equal temperament."""
    return [r / et for r, et in zip(ratios, ET)]

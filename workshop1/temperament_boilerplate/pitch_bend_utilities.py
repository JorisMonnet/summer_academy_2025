import math

import mido

PITCH_BEND_RANGE = 2  # in semitones


def midi_note_to_freq(note: int, base: float = 440.0) -> float:
    """Equal-tempered frequency for a MIDI note number."""
    return base * (2 ** ((note - 69) / 12))


def freq_to_pitch_bend(target_freq: float, midi_note: int) -> int:
    """Return pitch bend (-8192..8191) to tune midi_note (ET) to target_freq."""
    equal_freq = midi_note_to_freq(midi_note)
    diff_semitones = 12 * math.log2(target_freq / equal_freq)
    bend = int((diff_semitones / PITCH_BEND_RANGE) * 8192)
    return max(-8192, min(8191, bend))


def tuned_frequency_major_JI(midi_note: int, tonic_note: int, semitone_to_degree: dict,
                             temperament: list) -> float | None:
    """Given a MIDI note and a tonic, return the JI-major tuned frequency.
    Returns None if the note is chromatic (not in the major scale), in which case
    the caller should leave it equal-tempered (no bend).
    """
    semitone_offset = midi_note - tonic_note
    octave_offset, pc = divmod(semitone_offset, 12)

    if pc not in semitone_to_degree:
        return None

    degree_idx = semitone_to_degree[pc]
    ratio = temperament[degree_idx]

    # Account for octaves above/below the tonic
    ratio *= (2 ** octave_offset)

    tonic_freq = midi_note_to_freq(tonic_note)
    return tonic_freq * ratio


def apply_temperament_major_ji(mid: mido.MidiFile, tonic_note: int, semitone_to_degree: dict,
                               temperament: list) -> mido.MidiFile:
    """Apply Just Intonation (major) relative to the given tonic_note.
    - Preserves ticks_per_beat so timing is unchanged.
    - Inserts pitch bend at *the same timestamp* as note_on (by splitting delta time).
    - Resets pitch bend to 0 right after note_off.
    - Leaves chromatic notes (non-diatonic) unbent (equal temperament).
    NOTE: Pitch bend is per-MIDI-channel. Polyphonic passages needing different
    bends simultaneously on the same channel will not sound correct.
    """
    new_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for track in mid.tracks:
        new_track = mido.MidiTrack()
        new_mid.tracks.append(new_track)
        set_pitch_bend_range(new_track, semitones=PITCH_BEND_RANGE, channel=0)

        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                tuned_freq = tuned_frequency_major_JI(msg.note, tonic_note, semitone_to_degree, temperament)
                if tuned_freq is not None:
                    bend = freq_to_pitch_bend(tuned_freq, msg.note)
                    new_track.append(mido.Message('pitchwheel', pitch=bend, time=msg.time, channel=msg.channel))
                    new_track.append(msg.copy(time=0))
                else:
                    new_track.append(msg.copy())

            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                new_track.append(msg.copy())
                ch = msg.channel if hasattr(msg, 'channel') else 0
                new_track.append(mido.Message('pitchwheel', pitch=0, time=0, channel=ch))

            else:
                new_track.append(msg.copy())

    return new_mid


def set_pitch_bend_range(track: mido.MidiTrack, semitones: int = 2, channel: int = 0):
    track.append(mido.Message('control_change', control=101, value=0, channel=channel, time=0))  # RPN MSB
    track.append(mido.Message('control_change', control=100, value=0, channel=channel, time=0))  # RPN LSB
    track.append(mido.Message('control_change', control=6, value=semitones, channel=channel, time=0))  # Data Entry MSB
    track.append(mido.Message('control_change', control=38, value=0, channel=channel, time=0))  # Data Entry LSB
    track.append(mido.Message('control_change', control=101, value=127, channel=channel, time=0))  # RPN Null
    track.append(mido.Message('control_change', control=100, value=127, channel=channel, time=0))  # RPN Null

import mido

from workshop1.temperament_boilerplate.pitch_bend_utilities import apply_temperament_major_ji

JI_MAJOR = [
    1 / 1,
    9 / 8,
    5 / 4,
    4 / 3,
    3 / 2,
    5 / 3,
    15 / 8,
    2 / 1
]

ET_MAJOR = [
    1 / 1,
    2 ** (2 / 12),
    2 ** (4 / 12),
    2 ** (5 / 12),
    2 ** (7 / 12),
    2 ** (9 / 12),
    2 ** (11 / 12),
    2 / 1
]

PYTHAGOREAN_MAJOR = [
    1 / 1,
    9 / 8,
    81 / 64,
    4 / 3,
    3 / 2,
    27 / 16,
    243 / 128,
    2 / 1
]

SEMITONE_TO_DEGREE_MAJOR = {
    0: 0,
    2: 1,
    4: 2,
    5: 3,
    7: 4,
    9: 5,
    11: 6,
}

SEMITONE_TO_DEGREE_MINOR = {
    0: 0,
    2: 1,
    3: 2,
    5: 3,
    7: 4,
    8: 5,
    10: 6,
}

if __name__ == "__main__":
    input_path = "c_maj.mid"
    output_path = "output_et_major_C3.mid"
    tonic = 48  # C3

    tuned_mid = apply_temperament_major_ji(mido.MidiFile(input_path),
                                           tonic_note=tonic,
                                           semitone_to_degree=SEMITONE_TO_DEGREE_MAJOR,
                                           temperament=JI_MAJOR)
    tuned_mid.save(output_path)
    print(f"Saved tuned MIDI to {output_path}")
import mido

from workshop1.temperament_boilerplate.pitch_bend_utilities import ET, \
    apply_temperament_absolute, make_corrections

TEMPERAMENTS = {
    "JI": [
        1 / 1,
        16 / 15,
        9 / 8,
        6 / 5,
        5 / 4,
        4 / 3,
        45 / 32,
        3 / 2,
        8 / 5,
        5 / 3,
        9 / 5,
        15 / 8
    ],
    "Pythagorean": [
        1 / 1,
        256 / 243,
        9 / 8,
        32 / 27,
        81 / 64,
        4 / 3,
        729 / 512,
        3 / 2,
        128 / 81,
        27 / 16,
        16 / 9,
        243 / 128
    ],
    "ET": ET,
}

if __name__ == "__main__":
    input_path = "input.mid"

    temperament_name = "Pythagorean"

    output_path = f"tuned_{temperament_name}.mid"
    ratios = TEMPERAMENTS[temperament_name]
    tuned_mid = apply_temperament_absolute(mido.MidiFile(input_path), make_corrections(ratios))
    tuned_mid.save(output_path)

    print(f"Applied {temperament_name}, saved tuned MIDI to {output_path}")

#!/usr/bin/env python3

import argparse
import os
import shutil
import pandas as pd

import parselmouth
from parselmouth.praat import call, run_file

# Function to retrieve interval information
def get_coded_interval(tg, tier_number, interval_i):
    # Collect coding tier interval info
    int_label = call(tg, "Get label of interval", tier_number, interval_i).strip()
    int_start = call(tg, "Get start time of interval", tier_number, interval_i)
    int_end = call(tg, "Get end time of interval", tier_number, interval_i)
    int_mid = ((int_start+int_end)/2)

    # Collect corresponding word tier interval label based on time
    int_word = call(tg, "Get label of interval", tier_number+1, call(tg, "Get interval at time", tier_number+1, int_mid)).strip()

    if int_label and int_label != 'silent':
        return {'label': int_label, 'start': int_start, 'end': int_end, 'word': int_word}

def main(args):

    speaker_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings", args.speaker)

    # Set the folder path containing audio WAV files
    if args.originaldir:
        audio_in_path = os.path.join(speaker_path, "1_audio", "1_original")
    else:
        audio_in_path = os.path.join(speaker_path, "1_audio", "2_processed")


    audio_out_path = os.path.join(speaker_path, "1_audio", "3_extracted")
    if os.path.exists(audio_out_path):
        if args.overwrite:
            shutil.rmtree(audio_out_path)
            os.makedirs(audio_out_path)
        else:
            print("Extracted audio directory already exists. Rerun with -o to overwrite if desired.")
            os._exit(0)
    else:
        os.makedirs(audio_out_path)

    # Set the folder path containing TextGrid files
    tg_in_path = os.path.join(speaker_path, "2_textgrid", "2_manual")

    # Get a list of all TextGrid files in the folder
    tg_files = [f for f in os.listdir(tg_in_path) if f.endswith('.TextGrid')]

    if args.verbose:
        print(tg_files)

    # Iterate over the TextGrid files and get the corresponding audio file names
    for tg_file in tg_files:
        # Extract the base name of the TextGrid file without the extension
        tg_base_name = os.path.splitext(tg_file)[0]
        # Set the corresponding audio file path using the tg_base_name
        audio_file_path = os.path.join(audio_in_path, f"{tg_base_name}.wav")

        if args.verbose:
            print(audio_file_path)

        # Check if the audio file exists
        if os.path.exists(audio_file_path):
            # If it does, you can proceed to extract audio based on the TextGrid labels
            tg = parselmouth.read(os.path.join(tg_in_path, tg_file))
            sound = parselmouth.Sound(audio_file_path)

            coding_tier = 1

            n_coding_ints = call(tg, "Get number of intervals", coding_tier)
            # Collect interval info for all coded word intervals only
            coded_intervals = [get_coded_interval(tg, coding_tier, interval_i) for interval_i in range(1, n_coding_ints+1) if get_coded_interval(tg, coding_tier, interval_i) is not None]

            if args.verbose:
                print(coded_intervals)

            for i, interval in enumerate(coded_intervals):
                # Extract the audio segment
                audio_segment = sound.extract_part(from_time=interval['start'], to_time=interval['end'])

                # Set the file path to save the audio segment
                audio_save_path = os.path.join(audio_out_path, f"{tg_base_name}_{interval['word']}_{interval['label']}.wav")

                # Save the audio segment to a WAV file
                audio_segment.save(audio_save_path, format="WAV")

            print(f"Saved extracted audio files to {audio_out_path}")
        else:
            print(f"No corresponding audio file found for {tg_file}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=str, help='speaker code')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite extracted output directory')
    parser.add_argument('-d', '--originaldir', action='store_true', help='use audio from 1_original')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

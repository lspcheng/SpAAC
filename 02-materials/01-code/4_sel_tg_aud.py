#!/usr/bin/env python3

import argparse
import os
import shutil
import pandas as pd

import parselmouth
from parselmouth.praat import call, run_file

# Function to retrieve interval information
def is_target(audio_file, target_string):
    if not isinstance(target_string, str):
        target_string = str(target_string)
    audio_info = os.path.splitext(audio_file)[0].split('_')
    return audio_info[-1] == target_string

def main(args):

    speaker_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings", args.speaker)

    # Set the folder path containing audio WAV files
    audio_in_path = os.path.join(speaker_path, "1_audio", "3_extracted")

    # Set the folder path to write audio files to
    audio_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "1_audio")

    # Set the folder path containing TextGrid files
    tg_in_path = os.path.join(speaker_path, "2_textgrid", "3_extracted")

    # Set the folder path to write TextGrid files to
    tg_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "2_textgrid")

    concat_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "3_concatenated")

    if not args.prosody:
        if os.path.exists(audio_out_path):
            if args.overwrite:
                shutil.rmtree(audio_out_path)
                os.makedirs(audio_out_path)
                shutil.rmtree(tg_out_path)
                os.makedirs(tg_out_path)
                shutil.rmtree(concat_out_path)
                os.makedirs(concat_out_path)
            else:
                print("Selected audio directory already exists. Rerun with -o to overwrite if desired.")
                os._exit(0)
        else:
            os.makedirs(audio_out_path)
            os.makedirs(tg_out_path)
            os.makedirs(concat_out_path)

        print(f"\nSelecting target tokens...")

        # Get a list of all TextGrid files in the folder
        audio_dirs = sorted([d for d in os.listdir(audio_in_path) if os.path.isdir(os.path.join(audio_in_path, d))])
        if args.verbose:
            print(audio_dirs)

        # varnum_row_list = []
        # for j in range(1,9):
        #     for i in range(1,11):
        #         varnum_row_list.append(f"{j}-{i}")

        for audio_dir in audio_dirs:

            try:
                spk, session = audio_dir.split('-')
            except:
                spk = audio_dir
                session = '1' # or None
            if session == "supp":
                print("Ignoring 'supp' files.")
                continue

            if args.verbose:
                print(f"\nSpeaker Session: {audio_dir}")

            audio_files = sorted([f for f in os.listdir(os.path.join(audio_in_path, audio_dir)) if f.endswith('.wav')])

            target_audio_files = sorted([f for f in audio_files if is_target(f, 1) or is_target(f, 3) or is_target(f, '1a') or is_target(f, '3a')])

            if args.verbose:
                print(f"Total number of tokens: {len(target_audio_files)}")

            session_varnum_row_list = []
            count = 0
            # Copy files to output folder
            for audio_file in target_audio_files:
                audio_basename = os.path.splitext(audio_file)[0]

                _, varnum_row, word1_word2, code = audio_basename.split('_')
                varnum, row = varnum_row.split('-')
                word1, word2 = word1_word2.split('-')
                if code[0] == '2':
                    code = '2'
                    word = word2
                    variant = "O" # other (cOmpetitor)
                else:
                    word = word1
                    if code[0] == '1':
                        code = '1'
                        variant = "M" # Mainstream
                    elif code[0] == '3':
                        code = '3'
                        variant = "N" # Non-mainstream

                audio_out_filename = f"{spk}_{varnum_row}-{code}_{word}_{variant}.wav"
                tg_out_filename = f"{spk}_{varnum_row}-{code}_{word}_{variant}.TextGrid"

                # audio_variable_out_path = os.path.join(audio_out_path, f"v{varnum}")
                # tg_variable_out_path = os.path.join(audio_out_path, f"v{varnum}")
                # if not os.path.exists(audio_variable_out_path):
                #     os.makedirs(audio_variable_out_path)

                if args.verbose:
                    # if os.path.exists(os.path.join(audio_variable_out_path, audio_out_filename)):
                    if os.path.exists(os.path.join(audio_out_path, audio_out_filename)):
                        count += 1
                        print(f"{count}. Replacing existing file from {audio_dir}: {audio_out_filename}")

                # shutil.copyfile(os.path.join(audio_in_path, audio_dir, audio_file), os.path.join(audio_variable_out_path, audio_out_filename))
                shutil.copyfile(os.path.join(audio_in_path, audio_dir, audio_file), os.path.join(audio_out_path, audio_out_filename))
                shutil.copyfile(os.path.join(tg_in_path, audio_dir, f"{audio_basename}.TextGrid"), os.path.join(tg_out_path, tg_out_filename))

        print(f"\nCopied all selected files to {audio_out_path}")

        print(f"\nProcessing normalization and concatenation...")
        sorted_audio_files = sorted([(int(f.split('_')[1].split('-')[0]), int(f.split('_')[1].split('-')[1]), f) for f in os.listdir(audio_out_path)])
        sorted_tg_files = sorted([(int(f.split('_')[1].split('-')[0]), int(f.split('_')[1].split('-')[1]), f) for f in os.listdir(tg_out_path)])

        sounds = [parselmouth.Sound(os.path.join(audio_out_path, f)) for (v, r, f) in sorted_audio_files]
        call(sounds, "Scale peak", 0.99)
        call(sounds, "Scale intensity", 70.0)
        tgs = [parselmouth.read(os.path.join(tg_out_path, f)) for (v, r, f) in sorted_tg_files]

        if args.verbose:
            print(f"Opened sound files: {len(sounds)}")
            print(sounds[:5])
            print(f"Opened TextGrid files: {len(tgs)}")
            print(tgs[:5])

        ## Use original textgrid coding
        # concat_sounds = call(sounds, "Concatenate")
        # concat_tgs = call(tgs, "Concatenate")
        # call(concat_tgs, "Remove tier", 3)
        # call(concat_tgs, "Remove tier", 1)

        # Create new textgrid based on selected filenames
        concat_sounds, concat_tgs = call(sounds, "Concatenate recoverably")
        call(concat_tgs, "Replace interval texts", 1, 1, 0, "untitled", "", 'literals')
        for int_n in range(0, len(sorted_tg_files)):
            call(concat_tgs, "Set interval text", 1, int_n+1, os.path.splitext(sorted_tg_files[int_n][-1])[0])
        if args.verbose:
            print(f"Duration of concatenated sound: {concat_sounds.get_total_duration()}")
            # print(concat_sounds)
            print(f'Duration of concatenated TextGrid: {call(concat_tgs, "Get total duration")}')
            # print(concat_tgs)
        concat_sounds.save(os.path.join(concat_out_path, f"{spk}_words.wav"), format="WAV")
        concat_tgs.save(os.path.join(concat_out_path, f"{spk}_words.TextGrid"))

        print(f"\nConcatenated files saved to {concat_out_path}")

    else:
        print(f"\nExtracting prosodic information...")

        # Copy _ProsodyPro.praat to concat folder
        shutil.copyfile(os.path.join(os.path.dirname(__file__), "_ProsodyPro.praat"), os.path.join(concat_out_path, "_ProsodyPro.praat"))

        run_file([], os.path.join(concat_out_path, "_ProsodyPro.praat"),
                "2. Process all sounds without pause", 1, 1, '.label', '.wav',
                1, 0, 0,
                75, 600, 10, 100, # F0 Analysis options
                0, 500, 250, 5, 5500) # = female; male = 5000) #BID Analysis options
        run_file([], os.path.join(concat_out_path, "_ProsodyPro.praat"),
                "3. Get ensemble files", 1, 1, '.label', '.wav',
                1, 0, 0,
                75, 600, 10, 100, # F0 Analysis options
                0, 500, 250, 5, 5500) # = female; male = 5000) #BID Analysis options

        # Delete _ProsodyPro.praat from concat folder
        os.remove(os.path.join(concat_out_path, "_ProsodyPro.praat"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=str, help='speaker code')
    parser.add_argument('-p', '--prosody', action='store_true', help='extract prosodic information')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite extracted output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

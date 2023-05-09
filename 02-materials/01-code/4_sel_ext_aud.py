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
    base_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings")

    if args.speaker:
        speaker_list = args.speaker
    else:
        speaker_list = sorted([d for d in os.listdir(base_path) if d.startswith("S") and os.path.exists(os.path.join(base_path, d, "1_audio", "3_extracted"))])

    for speaker in speaker_list:

        print(f"\nCurrent speaker: {speaker}")

        speaker_path = os.path.join(base_path, speaker)

        # Set the folder path containing audio WAV files
        audio_in_path = os.path.join(speaker_path, "1_audio", "3_extracted")

        # Set the folder path to write audio files to
        audio_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "1_audio")
        audio_supp_out_path = os.path.join(audio_out_path, "supp")

        # Set the folder path containing TextGrid files
        tg_in_path = os.path.join(speaker_path, "2_textgrid", "3_extracted")

        # Set the folder path to write TextGrid files to
        tg_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "2_textgrid")
        tg_supp_out_path = os.path.join(tg_out_path, "supp")

        concat_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "3_concatenated")

        if os.path.exists(audio_out_path):
            if args.overwrite:
                for dir in [audio_out_path, tg_out_path, concat_out_path]:
                    shutil.rmtree(dir)
                    os.makedirs(dir)
            else:
                print("Selected audio directory already exists. Rerun with -o to overwrite if desired.")
                os._exit(0)
        else:
            for dir in [audio_out_path, tg_out_path, concat_out_path]:
                os.makedirs(dir)

        print(f"\nSelecting target tokens...")

        # Get a list of all TextGrid files in the folder
        audio_dirs = sorted([d for d in os.listdir(audio_in_path) if os.path.isdir(os.path.join(audio_in_path, d))])
        if args.verbose:
            print(audio_dirs)

        for audio_dir in audio_dirs:

            try:
                spk, session = audio_dir.split('-')
            except:
                spk = audio_dir
                session = '1' # or None
            if session == "supp":
                if os.path.exists(audio_supp_out_path):
                    if args.overwrite:
                        for dir in [audio_supp_out_path, tg_supp_out_path]:
                            shutil.rmtree(dir)
                            os.makedirs(dir)
                else:
                    for dir in [audio_supp_out_path, tg_supp_out_path]:
                        os.makedirs(dir)
                # If skipping supp files
                #print("Ignoring 'supp' files.")
                #continue

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

                if args.verbose:
                    if session != 'supp':
                        if os.path.exists(os.path.join(audio_out_path, audio_out_filename)):
                            count += 1
                            print(f"{count}. Replacing existing file from {audio_dir}: {audio_out_filename}")

                # Normalize and save files
                sound = parselmouth.Sound(os.path.join(audio_in_path, audio_dir, audio_file))
                call(sound, "Scale peak", 0.99)
                call(sound, "Scale intensity", 70.0)

                if session == 'supp':
                    audio_save_path = audio_supp_out_path
                    tg_save_path = tg_supp_out_path
                else:
                    audio_save_path = audio_out_path
                    tg_save_path = tg_out_path

                sound.save(os.path.join(audio_save_path, audio_out_filename), format="WAV")

                shutil.copyfile(os.path.join(tg_in_path, audio_dir, f"{audio_basename}.TextGrid"), os.path.join(tg_save_path, tg_out_filename))


        print(f"\nCopied and normalized all selected files to {audio_out_path}")

        print(f"\nProcessing concatenation...")

        # Sort files by variableN and rowN
        sorted_audio_files = sorted([(int(f.split('_')[1].split('-')[0]), int(f.split('_')[1].split('-')[1]), f) for f in os.listdir(audio_out_path) if f.endswith('.wav')] )
        sorted_tg_files = sorted([(int(f.split('_')[1].split('-')[0]), int(f.split('_')[1].split('-')[1]), f) for f in os.listdir(tg_out_path) if f.endswith('.TextGrid')] )

        sounds = [parselmouth.Sound(os.path.join(audio_out_path, f)) for (v, r, f) in sorted_audio_files]
        # call(sounds, "Scale peak", 0.99)
        # call(sounds, "Scale intensity", 70.0)
        tgs = [parselmouth.read(os.path.join(tg_out_path, f)) for (v, r, f) in sorted_tg_files]

        if args.verbose:
            print(f"Opened sound files: {len(sounds)}")
            print(sounds[:5])
            print(f"Opened TextGrid files: {len(tgs)}")
            print(tgs[:5])

        # Create new textgrid based on selected filenames
        concat_sounds, concat_tgs = call(sounds, "Concatenate recoverably")
        call(concat_tgs, "Replace interval texts", 1, 1, 0, "untitled", "", 'literals')
        # Create log file
        out_df = pd.DataFrame(columns=['filename', 'speaker', 'item_code', 'variableN', 'rowN', 'variantN', 'word', 'variant'])

        for int_n in range(0, len(sorted_tg_files)):
            token_filename = os.path.splitext(sorted_tg_files[int_n][-1])[0]
            spk, item_code, word, variant = token_filename.split('_')
            variableN, rowN, variantN = item_code.split('-')

            data_row = {'filename': token_filename, 'speaker': spk, 'item_code': item_code, 'variableN': variableN, 'rowN': rowN, 'variantN': variantN, 'word': word, 'variant': variant}
            out_df = out_df.append(data_row, ignore_index=True, sort=False)

            call(concat_tgs, "Set interval text", 1, int_n+1, token_filename)

        if args.verbose:
            print(f"Duration of concatenated sound: {concat_sounds.get_total_duration()}")
            print(f'Duration of concatenated TextGrid: {call(concat_tgs, "Get total duration")}')

        # Save files
        concat_sounds.save(os.path.join(concat_out_path, f"{spk}_selected_tokens.wav"), format="WAV")
        concat_tgs.save(os.path.join(concat_out_path, f"{spk}_selected_tokens.TextGrid"))
        out_df.to_csv(os.path.join(concat_out_path, f"{spk}_selected_tokens_info.csv"), index=False)

        print(f"\nConcatenated files saved to {concat_out_path}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=lambda s: [item for item in s.split(',')], help='speaker code (delimited list input); if empty, all speakers')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite extracted output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

#!/usr/bin/env python3

import argparse
import os
import shutil
import pandas as pd

import parselmouth
from parselmouth.praat import call, run_file

def main(args):

    speaker_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings", args.speaker)

    # Set the folder path containing original files
    concat_in_path = os.path.join(speaker_path, "3_selections", "1_P1", "3_concatenated")

    # Set the folder path to write files to for alignment
    original_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "4_aligned", "original_corpus")
    aligner_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "4_aligned", "mfa_aligner")
    aligned_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "4_aligned", "aligned_corpus")

    # Get selected tokens from previous step
    concat_wavs = [f for f in os.listdir(concat_in_path) if f.endswith('.wav')]
    concat_tgs = [f for f in os.listdir(concat_in_path) if f.endswith('.TextGrid')]

    run = 0

    if args.alignment:
        run = 1
        if os.path.exists(original_out_path):
            if args.overwrite:
                for dir in [original_out_path, aligner_out_path, aligned_out_path]:
                    shutil.rmtree(dir)
                    os.makedirs(dir)
            else:
                print("Alignment directories already exists. Rerun with -o to overwrite if desired.")
                os._exit(0)
        else:
            for dir in [original_out_path, aligner_out_path, aligned_out_path]:
                os.makedirs(dir)

        # Get version of textgrid with words on Tier 1
        for tg_file in concat_tgs:
            tg = parselmouth.read(os.path.join(concat_in_path, tg_file))
            call(tg, "Replace interval texts", 1, 1, 0,
            "_[A-Z]", "", "Regular Expressions")
            call(tg, "Replace interval texts", 1, 1, 0,
            "(.+)_", "", "Regular Expressions")
            tg.save(os.path.join(original_out_path, tg_file))

        for wav_file in concat_wavs:
            shutil.copy(os.path.join(concat_in_path, wav_file), original_out_path)

        print(f"\nSaved corpus files to {original_out_path}")

    if args.prosody or args.formants:

        if not os.path.exists(original_out_path):
            print("Acoustic extraction not run. Please rerun with -a.")
            os.exit()

    if args.prosody:
        run = 2

        word_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "5_profiled", "word_level")

        if os.path.exists(word_out_path):
            if args.overwrite:
                shutil.rmtree(word_out_path)
                os.makedirs(word_out_path)
            else:
                print("Word-level acoustic data directory already exists. Rerun with -o to overwrite if desired.")
                os._exit(0)
        else:
            os.makedirs(word_out_path)

        print(f"\nExtracting prosodic information...")

        # Access target files
        original_tgs = [f for f in os.listdir(original_out_path) if f.endswith('.TextGrid')]
        for tg_file in original_tgs:
            shutil.copy(os.path.join(original_out_path, tg_file), word_out_path)
        for wav_file in concat_wavs:
            shutil.copy(os.path.join(concat_in_path, wav_file), word_out_path)

        # Copy _ProsodyPro.praat to concat folder
        temp_script_path = os.path.join(word_out_path, "_ProsodyPro.praat")
        shutil.copyfile(os.path.join(os.path.dirname(__file__), "_ProsodyPro.praat"), temp_script_path)

        run_file([], temp_script_path,
                "2. Process all sounds without pause", 1, 1, '.label', '.wav',
                1, 0, 0,
                75, 600, 10, 100, # F0 Analysis options
                0, 500, 250, 5, 5500) # = female; male = 5000) #BID Analysis options
        run_file([], temp_script_path,
                "3. Get ensemble files", 1, 1, '.label', '.wav',
                1, 0, 0,
                75, 600, 10, 100, # F0 Analysis options
                0, 500, 250, 5, 5500) # = female; male = 5000) #BID Analysis options

        # Delete _ProsodyPro.praat from concat folder
        os.remove(temp_script_path)
        for wav_file in concat_wavs:
            os.remove(os.path.join(word_out_path, wav_file))

    if args.formants or args.fasttrack:

        target_dict = {'1': 'EH1', '2': 'IY1', '3': 'DH', '4': 'OW1', '5': 'UW1', '6': 'AE1', '7': 'AE1', '8': 'T'}

        # Access target files
        aligned_tgs = [f for f in os.listdir(os.path.join(aligned_out_path)) if f.endswith('.TextGrid')]

        if not aligned_tgs:
            print("No aligned textgrid found. Please conduct forced alignment before rerunning with -f or -ft.")
            os._exit(0)

        for tg_file in aligned_tgs:
            tg_concat = parselmouth.read(os.path.join(concat_in_path, tg_file))
            tg_aligned = parselmouth.read(os.path.join(aligned_out_path, tg_file))

            tg_merged = call([tg_concat, tg_aligned], "Merge")
            call(tg_merged, "Insert interval tier", 1, "targets")
            n_phone_ints = call(tg_merged, "Get number of intervals", 4)
            if args.verbose:
                print(n_phone_ints)
            for int_i in range(1, n_phone_ints+1):
                phone_label = call(tg_merged, "Get label of interval", 4, int_i)
                if phone_label in target_dict.values():
                    phone_start = call(tg_merged, "Get start time of interval", 4, int_i)
                    if args.verbose:
                        print(int_i, phone_label, phone_start)
                    cond_int_i = call(tg_merged, "Get interval at time", 2, phone_start)
                    spk, item_code, word, variant = call(tg_merged, "Get label of interval", 2, cond_int_i).split('_')
                    variableN, rowN, variantN = item_code.split('-')
                    if args.verbose:
                        print(spk, item_code, word, variant)
                        print(variableN, rowN, variantN)
                        print(target_dict[variableN])
                    if phone_label == target_dict[variableN]:
                        phone_end = call(tg_merged, "Get end time of interval", 4, int_i)
                        call(tg_merged, "Insert boundary", 1, phone_start)
                        call(tg_merged, "Insert boundary", 1, phone_end)
                        call(tg_merged, "Set interval text", 1, call(tg_merged, "Get interval at time", 1, phone_start), phone_label)

        if args.formants:
            run = 3

            phone_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "5_profiled", "phone_level")

            if os.path.exists(phone_out_path):
                if args.overwrite:
                    shutil.rmtree(phone_out_path)
                    os.makedirs(phone_out_path)
                else:
                    print("Phone-level acoustic data directory already exists. Rerun with -o to overwrite if desired.")
                    os._exit(0)
            else:
                os.makedirs(phone_out_path)

            tg_merged.save(os.path.join(phone_out_path, tg_file))

            for wav_file in concat_wavs:
                shutil.copy(os.path.join(concat_in_path, wav_file), phone_out_path)

            print(f"\nExtracting formant information...")

            # Copy _FormantPro.praat to folder
            temp_script_path = os.path.join(phone_out_path, "_FormantPro.praat")
            shutil.copyfile(os.path.join(os.path.dirname(__file__), "_FormantPro.praat"), temp_script_path)

            run_file([], temp_script_path,
                    "2. Process all sounds without pause", 1, 1, 0, 0, "repetition_list.txt", 0,
                    ".TextGrid", ".wav",
                    "./", "speaker_folders.txt",
                    5, 5500, 0.25, # Formant Analysis options options
                    10, # Number of normalized times per interval
                    0.10)
            run_file([], temp_script_path,
                    "3. Get ensemble files",  1, 1, 0, 0, "repetition_list.txt", 0,
                    ".TextGrid", ".wav",
                    "./", "speaker_folders.txt",
                    5, 5500, 0.25, # Formant Analysis options options
                    10, # Number of normalized times per interval
                    0.10)

            # Delete _FormantPro.praat from folder
            os.remove(temp_script_path)
            for wav_file in concat_wavs:
                os.remove(os.path.join(phone_out_path, wav_file))

        if args.fasttrack:
            run = 4

            fasttrack_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "5_profiled", "phone_level_ft")

            if os.path.exists(fasttrack_out_path):
                if args.overwrite:
                    shutil.rmtree(fasttrack_out_path)
                    os.makedirs(fasttrack_out_path)
                else:
                    print("Phone-level (FastTrack) acoustic data directory already exists. Rerun with -o to overwrite if desired.")
                    os._exit(0)
            else:
                os.makedirs(fasttrack_out_path)

            tg_merged.save(os.path.join(fasttrack_out_path, tg_file))

            for wav_file in concat_wavs:
                shutil.copy(os.path.join(concat_in_path, wav_file), fasttrack_out_path)

            print(f"Open the files in Praat and run 'Extract vowels with Textgrid' using folder:\n\n{os.path.abspath(fasttrack_out_path)}\n")

            print("Then run 'Track folder'.")

    if not run:
        print("No processes selected. Rerun with appropriate flag as needed.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=str, help='speaker code')
    parser.add_argument('-a', '--alignment', action='store_true', help='prep for forced alignment')
    parser.add_argument('-p', '--prosody', action='store_true', help='extract prosodic information')
    parser.add_argument('-f', '--formants', action='store_true', help='extract formant information')
    parser.add_argument('-ft', '--fasttrack', action='store_true', help='prep for extracting formant information via fasttrack')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite extracted output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

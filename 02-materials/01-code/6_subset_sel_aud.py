#!/usr/bin/env python3

import argparse
import os
import shutil
import pandas as pd
import random
import glob

import parselmouth
from parselmouth.praat import call, run_file

def main(args):

    base_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings")

    # Get processed speaker list
    token_file_paths = glob.glob(os.path.join(base_path, "**", "*selected_tokens_info.csv"), recursive=True)
    token_file_info = sorted([(os.path.normpath(p).split(os.path.sep)[-5], os.path.normpath(p).split(os.path.sep)[-1], p) for p in token_file_paths])

    speaker_list = [info[0] for info in token_file_info]
    if args.verbose:
        print(f"All available speakers: {speaker_list}")

    if args.speaker:
        speaker_list = args.speaker

    if args.verbose:
        print(f"Speakers to process: {speaker_list}\n")

    # Create aggregate folder
    if args.aggregate:
        aggregate_auto_out_path = os.path.join(base_path, "1_aggregate", "1_ratings", "temp")
        aggregate_manual_out_path = os.path.join(base_path, "1_aggregate", "1_ratings", "1_manual")
        aggregate_norming_out_path = os.path.join(base_path, "1_aggregate", "1_norming", "temp")

        # Set aggregate path
        if args.variableN:
            aggregate_path = aggregate_auto_out_path
        elif args.random:
            aggregate_path = aggregate_norming_out_path

        if os.path.exists(aggregate_path):
            if args.overwrite:
                shutil.rmtree(aggregate_path)
                os.makedirs(aggregate_path)
            else:
                print("Output directory already exists. Rerun with -o to overwrite if desired.")
                os._exit(0)
        else:
            os.makedirs(aggregate_path)

        if args.variableN:
            if not os.path.exists(aggregate_manual_out_path):
                os.makedirs(aggregate_manual_out_path)

    # Generate random list if it doesn't already exist
    if args.random:
        random_filepath = os.path.join(os.path.dirname(__file__), f"N2_random_items.csv")

        if not os.path.exists(random_filepath):
            if args.verbose:
                print(f"Creating {random_filepath}...")
            full_df = pd.DataFrame()
            for spk, fn, fp in token_file_info:
                # merge files together
                spk_df = pd.read_csv(fp)
                spk_df = spk_df.loc[(spk_df['variantN'] == 1)]
                spk_df = spk_df.loc[spk_df['variableN'].isin(range(5,9))]
                full_df = pd.concat([full_df, spk_df])
            # if args.verbose:
            #     print(full_df)

            n_speakers = full_df['speaker'].nunique()
            word_counts = full_df['word'].value_counts()
            included_words = [word_counts.index[i] for i, c in enumerate(word_counts) if c == n_speakers]
            # if args.verbose:
            #     print(included_words)

            included_df = full_df.loc[full_df['word'].isin(included_words)]
            # if args.verbose:
            #     print(included_df.nunique())

            included_items_df = included_df[['item_code', 'variableN', 'rowN', 'variantN', 'word']].drop_duplicates()
            # if args.verbose:
            #     print(included_items_df)

            random_items_df = pd.DataFrame()
            for current_N in range(5, 9):
                current_df = included_items_df.loc[(included_items_df['variableN'] == current_N)]
                sample_df = current_df.sample(n=3, random_state=args.random) #4 #6
                random_items_df = pd.concat([random_items_df, sample_df])

            # Randomly shuffle rows
            random_items_df = random_items_df.sample(frac=1, random_state=args.random)
            random_items_df = random_items_df.assign(random_state=args.random)
            # Save output reference file to 01-code
            random_items_df.to_csv(random_filepath, index=False)
        else:
            if args.verbose:
                print(f"Using existing {random_filepath}...")

        # Read in random items list
        random_items_df = pd.read_csv(random_filepath).reset_index()
        if args.verbose:
            print(random_items_df)

    # Extract selected files (regardless of aggregate or not)
    for speaker in speaker_list:
        speaker_path = os.path.join(base_path, speaker)

        # Set the folder path containing original files
        audio_in_path = os.path.join(speaker_path, "3_selections", "1_P1", "1_audio")
        concat_in_path = os.path.join(speaker_path, "3_selections", "1_P1", "3_concatenated")

        print(f"\nCurrent speaker: {speaker}")

        selected_wavs = [f for f in os.listdir(audio_in_path) if f.endswith('.wav')]
        selected_info = [f for f in os.listdir(concat_in_path) if f.endswith('.csv')]

        # Set the folder path to write files to
        if args.random:
            subset_out_path = os.path.join(speaker_path, "3_selections", "0_N2", "1_audio")
        if args.variableN and args.aggregate:
            subset_out_path = aggregate_auto_out_path
        elif args.variableN:
            subset_out_path = os.path.join(speaker_path, "3_selections", "1_P1", "6_subsetted")

        if not args.aggregate:
            if os.path.exists(subset_out_path):
                if args.overwrite:
                    shutil.rmtree(subset_out_path)
                    os.makedirs(subset_out_path)
                else:
                    print("Output directory already exists. Rerun with -o to overwrite if desired.")
                    os._exit(0)
            else:
                os.makedirs(subset_out_path)

        # Run random token selection + concatenate
        # Always save to local speaker folders
        # If args.aggregate, additionally save to aggregate folder
        if args.random:
            subset_concat_out_path = os.path.join(speaker_path, "3_selections", "0_N2", "2_concatenated")
            if not os.path.exists(subset_concat_out_path):
                os.makedirs(subset_concat_out_path)

            for csv_file in selected_info:
                token_df = pd.read_csv(os.path.join(concat_in_path, csv_file))
                subset_df = token_df.loc[(token_df['item_code'].isin( random_items_df['item_code'].to_list()))]
                # Sort subset_filenames to be in scrambled order
                sorted_subset_df = pd.merge(subset_df, random_items_df, on=['item_code', 'variableN', 'rowN', 'variantN', 'word']).sort_values(by='index')

                if args.verbose:
                    print(sorted_subset_df)

                # Extract subsetted_df filename column (as list)
                subset_filenames = sorted_subset_df['filename'].to_list()

                # Create copied files, adding silence padding between tokens
                sil1 = call('Create Sound from formula', "silence", 1, 0, 0.25, 44100, "0")
                sil2 = call('Create Sound from formula', "silence", 1, 0, 0.25, 44100, "0")
                for fn in subset_filenames:
                    sound = parselmouth.Sound(os.path.join(audio_in_path, f"{fn}.wav"))
                    padded_sound = call([sil1, sound, sil2], 'Concatenate')
                    padded_sound.save(os.path.join(subset_out_path, f"{fn}.wav"), format="WAV")

                # Concatenate copied/padded files
                sounds = [parselmouth.Sound(os.path.join(subset_out_path, f"{fn}.wav")) for fn in subset_filenames]
                concat_sounds, concat_tgs = call(sounds, "Concatenate recoverably")
                call(concat_tgs, "Replace interval texts", 1, 1, 0, "untitled", "", 'literals')
                for int_n, int_label in enumerate(subset_filenames):
                  call(concat_tgs, "Set interval text", 1, int_n+1, int_label)

                # Save files
                concat_sounds.save(os.path.join(subset_concat_out_path, f"{speaker}_random_tokens.wav"), format="WAV")
                concat_tgs.save(os.path.join(subset_concat_out_path, f"{speaker}_random_tokens.TextGrid"))

                # Save copy of file to aggregate
                if args.aggregate:
                    concat_sounds.save(os.path.join(aggregate_norming_out_path, f"{speaker}_random_tokens.wav"), format="WAV")

        # Run variable subset token selection + coding script preparation
        # Save to local speaker folder or if args.aggregate, to aggregate folder
        if args.variableN:

            for vN in args.variableN:

                vN_out_path = os.path.join(subset_out_path, f"v{vN}")
                if not os.path.exists(vN_out_path):
                    os.makedirs(os.path.join(vN_out_path, "sounds_in"))
                    os.makedirs(os.path.join(vN_out_path, "sounds_out"))

                temp_script_path = os.path.join(vN_out_path, "soundfile_rating_randomblind.praat")

                # Read and edit script
                with open(os.path.join(os.path.dirname(__file__), "soundfile_rating_randomblind.praat"), 'r', encoding='utf-8') as script_file:
                    script_data = script_file.read()
                    script_data = script_data.replace("positive Rating_variable 3", f"positive Rating_variable {vN}")

                # Write script versions to output folders
                with open(temp_script_path, 'w') as script_file:
                  script_file.write(script_data)

                # Subset csv list for only those that have variableN in the list of args.variableN
                for csv_file in selected_info:
                    token_df = pd.read_csv(os.path.join(concat_in_path, csv_file))
                    subset_df = token_df.loc[(token_df['variableN'] == vN)]

                    if args.verbose:
                        print(subset_df)

                    # Extract subsetted_df filename column (as list)
                    subset_filenames = subset_df['filename'].to_list()

                    # Copy files
                    for fn in subset_filenames:
                        shutil.copy(os.path.join(audio_in_path, f"{fn}.wav"), os.path.join(vN_out_path, "sounds_in"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=lambda s: [item for item in s.split(',')], help='speaker code (delimited list input); if empty, all speakers')
    # parser.add_argument('-p', '--path', default=None, type=str, help='output path')
    parser.add_argument('-r', '--random', default=6, type=int, help='generate random sample and save random tokens (individual and concatenated); takes integer argument as random seed (default: 6)')
    parser.add_argument('-n', '--variableN', default=None, type=lambda s: [int(item) for item in s.split(',')], help='variableNs to subset (delimited list input)')
    parser.add_argument('-a', '--aggregate', action='store_true', help='aggregate by-speaker output into separate directory')
    parser.add_argument('-o', '--overwrite', action='store_true', help='overwrite extracted output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

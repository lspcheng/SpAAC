#!/usr/bin/env python3

# NOTE: Concatenate WAV files into one before using this script

import argparse
import os
import pandas as pd

import parselmouth
from parselmouth.praat import call, run_file

def main(args):

    speaker_path = os.path.join("..", "02-stimuli", "P0-norming", "n2", "03-recordings", args.speaker)

    if args.originaldir:
        audio_in_path = os.path.join(speaker_path, "1_audio", "1_original")
    else:
        audio_in_path = os.path.join(speaker_path, "1_audio", "2_processed")
    tg_out_path = os.path.join(speaker_path, "2_textgrid", "1_original")

    if args.filename:
        name, _ = os.path.splitext(args.filename)
        wav_files = [f"{name}.wav"]
    else:
        wav_files = [f for f in os.listdir(audio_in_path) if f.endswith('.wav')]

    if args.verbose:
        print(wav_files)

    n_wav = len(wav_files)
    if n_wav == 0:
        print("\nNo audio file found. Exiting script.")
        os._exit(0)

    # read in variable and word labels
    if args.number == 0:
        var_boundary_labels = []
        word_boundary_labels = []
    elif args.number == 9:
        suppwordrows = pd.read_csv("recordings_suppwordrows.csv")
        var_boundary_labels = suppwordrows['Variable_Name'].unique().tolist()
        word_boundary_labels = suppwordrows['Word_Code'].tolist()
    else:
        wordrows = pd.read_csv("recordings_wordrows.csv")
        if args.number == None:
            var_boundary_labels = wordrows['Variable_Name'].unique().tolist()
            word_boundary_labels = wordrows['Word_Code'].tolist()
        else:
            var_boundary_labels = wordrows.loc[wordrows['Variable_Num'] == args.number]['Variable_Name'].unique().tolist()
            word_boundary_labels = wordrows.loc[wordrows['Variable_Num'] == args.number]['Word_Code'].tolist()


    n_var = len(var_boundary_labels)
    if args.verbose:
        print("\nNumber of variables per file: {0}".format(n_var))

    for wav in wav_files:

        print("\nProcessing TextGrid for {0}...".format(wav))

        wav_fn = os.path.join(audio_in_path, wav)
        name, ext = os.path.splitext(wav)
        tg_fn = os.path.join(tg_out_path, name+".TextGrid")

        if args.verbose:
            print("\nInput WAV file name: {0}".format(wav_fn))
            print("Output TG file name: {0}".format(tg_fn))

        # Process sound
        sound = parselmouth.Sound(wav_fn)
        total_duration = sound.get_total_duration()
        if args.verbose:
            print("\nFile duration (s): {0}".format(total_duration))

        # Process textgrid
        textgrid = call(sound, 'To TextGrid (silences)...',
                        # intensity analysis parameters (default)
                        100,
                        0,
                        # silence threshold (dB)
                        args.threshold,
                        # min silent/sounding interval
                        args.silentint,
                        args.soundingint,
                        # silent/sounding labels (default)
                        "silent",
                        ""
                        )

        call(textgrid, 'Insert interval tier', 2, 'row')
        call(textgrid, 'Insert interval tier', 3, 'variable')
        call(textgrid, 'Insert point tier', 4, 'notes')

        if n_var != 0:
            # Get variable & word boundary timestamps
            var_int_dur = total_duration / n_var
            var_boundary_times = [var_int_dur * boundary_i for boundary_i in range(1, n_var)]

            n_word = 14 if args.number ==9 else 10
            word_boundary_times = [var_int_dur/n_word * boundary_i for boundary_i in range(1, n_var*n_word)]

            if args.verbose:
                print("\nNumber of variable boundaries: {0}".format(len(var_boundary_times)))
                print("Number of word boundaries: {0}".format(len(word_boundary_times)))

            for boundary_time in var_boundary_times:
                call(textgrid, 'Insert boundary', 3, boundary_time)

            for word_time in word_boundary_times:
                call(textgrid, 'Insert boundary', 2, word_time)

            for i, boundary_label in enumerate(var_boundary_labels):
                # print(i, boundary_label)
                call(textgrid, 'Set interval text', 3, i+1, boundary_label)

            for i, word_label in enumerate(word_boundary_labels):
                # print(i, word_label)
                call(textgrid, 'Set interval text', 2, i+1, word_label)

        # Save to output dir
        textgrid.save(tg_fn)
        print("\nSaved TextGrid to: {0}".format(tg_fn))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=str, help='speaker code')
    parser.add_argument('-t', '--threshold', default="-50", type=int, help='silence threshold (dB); default=-50')
    parser.add_argument('-i', '--silentint', default="0.2", type=float, help='minimum silent interval (s); default=0.2')
    parser.add_argument('-o', '--soundingint', default="0.3", type=float, help='minimum sounding interval (s); default=0.3')
    parser.add_argument('-f', '--filename', default=None, type=str, help='file name if processing only one file')
    parser.add_argument('-n', '--number', default=None, type=int, help='variable number (1-8) if processing only one variable; use 0 if no variable labels should be added; use 9 if supplementary variable')
    parser.add_argument('-d', '--originaldir', action='store_true', help='use audio from 1_original for checking')
    parser.add_argument('-v', '--verbose', action='store_true', help='print out processing checks')


    args = parser.parse_args()

    main(args)

# Leftovers

    # Get project name/path
    # file_dir = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    # project = file_dir[-3]
    # recordings_path = os.path.join(project, "02-materials", "03-stimuli", "P0-norming", "n2", "03-recordings")

    # # Get number of variables estimated for each file by num of files
    # n_var_per_wav = int(8 / n_wav)
    # if args.verbose:
    #     print(n_var_per_wav)

    # Get number of intervals. need to make sure labels start from the last one that was used, if multiple files — Actually, just make sure to concanate all files together in order when doing WAV processing.
    # n_var_int = call(textgrid, 'Get number of intervals', 3)

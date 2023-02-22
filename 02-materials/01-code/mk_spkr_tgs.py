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

    wav_list = [f for f in os.listdir(os.path.join(audio_in_path)) if f.endswith('.wav')]
    # print(wav_list)

    n_wav = len(wav_list)
    if n_wav == 0:
        print("No processed audio file found. Exiting script.")
        os._exit(0)

    # Get number of variables estimated for each file by num of files
    n_var_per_wav = int(8 / n_wav)

    var_boundary_labels = ['PIN-PEN', 'FEEL-FILL', 'TH-stopping', 'OU-backing', 'U-fronting', 'AEN-raising', 'AE-backing', 'T-deletion']

    # read in word labels
    wordrows = pd.read_csv("recordings_wordrows.csv")
    word_boundary_labels = wordrows['Word_Code'].tolist()

    for wav in wav_list:

        print("Processing TextGrid for {0}...".format(wav))

        wav_fn = os.path.join(audio_in_path, wav)
        name, ext = os.path.splitext(wav)
        tg_fn = os.path.join(tg_out_path, name+".TextGrid")

        # Process sound
        sound = parselmouth.Sound(wav_fn)
        total_duration = sound.get_total_duration()
        # print("File duration (s): {0}".format(total_duration))

        # Get variable & word boundary timestamps
        var_int_dur = total_duration / n_var_per_wav
        var_boundary_times = [var_int_dur * boundary_i for boundary_i in range(1, n_var_per_wav)]
        word_boundary_times = [var_int_dur/10 * boundary_i for boundary_i in range(1, n_var_per_wav*10)]

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
        print("Saved TextGrid to: {0}".format(tg_fn))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Create speaker textgrids.')

    parser.set_defaults(func=None)
    parser.add_argument('-s', '--speaker', default=None, type=str, help='speaker code')
    parser.add_argument('-t', '--threshold', default="-50", type=int, help='silence threshold (dB); default=-50')
    parser.add_argument('-i', '--silentint', default="0.2", type=float, help='minimum silent interval (s); default=0.2')
    parser.add_argument('-o', '--soundingint', default="0.3", type=float, help='minimum sounding interval (s); default=0.3')
    parser.add_argument('-d', '--originaldir', action='store_true', help='use audio from 1_original for checking')

    args = parser.parse_args()

    main(args)

# Leftovers

    # Get project name/path
    # file_dir = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    # project = file_dir[-3]
    # recordings_path = os.path.join(project, "02-materials", "03-stimuli", "P0-norming", "n2", "03-recordings")

    # Get number of intervals. need to make sure labels start from the last one that was used, if multiple files — Actually, just make sure to concanate all files together in order when doing WAV processing.
    # n_var_int = call(textgrid, 'Get number of intervals', 3)

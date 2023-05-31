# (0) Using aligner
**Open up virtual env:**

conda activate aligner

**Close virtual env:**

conda deactivate

---

# (1) Validate

## Structure
mfa validate -t [[temp_alignment_folder]] [corpus_directory] [dictionary_path] [optional_acoustic_model_path]

---
# (2) Generate dictionary
## Structure
mfa g2p [g2p_model_path] [input_path] [output_path]

___
# (3) Align

## Structure
mfa align -t [[temp_alignment_folder]] [corpus_directory] [dictionary_path] [acoustic_model_path] [output_directory]

---

# Steps

## First Pass (Dictionary Prep)
speaker = S01

## (1) Validate
### ignoring acoustics (with original dictionary)
mfa validate -t ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/mfa_aligner ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/original_corpus ~/Documents/MFA/pretrained_models/dictionary/english.dict --ignore_acoustics --clean

### w/ acoustic model (testing, but don't need probably)
mfa validate -t ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/mfa_aligner ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/original_corpus ~/Documents/Projects/SpAAC/02-materials/01-code/mfa-english.dict --acoustic_model_path ~/Documents/MFA/pretrained_models/acoustic/english.zip --clean

## (2) Generate Dictionary for OOVs (only need once)
mfa g2p ~/Documents/MFA/pretrained_models/g2p/english_g2p.zip ~/Documents/Projects/SpAAC/02-materials/01-code/mfa/oovs_found.txt ~/Documents/Projects/SpAAC/02-materials/01-code/mfa/oovs.dict

### + Manual dictionary modification
(Update dictionary saved to: ~/Documents/Projects/SpAAC/02-materials/01-code/mfa/english.dict)

## (3) Align
### w/ original dictionary
mfa align -t ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/mfa_aligner ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/original_corpus ~/Documents/MFA/pretrained_models/dictionary/english.dict --acoustic_model_path ~/Documents/MFA/pretrained_models/acoustic/english.zip ../02-stimuli/P0-norming/n2/03-recordings/S01/3_selections/1_P1/4_aligned/aligned_corpus


## Follow-up Runs
speaker = S03

## (1) Validate

### ignoring acoustics (for dictionary only with updated dictionary)
mfa validate -t ../02-stimuli/P0-norming/n2/03-recordings/S03/3_selections/1_P1/4_aligned/mfa_aligner ../02-stimuli/P0-norming/n2/03-recordings/S03/3_selections/1_P1/4_aligned/original_corpus ~/Documents/Projects/SpAAC/02-materials/01-code/mfa/english.dict --ignore_acoustics --clean

## (3) Align

### w/ OOV-supplemented dictionary
mfa align -t ../02-stimuli/P0-norming/n2/03-recordings/S03/3_selections/1_P1/4_aligned/mfa_aligner ../02-stimuli/P0-norming/n2/03-recordings/S03/3_selections/1_P1/4_aligned/original_corpus ~/Documents/Projects/SpAAC/02-materials/01-code/mfa/english.dict --acoustic_model_path ~/Documents/MFA/pretrained_models/acoustic/english.zip ../02-stimuli/P0-norming/n2/03-recordings/S03/3_selections/1_P1/4_aligned/aligned_corpus --clean

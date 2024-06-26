# Copyright (c) 2024, FeitengLi(lifeiteng0422@gmail.com).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This file contains functions for make TextGrid-format subtitle files based on the generated alignment.
"""

import os
import soundfile as sf
from praatio import textgrid


from utils.data_prep import Segment, Word


def make_tgt_files(
    utt_obj,
    output_dir_root,
    tgt_file_config,
):
    # don't try to make files if utt_obj.segments_and_tokens is empty, which will happen
    # in the case of the ground truth text being empty or the number of tokens being too large vs audio duration
    if not utt_obj.segments_and_tokens:
        return utt_obj

    # get duration of the utterance, so we know the final timestamp of the final set of subtitles,
    # which we will keep showing until the end
    with sf.SoundFile(utt_obj.audio_filepath) as f:
        audio_dur = f.frames / f.samplerate

    utt_obj = make_sgement_and_word_level_tgt_file(utt_obj, output_dir_root, tgt_file_config, audio_dur)

    return utt_obj


def make_sgement_and_word_level_tgt_file(utt_obj, output_dir_root, tgt_file_config, audio_dur):
    output_dir = os.path.join(output_dir_root, "tgt", "segments_and_words")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{utt_obj.utt_id}.TextGrid")

    segments, words = [], []
    for segment_or_token in utt_obj.segments_and_tokens:

        if type(segment_or_token) is Segment:
            segment = segment_or_token

            words_in_segment = []
            for word_or_token in segment.words_and_tokens:
                if type(word_or_token) is Word:
                    words_in_segment.append(word_or_token)

            segments.append((words_in_segment[0].t_start, words_in_segment[-1].t_end, segment.text))
            for word in words_in_segment:
                words.append((word.t_start, word.t_end, word.text))

    tg = textgrid.Textgrid()
    segmentTier = textgrid.IntervalTier('segments', segments)
    wordTier = textgrid.IntervalTier('words', words)

    tg.addTier(segmentTier)
    tg.addTier(wordTier)
    tg.save(output_file, format="long_textgrid", includeBlankSpaces=True)

    utt_obj.saved_output_files[f"words_level_tgt_filepath"] = output_file
    return utt_obj

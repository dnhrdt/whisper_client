"""
Sentence Combiner Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 14:00 CET

Dieses Modul enthält Funktionen zur Kombination von Sätzen und Behandlung von Satzfortsetzungen.
"""

import config


def handle_sentence_continuation(sentences):
    """Behandelt Satzfortsetzungen"""
    if len(sentences) <= 1:
        return sentences

    i = len(sentences) - 1
    while i > 0:
        # Case 1: Previous sentence doesn't end with a sentence marker
        if not any(
            sentences[i - 1].endswith(marker) for marker in config.SENTENCE_END_MARKERS
        ):
            # Combine with the next sentence
            sentences[i - 1] = sentences[i - 1] + " " + sentences[i]
            sentences.pop(i)
        # Case 2: Current sentence starts with lowercase and previous ends with a period
        # This is common in mixed language texts where periods might be part of
        # abbreviations
        elif sentences[i - 1].endswith(".") and sentences[i] and sentences[i][0].islower():
            # Combine with the previous sentence
            sentences[i - 1] = sentences[i - 1] + " " + sentences[i]
            sentences.pop(i)
        # Case 3: Previous sentence ends with a period and next sentence starts with 'Y'
        # or other connectors
        # This is common in mixed language texts
        elif (
            sentences[i - 1].endswith(".")
            and sentences[i]
            and sentences[i].startswith(("Y ", "y ", "And ", "and "))
        ):
            # Combine with the previous sentence
            sentences[i - 1] = sentences[i - 1] + " " + sentences[i]
            sentences.pop(i)
        i -= 1

    return sentences


def should_combine_sentences(sentence1, sentence2):
    """Prüft, ob zwei Sätze kombiniert werden sollten"""
    # Case 1: First sentence doesn't end with a sentence marker
    if not any(sentence1.endswith(marker) for marker in config.SENTENCE_END_MARKERS):
        return True

    # Case 2: Second sentence starts with lowercase and first ends with a period
    if sentence1.endswith(".") and sentence2 and sentence2[0].islower():
        return True

    # Case 3: First sentence ends with a period and second starts with a connector
    if (
        sentence1.endswith(".")
        and sentence2
        and sentence2.startswith(("Y ", "y ", "And ", "and "))
    ):
        return True

    return False

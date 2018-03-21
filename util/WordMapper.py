import itertools
import json

from fastText import load_model
import keras.backend as K
import numpy as np
from keras.utils.np_utils import to_categorical
from util.standardization import standardization

class WordMapper:
    """
    A word mapper associates a vector in a semantic space to every word.

    Args:
        labels_list_ner_path (str): Path of the file containing the possible labels.
        embeddings_path (str): Path to the FastText model.

    Attributes:
        num_labels_ner (int): Number of labels in the list of labels.
        word_vectors_len (int): Dimension of the vectors representing each word.
    """

    def __init__(self, labels_list_ner_path, embeddings_path=None):
        # build iobs list
        self._labels_values_ner = WordMapper.create_iob_list(labels_list_ner_path)
        self._labels_indices_ner = {l: i for i, l in enumerate(self._labels_values_ner)}
        self.num_labels_ner = len(self._labels_values_ner)
        if embeddings_path is not None:
            # load fasttext embedding
            self._fasttext_model = load_model(embeddings_path)
            self.word_vectors_len = self._fasttext_model.get_dimension()
        else:
            self.word_vectors_len = 100

    def get_label_ner_for_index(self, label_index):
        return self._labels_values_ner[label_index]

    def get_index_for_label_ner(self, label):
        return self._labels_indices_ner[label]

    def get_word_vector(self, word):
        """
        Abstract method. Retrieves the input of the network for a given word.

        Returns:
            word_vector is the corresponding vector in the model.
        """
        try:
            ##words are lower and standardized in model

            ##ici, aucun fasttest model
            return self._fasttext_model.get_word_vector(standardization(word))
        except AttributeError:
            return None

    def samples_to_batch(self, samples, max_sentence_len):
        """
        Turns a bunch of samples to a batch.

        Returns:
            tuple: Tuple (inputs, outputs) which can be fed to the network.
        """
        frozen_word_vecs = np.zeros((len(samples), max_sentence_len, self.word_vectors_len), dtype=K.floatx())
        labels_ner = np.zeros((len(samples), max_sentence_len, len(self._labels_values_ner)), dtype=K.floatx())
        for i, sample in enumerate(samples):
            for j, word in enumerate(sample.sentence[:max_sentence_len]):
                frozen_vec = self.get_word_vector(word)
                frozen_word_vecs[i, j, :] = frozen_vec
            labels_ner[i, :min(len(sample.sentence), max_sentence_len), :] = to_categorical(
                [self.get_index_for_label_ner(l) for l in sample.label_ner[:max_sentence_len]],
                num_classes=len(self._labels_values_ner))
        return frozen_word_vecs, labels_ner

    @staticmethod
    def create_iob_list(labels_path):
        with open(labels_path, 'r') as f:
            l = json.load(f)
            return ['O'] + list(itertools.chain.from_iterable(('B-' + t, 'I-' + t) for t in l))

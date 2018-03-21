import string
import numpy as np
from util.abstract_tokens_dico import abstract_tokens_dico
from util.standardization import standardization

class Sample:
    """
    Class representing a labelled sample of the src.

    Args:
        p_sentence (list of str): Tokens of the sentence.
        p_label_ner (list of str): Label of each token.
    """

    def __init__(self, p_sentence, p_label_ner, p_intent=None, p_simple_iob=False):

        self.sentence = [standardization(word) for word in p_sentence]
        if p_simple_iob:
            self.label_ner, error = abstract_tokens_dico(p_label_ner[0])
            if error :
                print(self.sentence)
        else :
            self.label_ner = p_label_ner

        self.intent = p_intent

        # Would be better as class attributes, but can't set static method from class attributes
        self.MUTATION_TYPES = [None, Sample.sample_insert_random_unk, Sample.sample_replace_random_unk]
        #self.MUTATION_PROBABILITY = [dataset_config['mutation']['none'],
        #                             dataset_config['mutation']['insert'], dataset_config['mutation']['replace']]

    def display(self):
        print('intent is: ', self.intent)
        for i in range(len(self.sentence)):
            print(self.sentence[i].rjust(25), '<>', self.label_ner[i])

    def mutate(self):
        mutation = np.random.choice(self.MUTATION_TYPES, p=self.MUTATION_PROBABILITY)
        while mutation is not None:
            mutation(self)
            mutation = np.random.choice(self.MUTATION_TYPES, p=self.MUTATION_PROBABILITY)

    @staticmethod
    def sample_insert_random_unk(p_sample):
        """
        Messes with a sample inserting an UNK token at a random position before the beginning of a BIO group.
        Args:
            p_sample (Sample): Sample (will be modified in-place).
        """
        # on génère une suite de 12 lettres
        unk_word = ''.join(np.random.choice(list(string.ascii_letters), 12))
        # on insère juste avant un begining
        possible_positions = [i for i, l in enumerate(p_sample.label_ner) if l.startswith('B-')]
        if possible_positions :
            position = np.random.choice(possible_positions)
            p_sample.sentence.insert(position, unk_word)
            p_sample.label_ner.insert(position, 'O')
        else :
            print(p_sample.sentence, p_sample.label_ner)

    @staticmethod
    def sample_replace_random_unk(p_sample):
        """
        Messes with a sample replacing a random token with an UNK token but keeping the same label.

        Args:
            p_sample (Sample): Sample (will be modified in-place).
        """
        unk_word = ''.join(np.random.choice(list(string.ascii_letters), 12))
        position = np.random.choice(len(p_sample.sentence))
        p_sample.sentence[position] = unk_word



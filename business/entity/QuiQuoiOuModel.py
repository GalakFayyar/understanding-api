import json
from keras.models import model_from_json
import numpy as np
from util.WordMapper import WordMapper
from util.Sample import Sample
from business.entity.EntityPrediction import EntityPrediction
from util.decode_bio import decode_bio
from fastText import load_model
import re

MAX_SENTENCE_LEN = 24

EntityMap = {"metier": "quoi", "attribut": "quoi", "pro": "qui", "localite": "ou", "proximite": "prox"}


class QuiQuoiOuModel:
    def __init__(self):
        super().__init__()
        self.name = __class__.__name__
        self.modele = None
        self.modele_proximite = None
        self.word_mapper = None

    def load_model(self, p_modele_json: str, p_modele_poids: str) -> None:
        json_data = open(p_modele_json)
        data = json.load(json_data)
        self.modele = model_from_json(json.dumps(data))
        self.modele.load_weights(p_modele_poids)
        self.word_mapper = WordMapper("data/labels_100.json", "data/model_100.bin")
        self.modele_proximite = load_model("data/modelProx.bin")

    @staticmethod
    def prediction_to_sentence_labels_probabilitis(p_labels, p_seqlens):
        # keep 2 choices of the network
        probabilities = np.sort(p_labels)[:, :, -2:]
        predictions = np.argsort(p_labels, -1)[:, :, -2:]
        predictions = [l[:seqlen] for l, seqlen in zip(predictions, p_seqlens)]
        return predictions, probabilities

    def get_batch(self, p_text):
        tokens = p_text.split(' ')
        dummy_labels = ['O'] * len(tokens)
        samples = [Sample(tokens, dummy_labels)]
        batch = self.word_mapper.samples_to_batch(samples, MAX_SENTENCE_LEN)[0]
        return batch

    def get_prediction(self, p_text):
        tokens = p_text.split(' ')
        batch = self.get_batch(p_text)
        labels = self.modele.predict(batch)
        labels_ner = np.argmax(labels[0], axis=-1)
        prediction_ner = list(map(self.word_mapper.get_label_ner_for_index, labels_ner))
        prediction = decode_bio(tokens, prediction_ner)
        return prediction

    def get_predictions_ner(self, p_text):
        tokens = p_text.split(' ')
        batch = self.get_batch(p_text)
        labels = self.modele.predict(batch)
        mask = np.logical_or.reduce(batch != 0, axis=2)
        seqlens = [len(np.trim_zeros(row, trim='b')) for row in mask]
        predictions, probabilities = self.prediction_to_sentence_labels_probabilitis(labels, seqlens)
        predictions_ner = []
        for pred, prob, tok in zip(predictions[0], probabilities[0], tokens):
            prediction_ner = {
                "token": tok,
                "p1": self.word_mapper.get_label_ner_for_index(pred[1]),
                "p1_score": prob[1],
                "p2": self.word_mapper.get_label_ner_for_index(pred[0]),
                "p2_score": prob[0]
            }
            predictions_ner.append(prediction_ner)
        return predictions_ner

    @staticmethod
    def get_pattern_from_predictions_ner(p_predictions_ner):
        p1, p2, pattern = "", "", ""
        for pred in p_predictions_ner:
            p1 += pred["token"] + ":" + pred["p1"] + ":" + str(round(pred["p1_score"], 2)) + " "
            p2 += pred["token"] + ":" + pred["p2"] + ":" + str(round(pred["p2_score"], 2)) + " "
            pattern += pred["p1"][2:] + " " if pred["p1"] != "O" else "O "
        p1 = p1.rstrip()
        p2 = p2.rstrip()
        pattern = pattern.rstrip()
        return p1, p2, pattern

    @staticmethod
    def change_the_element_with_best_p2(p_pattern, p_prediction, p_predictions_ner):
        best_score = 0
        best_index = -1
        pattern_list = p_pattern.split(" ")
        for idx, prediction_ner in enumerate(p_predictions_ner):
            if prediction_ner["p1"] != 'O' and prediction_ner["p2_score"] > best_score and \
                    pattern_list.count(prediction_ner["p1"][2:]) > 1:
                best_score = prediction_ner["p2_score"]
                best_index = idx
        if best_index >= 0:
            if p_prediction[best_index][1] == "localite":
                p_prediction[best_index][1] = "metier"
                pattern_list[best_index] = "metier"
            else:
                p_prediction[best_index][1] = "localite"
                pattern_list[best_index] = "localite"
            p_predictions_ner[best_index]["p2_score"] = -2
        p_pattern = " ".join(pattern_list)
        return p_pattern, p_prediction, p_predictions_ner

    @staticmethod
    def fix_same_o_same(p_pattern, p_prediction, p_predictions_ner):
        pattern_list = p_pattern.split(" ")
        for idx, pred in enumerate(p_prediction):
            if pred[1] == '':
                if 0 < idx < len(p_prediction) - 1:
                    if p_prediction[idx - 1][1] == p_prediction[idx + 1][1]:
                        if idx > 1:
                            if p_prediction[idx - 2][1] != p_prediction[idx - 1][1]:
                                p_prediction[idx - 1][1] = p_prediction[idx - 2][1]
                                pattern_list[idx - 1] = p_prediction[idx - 2][1]
                                p_predictions_ner[idx - 1]["p2_score"] = 0
                        if idx < len(p_prediction) - 2:
                            if p_prediction[idx + 2][1] != p_prediction[idx + 1][1]:
                                p_prediction[idx + 1][1] = p_prediction[idx + 2][1]
                                pattern_list[idx + 1] = p_prediction[idx + 2][1]
                                p_predictions_ner[idx + 1]["p2_score"] = 0
        p_pattern = " ".join(pattern_list)
        return p_pattern, p_prediction, p_predictions_ner

    def fix_bad_regexp_pattern(self, p_pattern, p_prediction, p_predictions_ner, p_max_retry=10):
        previous_prediction = p_prediction
        while p_max_retry >= 0 and re.search("localite proximite|metier.*localite.*metier|localite.*metier.*localite", p_pattern) is not None:
            p_pattern, p_prediction, p_predictions_ner = self.change_the_element_with_best_p2(p_pattern, p_prediction, p_predictions_ner)
            p_max_retry -= 1
        if p_max_retry == 0:
            p_prediction = previous_prediction
        return p_pattern, p_prediction, p_predictions_ner

    def redressage_pattern(self, p_pattern, p_prediction, p_predictions_ner):
        # If the pattern cointain only localite or only metier
        # It change the localite/metier with the highest second score
        if (p_pattern.find("localite") == -1 and p_pattern.find("metier") >= 0) or (p_pattern.find("metier") == -1 and p_pattern.find("localite") >= 0):
            p_pattern, p_prediction, p_predictions_ner = self.change_the_element_with_best_p2(p_pattern, p_prediction, p_predictions_ner)
        # If the pattern localite O localite or metier O metier is found,
        # it changes it to metier O localite or localite O metier
        p_pattern, p_prediction, p_predictions_ner = self.fix_same_o_same(p_pattern, p_prediction, p_predictions_ner)
        # While the bad pattern is found and max_retry > 0
        # It change the localite/metier with the highest second score
        p_pattern, p_prediction, p_predictions_ner = self.fix_bad_regexp_pattern(p_pattern, p_prediction, p_predictions_ner)
        return p_prediction, p_pattern

    @staticmethod
    def get_final_prediction(p_prediction):
        qui_quoi_ou = {"qui": "", "quoi": "", "ou": "", "prox": ""}
        for element in p_prediction:
            if EntityMap.get(element[1]):
                if not qui_quoi_ou[EntityMap.get(element[1])]:
                    qui_quoi_ou[EntityMap.get(element[1])] = element[0]
                else:
                    qui_quoi_ou[EntityMap.get(element[1])] = qui_quoi_ou[EntityMap.get(element[1])] + ' ' + element[0]
        qui_quoi_ou["prox"] = True if len(qui_quoi_ou["prox"]) > 0 else False
        return qui_quoi_ou

    def predict(self, p_text: str, p_redressage_activated: bool) -> EntityPrediction:
        analyse = {"phrase": p_text, "p1": "", "p2": "", "pattern": ""}

        prediction = self.get_prediction(p_text)
        predictions_ner = self.get_predictions_ner(p_text)

        # get the p1,p2 and the str pattern for the given p_text (str pattern : metier O localité)
        analyse["p1"], analyse["p2"], analyse["pattern"] = self.get_pattern_from_predictions_ner(predictions_ner)

        # If redressage is activate and pattern contains less than 5 words
        if p_redressage_activated and len(analyse["pattern"].split(" ")) < 6:
            prediction, analyse["pattern"] = self.redressage_pattern(analyse["pattern"], prediction, predictions_ner)
        qui_quoi_ou = self.get_final_prediction(prediction)

        return EntityPrediction(p_qui=qui_quoi_ou["qui"], p_quoi=qui_quoi_ou["quoi"],
                                p_ou=qui_quoi_ou["ou"], p_proximite=qui_quoi_ou["prox"], p_analyse=analyse)

    def get_name(self) -> str:
        return self.name

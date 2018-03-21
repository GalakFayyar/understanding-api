
class EntityPrediction:

    def __init__(self, p_qui, p_quoi, p_ou, p_proximite, p_analyse):
        self.qui = p_qui
        self.quoi = p_quoi
        self.ou = p_ou
        self.proximite = p_proximite
        self.analyse = p_analyse

    def to_dict(self):
        return dict(
            qui=self.qui,
            quoi=self.quoi,
            ou=self.ou,
            proximite=self.proximite,
            analyse=self.analyse
        )

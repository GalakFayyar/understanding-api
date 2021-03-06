"""
Abstract Token Dico
translate complex IOB to simple

"""
def abstract_tokens_dico(phrase: str) -> str:
    translate = {
        'B-date.heure': 'B-date',
        'B-date.heure_relative': 'B-date',
        'B-date.jour': 'B-date',
        'B-date.mois': 'B-date',
        'B-date.moment_du_jour': 'B-date',
        'B-date.relative': 'B-date',
        'B-attribut': 'B-attribut',
        'B-attribut#hebergement': 'B-attribut',
        'B-attribut#ouverture': 'B-attribut',
        'B-attribut#restauration': 'B-attribut',
        'B-avis': 'B-attribut',
        'B-tarif': 'B-attribut',
        'B-arrondissement': 'B-localite',
        'B-departement_code': 'B-localite',
        'B-departement_nom': 'B-localite',
        'B-localisation': 'B-localite',
        'B-localite': 'B-localite',
        'B-poi': 'B-localite',
        'B-proximite': 'B-localite',
        'B-region': 'B-localite',
        'B-voie': 'B-localite',
        'B-metier': 'B-metier',
        'B-metier#pascher': 'B-metier',
        'B-metier#un': 'B-metier',
        'B-metier#une': 'B-metier',
        'B-metier.habitat': 'B-metier',
        'B-metier.hebergement': 'B-metier',
        'B-metier.hebergement#un': 'B-metier',
        'B-metier.hebergement#une': 'B-metier',
        'B-metier.restauration': 'B-metier',
        'B-metier.restauration#un': 'B-metier',
        'B-metier.restauration#une': 'B-metier',
        'B-metier.sante': 'B-metier',
        'B-metier.sante#un': 'B-metier',
        'B-metier.sante#une': 'B-metier',
        'B-number': 'B-metier',
        'B-possessifmetier': 'B-metier',
        'B-produit': 'B-metier',
        'B-produit.restauration': 'B-metier',
        'B-produit.restauration#un': 'B-metier',
        'B-produit.restauration#une': 'B-metier',
        'B-produit.service.public': 'B-metier',
        'B-produit.service.public#ma': 'B-metier',
        'B-produit.service.public#un': 'B-metier',
        'B-produit.service.public#une': 'B-metier',
        'B-service.public': 'B-metier',
        'B-service.public#dela': 'B-metier',
        'B-service.public#du': 'B-metier',
        'B-service.public#la': 'B-metier',
        'B-service.public#le': 'B-metier',
        'B-pro': 'B-pro',
        'B-pro#hebergement': 'B-pro',
        'B-pro#restauration': 'B-pro',
        'B-pro#sante': 'B-pro',
        'I-date.heure': 'B-date',
        'I-date.heure_relative': 'B-date',
        'I-date.jour': 'B-date',
        'I-date.mois': 'B-date',
        'I-date.moment_du_jour': 'B-date',
        'I-date.relative': 'B-date',
        'I-attribut': 'B-attribut',
        'I-attribut#hebergement': 'B-attribut',
        'I-attribut#ouverture': 'B-attribut',
        'I-attribut#restauration': 'B-attribut',
        'I-avis': 'B-attribut',
        'I-tarif': 'B-attribut',
        'I-arrondissement': 'B-localite',
        'I-departement_code': 'B-localite',
        'I-departement_nom': 'B-localite',
        'I-localisation': 'B-localite',
        'I-localite': 'B-localite',
        'I-poi': 'B-localite',
        'I-proximite': 'B-localite',
        'I-region': 'B-localite',
        'I-voie': 'B-localite',
        'I-metier': 'B-metier',
        'I-metier#pascher': 'B-metier',
        'I-metier#un': 'B-metier',
        'I-metier#une': 'B-metier',
        'I-metier.habitat': 'B-metier',
        'I-metier.hebergement': 'B-metier',
        'I-metier.hebergement#un': 'B-metier',
        'I-metier.hebergement#une': 'B-metier',
        'I-metier.restauration': 'B-metier',
        'I-metier.restauration#un': 'B-metier',
        'I-metier.restauration#une': 'B-metier',
        'I-metier.sante': 'B-metier',
        'I-metier.sante#un': 'B-metier',
        'I-metier.sante#une': 'B-metier',
        'I-number': 'B-metier',
        'I-possessifmetier': 'B-metier',
        'I-produit': 'B-metier',
        'I-produit.restauration': 'B-metier',
        'I-produit.restauration#un': 'B-metier',
        'I-produit.restauration#une': 'B-metier',
        'I-produit.service.public': 'B-metier',
        'I-produit.service.public#ma': 'B-metier',
        'I-produit.service.public#un': 'B-metier',
        'I-produit.service.public#une': 'B-metier',
        'I-service.public': 'B-metier',
        'I-service.public#dela': 'B-metier',
        'I-service.public#du': 'B-metier',
        'I-service.public#la': 'B-metier',
        'I-service.public#le': 'B-metier',
        'I-pro': 'B-pro',
        'I-pro#hebergement': 'B-pro',
        'I-pro#restauration': 'B-pro',
        'I-pro#sante': 'B-pro',
        'O':'O'
    }
    out = []
    error = False
    for tok in phrase:
        try:
            out.append(translate[tok])
        except:
            print("abstract_tokens_dico : pas de conversion pour {}".format(phrase))
            error = True
    return out, error

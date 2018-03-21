from requests import codes as http_codes
import os
from collections import OrderedDict

from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from flask_restplus import Api, Resource
from flask_restplus import abort

from commons.logger import logger, configure
from commons import configuration

# Pour charger les modèles à utiliser
from business.entity.QuiQuoiOuModel import QuiQuoiOuModel
import json

from tech.SmokeTest import SmokeTest

import traceback

# Chargement de la conf
conf = configuration.load()
script_dir = os.path.dirname(__file__)


def _init_app(p_conf):
    # Configuration du logger
    configure(p_conf['log']['level_values'][p_conf['log']['level']],
              p_conf['log']['dir'], p_conf['log']['filename'],
              p_conf['log']['max_filesize'], p_conf['log']['max_files'])

    # Load app config into Flask WSGI running instance
    r_app = Flask(__name__)
    r_app.config['API_CONF'] = p_conf

    # Autoriser le Cross-origin (CORS)
    r_app.config['CORS_HEADERS'] = 'Auth-Token, Content-Type, User, Content-Length'
    CORS(r_app, resources={r"/*": {"origins": "*"}})

    # Documentation swagger
    # L'utilisation de blueprint permet de modifier la route associée à la doc
    blueprint = Blueprint('api', __name__)
    r_swagger_api = Api(blueprint, doc='/' + p_conf['url_prefix'] + '/doc/',
                        title='API',
                        description="Api pour la detection d'entités et d'intentions")
    r_app.register_blueprint(blueprint)
    r_ns = r_swagger_api.namespace(name=p_conf['url_prefix'], description="Documentation de l'api")

    return r_app, r_swagger_api, r_ns


def _load_entity_models():
    r_entity_models = OrderedDict()

    keras = QuiQuoiOuModel()
    keras.load_model(p_modele_json='./data/model_100.json',
                     p_modele_poids='./data/weights_100.h5')
    r_entity_models[keras.get_name()] = keras

    return r_entity_models


app, swagger_api, ns = _init_app(conf)
entity_models = _load_entity_models()
meta_info = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf/meta_info.json')))

smoke = SmokeTest()


# Access log query interceptor
@app.before_request
def access_log():
    logger.info("{0} {1}".format(request.method, request.path))


@ns.route('/', strict_slashes=False)
class Base(Resource):
    @staticmethod
    def get():
        """
            Base route
        """
        response = meta_info

        return make_reponse(response, 200)


@ns.route('/heartbeat')
class Heart(Resource):
    @staticmethod
    def get():
        """
            Heartbeat
            Est-ce que l'api est en vie ?
        """
        response = {
            'status_code': 200,
            'message': 'Heartbeat'
        }

        return _success(response)


@ns.route("/supervision")
class Supervision(Resource):
    @staticmethod
    def get():
        """
            Retourne la configuration de l'api
        """
        response = None
        try:
            response = app.config['API_CONF']
        except Exception:
            abort(http_codes.SERVER_ERROR, "Erreur interne lors de la récupération de la configuration")

        return _success(response)


@ns.route("/smokeTest")
class SmokeTest(Resource):
    @staticmethod
    def get():
        """
            SmokeTest
        """
        response = None
        try:
            response = smoke.get_results(entity_models, intent_models)
        except Exception:
            abort(http_codes.SERVER_ERROR, "Erreur interne lors de la récupération des modèles")

        return _success(response)

# Doc de la route /quiquoiou?phrase=<phrase>


quiquoi_parser = swagger_api.parser()
quiquoi_parser.add_argument(name='phrase', required=True, type=str, help="La phrase à analyser")
quiquoi_parser.add_argument(name='redressage', required=False, type=str, help="Active le redressage_pattern")


@ns.route("/quiquoiou", endpoint="/quiquoiou")
@swagger_api.expect(quiquoi_parser)
class QuiQuoiOu(Resource):
    @staticmethod
    def get():
        """
            Retourne un Qui/Quoi/Ou/Proximité utilisable dans le cadre du portail PJ
        """

        if not entity_models:
            abort(http_codes.BAD_REQUEST, "Aucun modèle de détection d'entité n'a été chargé")

        phrase, entity_model_name, redressage_active = None, None, True
        try:
            phrase = request.args.get('phrase', None)
            redressage = request.args.get('redressage', None)
            if redressage and redressage.lower() == "false":
                redressage_active = False

            # next(iter(dictionnary)) => renvoie la 'première' clé d'un dictionnaire
            entity_model_name = request.args.get('entity_model', next(iter(entity_models)))

        except Exception:
            abort(http_codes.SERVER_ERROR, "Erreur lors du chargement du modèle")

        logger.info("Analyse de {sentence} avec le modèle {entity}".format(
            sentence=phrase, entity=entity_model_name
        ))

        entity_model = None
        try:
            entity_model = entity_models.get(entity_model_name)
        except KeyError:
            abort(http_codes.BAD_REQUEST, "Le modele de prédiction d'entité {} n'existe pas.".format(
                entity_model_name
            ))

        entity_prediction = entity_model.predict(phrase, redressage_active)
        response = {
            'qui': entity_prediction.to_dict()["qui"],
            'quoi': entity_prediction.to_dict()["quoi"],
            'ou': entity_prediction.to_dict()["ou"],
            'proximite': entity_prediction.to_dict()["proximite"],
            'analyse': entity_prediction.to_dict()["analyse"]
        }
        logger.info(response)

        return _success(response)


def _success(response):
    return make_reponse(response, http_codes.OK)


def _failure(exception, http_code=http_codes.SERVER_ERROR):
    try:
        exn = traceback.format_exc(exception)
        logger.info("EXCEPTION: {}".format(exn))
    except:
        logger.info("EXCEPTION: {}".format(exception))
    try:
        data, code = exception.to_tuple()
        return make_reponse(data, code)
    except:
        try:
            data = exception.to_dict()
            return make_reponse(data, exception.http)
        except Exception:
            return make_reponse(None, http_code)


def make_reponse(p_object=None, status_code=200):
    """
        Fabrique un objet Response à partir d'un p_object et d'un status code
    """
    if p_object is None and status_code == 404:
        p_object = {"status": {"status_content": [{"code": "404 - Not Found", "message": "Resource not found"}]}}

    json_response = jsonify(p_object)
    json_response.status_code = status_code
    json_response.content_type = 'application/json;charset=utf-8'
    json_response.headers['Cache-Control'] = 'max-age=3600'
    return json_response


if __name__ == "__main__":
    # Run http REST stack
    logger.info("Run api on {}:{}".format(conf['host'], conf['port']))
    app.run(host=conf['host'], port=int(conf['port']), debug=conf['log']['level'] == "DEBUG")

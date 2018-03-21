import collections
import logging


class SmokeTest(object):

    def __init__(self):
        self.logger = logging.getLogger('api-comprehension')

    def get_results(self, p_entity_models, p_intent_models):
        """
            Get smoke test results
        """
        main_result = collections.OrderedDict()
        main_result['resultats'] = []
        main_result['status'] = "SUCCESS"
        main_result['nbTestSuccess'] = 1
        main_result['nbTestWarning'] = 0
        main_result['nbTestError'] = 0

        test_model = collections.OrderedDict()
        test_model['name'] = "Model Tests"
        test_model['status'] = "SUCCESS"
        test_model['nbTestSuccess'] = 0
        test_model['nbTestWarning'] = 0
        test_model['nbTestError'] = 0
        test_model['cases'] = []

        # Test Existence du modele entites
        test_model_entities = self._test_model(p_entity_models, 'entites')
        if test_model_entities['status'] == "SUCCESS":
            test_model['nbTestSuccess'] += 1
        else:
            test_model['nbTestError'] += 1
            test_model['status'] = "ERROR"
        test_model['cases'].append(test_model_entities)

        # Test Existence du modele intention
        test_model_intentions = self._test_model(p_intent_models, 'intentions')
        if test_model_intentions['status'] == "SUCCESS":
            test_model['nbTestSuccess'] += 1
        else:
            test_model['nbTestError'] += 1
            test_model['status'] = "ERROR"
        test_model['cases'].append(test_model_intentions)

        # Update the global object with subtests
        main_result['nbTestSuccess'] += test_model['nbTestSuccess']
        main_result['nbTestError'] += test_model['nbTestError']
        main_result['resultats'].append(test_model)

        if main_result['nbTestError'] > 0:
            main_result['status'] = "ERROR"

        return main_result

    @staticmethod
    def _test_model(p_modele, p_nom_model):
        """
            Vérifie l'existence des modèles
            returns a caseTest object
        """
        case_test = {
            "message": "",
            "status": "SUCCESS",
            "name": "Model Existence"
        }

        if p_modele:
            case_test['message'] = "Le modele {} existe".format(p_nom_model)
        else:
            case_test['message'] = "Le modele {} n'existe pas".format(p_nom_model)
            case_test['status'] = "ERROR"

        return case_test

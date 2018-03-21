# Changelog

## Version

  - **1.5.0**
    - Amélioration du modèle de prédiction :
      - Appris avec un corpus à 50% issu de requêtes monochamp (et le reste classsique pj18)
      - Modèle avec un LSTM de dimension 300 et deux couches de dropout de 60%
    - Amélioration du redressage pattern :
      - Quand on se retrouve avec une même occurence de chaque coté d'un "O", on part du principe que c'est faux et on tente le redressage, par exemple : 
      - Metier Localite O Localite -> Metier Metier O Localite
      - Metier O Metier Localite -> Metier O Localite Localite
      - Tant que on trouve un pattern faux, on tente de le redresser, par exemple : 
        - Metier Localite Localite Metier Metier -> Metier Localite Localite Localite Metier -> Metier Localite Localite Localite Localite
    - Bridage du redressage pattern si la phrase contient plus de 5 mots
    - Correction sur le redressage, On ne génére de faux pattern du type :
        - Metier Metier Metier -> Metier Localite Metier
    
  - **1.4.1**
    - Amélioration du modèle de prédiction
      - Appris avec un corpus à 6% issu de requêtes monochamp (et le reste classsique pj18)
      - Modèle avec un LSTM de dimension 350 et deux couches de dropout de 60%
    - Création du redressage pattern : 
      - Quand un pattern ne contient que des occurences de type Metier ou de type Localite, alors l'occurence avec le plus gros doute est transformée, par exemple : 
        - Metier (O) Metier / Localite (O) Localite -> Metier (O) Localite / Localite (O) Metier
        - Metier (O) Metier (O) Metier (O) -> Localite (O) Metier (O) Metier / Metier (O) Localite (O) Metier / Metier (O) Metier (O) Localite

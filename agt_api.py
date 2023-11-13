import requests
from datetime import datetime

bdg_url = "https://portail6.agt-systemes.fr/eReference/HORANET/HTBdgRef.php"
info_url = "https://portail6.agt-systemes.fr/eReference/HORANET/modules/Badgeuse/php/tableau_hebdomadaire.php"
fiche_info_url = "https://portail6.agt-systemes.fr/eReference/HORANET/modules/Badgeuse/php/options_ereference.php"


def agt_action(action, badge_number):
    badg = badge_number + datetime.now().strftime("%Y%m%d%H%M")
    if action == "BADGER":
        badg += "30"
    elif action == "PAUSE":
        badg += "31"
    else:
        print("Action inconnue. Les actions valables sont PAUSE et BADGER")
        return 1
    req = requests.get(url=bdg_url, params={"badg": badg, "TERM": "099"})
    print(req.content)
    return 0


def get_fiche_num(badge_number):
    req = requests.post(url=fiche_info_url, data={"Badge": badge_number, "recuperation_fiche": "true"})
    json_result = req.json()
    try:
        return json_result[0]['Fiche']
    except KeyError as e:
        print("La requête a entraîné une erreur :", e)
        print("Résultat de la requête :")
        print(json_result)


def get_agt_info(badge_number, detail="week"):
    _now = datetime.now()

    signe = ""
    fiche = get_fiche_num(badge_number)
    annee = _now.strftime("%Y")
    semaine = _now.strftime("%V")
    true_str = "true"
    data = {"Signe": signe, "Fiche": fiche, "Annee": annee, "Semaine": semaine, "tableau_hebdomadaire": true_str}

    req = requests.post(url=info_url, data=data)
    json_result = req.json()

    if detail == "week":
        return json_result

    elif detail == "day":
        current_day = _now.strftime("%d/%m/%Y")
        for jour in json_result['Resultat']:
            if jour['Jour'] == current_day:
                return jour


if __name__ == "__main__":
    info = get_agt_info("0004FF589D")


from datetime import timedelta

# Time utils
def time_to_str(seconds: int):
    """
    Transforme un nombre de secondes en chaîne de carctères au format "hh:mm:ss"
    Utilisé pour l'affichage de l'heure et du tooltip
    :param seconds: int - Nombre de secondes à transformer
    :return: str - Chaîne de caractères au format "hh:mm:ss"
    """
    hrs = seconds//3600
    mins = (seconds % 3600)//60
    seconds = (seconds % 3600) % 60
    return '{:02d}'.format(hrs) + ":" + '{:02d}'.format(mins) + ":" + '{:02d}'.format(seconds)


def secs_to_mins(delta: timedelta):
    """
    Transforme un nombre de secondes en chaîne de carctères au format "mm:ss"
    Utilisé pour l'affichage de la durée des pauses
    :param delta: Un objet datetime.timedelta duquel on extrait le nombre total de secondes
    :return: str - Chaîne de caractères au format "mm:ss"
    """
    secs = int(delta.total_seconds())
    minutes = secs // 60
    secs_left = secs % 60
    return f"{'{:02d}'.format(minutes)}:{'{:02d}'.format(secs_left)}"
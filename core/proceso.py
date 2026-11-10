"""Une las piezas: toma prospectos de la base, los clasifica, los puntúa y guarda el resultado."""

from core import clasificador, db, puntaje


def clasificar_y_puntuar(ids, usar_ia=False, al_avanzar=None):
    """Procesa la lista de ids. al_avanzar(i, total, nombre) permite mostrar progreso."""
    total = len(ids)
    for i, pid in enumerate(ids, start=1):
        p = db.obtener(pid)
        if p is None:
            continue
        c = clasificador.clasificar(p, usar_ia=usar_ia)
        resultado = puntaje.calcular(p, c)
        db.actualizar(pid, **resultado)
        db.registrar_evento(pid, "Clasificado",
                            f"{resultado['metodo']}: {resultado['puntaje']} pts, prioridad {resultado['prioridad']}")
        if al_avanzar:
            al_avanzar(i, total, p["razon_social"])

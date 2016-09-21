# coding=utf-8
from survivability.utils.utils import _e2vpath


def compute_ks(scenarios, demands):
    """
    Este metodo construye la lista de demandas a rutear por escenario.
    Args:
        scenarios: Es una lista de escenarios de corte. Donde cada elemento
                   de la lista (escenario) es una lista con los inidices de
                   arco, e_ids, de aquellos arcos que están cortados. La
                   posición en la lista representa el número de escenario.

        demands: Es una lista de demandas. Cada demanda es una tupla de dos
                 elementos, donde el primero es la capacidad demandada y el
                 segundo es una lista de caminos. Estos caminos representan
                 a los caminos de working y protección dedicada del servicio.
                 [(3,[[0],[2,1]]),(2,[[23],[21,13],[45,20]]),(4,[[43]]),
                    ...,(cap,[epath0,epath1])]
    Returns:
            Ks: Es una lista que contiene las demandas que deben ser ruteadas en
            cada escenario. Es decir, cada elemento de Ks es una lista con los
            indices de aquellas demandas que fueron afectadas por el escenario
            que corresponde con la posición de la lista en Ks y que deben
            ser restauradas.

    """
    # Genero la lista de demandas que deberían ser ruteadas
    ks = []
    for g, g_list in enumerate(scenarios):
        kg = []
        for k, dem in enumerate(demands):
            cuts = 0
            for p_id, p in enumerate(dem[1]):
                for e_id in g_list:
                    if e_id in p:
                        cuts += 1
                        break
            if cuts == len(dem[1]):
                kg.append(k)
        ks.append(kg)
    return ks


def compute_kp(graph, scenarios, demands):
    """

    Args:
        graph: Un grafo de igraph que representa la topología sobre la que
               se rutean las demandas de servicio.
        scenarios: Es una lista de escenarios de corte. Donde cada elemento
                   de la lista (escenario) es una lista con los inidices de
                   arco, e_ids, de aquellos arcos que están cortados. La
                   posición en la lista representa el número de escenario.
        demands: Es una lista de demandas. Cada demanda es una tupla de dos
                 elementos, donde el primero es la capacidad demandada y el
                 segundo es una lista de caminos. Estos caminos representan
                 a los caminos de working y protección dedicada del servicio.
                 [(3,[[0],[2,1]]),(2,[[23],[21,13],[45,20]]),(4,[[43]]),
                    ...,(cap,[epath0,epath1])]

    Returns:
        Kp: Es una lista que contiene las demandas que pueden ser ruteadas en
            cada escenario. Es decir cada elemento de Kp es una lista con
            los indices de las demandas que tiene al menos 1 camino en el
            escenario que corresponde con la psoción de la lista en Kp.

    """
    # Creacion de listas origen y destino para cada demanda.
    s = []
    d = []
    for dem in demands:
        vpath = _e2vpath(graph, dem[1][0])
        s.append(vpath[0])
        d.append(vpath[-1])

    # Genero lista de demandas que tienen al menos un camino disponible por
    # subgrafo
    Kp = []
    for cuts in scenarios:
        Kp.append([])
        g2 = graph.copy()
        g2.delete_edges(cuts)
        for i, source in enumerate(s):
            res = g2.get_all_shortest_paths(source, to=d[i], mode=3)
            if res:
                Kp[-1].append(i)

    return Kp


def compute_sp(scenarios, demands, inst_s):
    """

    Args:
        scenarios: Es una lista de escenarios de corte. Donde cada elemento
                   de la lista (escenario) es una lista con los inidices de
                   arco, e_ids, de aquellos arcos que están cortados. La
                   posición en la lista representa el número de escenario.
        demands: Es una lista de demandas. Cada demanda es una tupla de dos
                 elementos, donde el primero es la capacidad demandada y el
                 segundo es una lista de caminos. Estos caminos representan
                 a los caminos de working y protección dedicada del servicio.
                 [(3,[[0],[2,1]]),(2,[[23],[21,13],[45,20]]),(4,[[43]]),
                    ...,(cap,[epath0,epath1])]
        inst_s: Representa a la capacidad spare pre-instalada. Puede ser una
                lista o un label para un atributo de los arcos del grafo.

    Returns:
        Sp: Es una lista que contiene las capacidades disponibles en cada arco
            para cada escenario. Es decir que Sp tiene un elemento por
            escenario. Cada elemento de Sp es una lista de longitud
            len(graph.es) que contiene las capacidades disponibles (remanente
            + liberadas por servicios)
    """
    # Generación de la lista Sp
    sp =[]
    for g, g_list in enumerate(scenarios):
        sg = inst_s[:]
        for k, dem in enumerate(demands):
            for p_id, p in enumerate(dem[1]):
                for e_id in g_list:
                    if e_id in p:
                        for e_id in p:
                            sg[e_id] += dem[0]
        sp.append(sg)
    return sp


def compute_sides(graph, demands):
    """

    Args:
        graph: Un grafo de igraph que representa la topología sobre la que
               se rutean las demandas de servicio.
        demands: Es una lista de demandas. Cada demanda es una tupla de dos
                 elementos, donde el primero es la capacidad demandada y el
                 segundo es una lista de caminos. Estos caminos representan
                 a los caminos de working y protección dedicada del servicio.
                 [(3,[[0],[2,1]]),(2,[[23],[21,13],[45,20]]),(4,[[43]]),
                    ...,(cap,[epath0,epath1])]
    Returns:
        s:  Es una lista ordenada de los origenes de las demandas.
        d:  Es una lista ordenada de los destinos de las demandas.
    """
    # Creacion de listas origen y destino para cada demanda.
    s = []
    d = []
    for dem in demands:
        vpath = _e2vpath(graph, dem[1][0])
        s.append(vpath[0])
        d.append(vpath[-1])
    return s, d


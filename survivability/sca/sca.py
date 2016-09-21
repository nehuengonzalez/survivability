# coding=utf-8

from pulp import *
from survivability.preproc.compute import *


def sca_lp(graph, scenarios, demands, inst_s='s', e_avoid='avoid'
           , e_cost='weight', instance_name="NN"):
    """
    Este método crea una instancia de problema de spare capacity allocation
    para un esquema de restauración. En las demandas solo deben incluirse
    aquellas que requieran restauración.

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
        inst_s: Representa a la capacidad spare pre-instalada. Puede ser una
                lista o un label para un atributo de los arcos del grafo.
        e_avoid: Representa a la posibilidad de instalar nueva capacidad en
                 cada arco (True si está permitido y False en caso contrario).
                 Puede ser una lista o un label para un atributo de los arcos
                 del grafo.
        e_cost: Representa el costo de instalar una unidad de capacidad en cada
                arco. Puede ser una lista o un label para un atributo de los
                arcos del grafo.
        instance_name: El nombre de la instancia.

    Returns: Una instancia de pulp.LpProblem que contiene la instancia del
             problema de SCA sin resolver.

    """

    graph = graph.copy()  # Copiar el grafo.

    if isinstance(inst_s, str):
        inst_s = graph.es[inst_s]

    if isinstance(e_avoid, str):
        e_avoid = graph.es[e_avoid]

    if isinstance(e_cost, str):
        e_cost = graph.es[e_cost]

    # Pre-procesamiento
    kp = compute_kp(graph, scenarios, demands)
    ks = compute_ks(graph, demands)
    sp = compute_sp(scenarios, demands, inst_s)
    sources, destinations = compute_sides(graph, demands)

    # Creación de la instancia
    prob = LpProblem("SCA instance: %s" % instance_name, LpMinimize)

    # Capacidad necesaria de instalar total
    s_total = LpVariable("Total spare capacity", lowBound=0, cat=LpInteger)

    # Variables de flujo
    x_combs = []
    for g, g_list in enumerate(scenarios):
        for k in [ki for ki in kp[g] if ki in ks[g]]:
            for e_id, e in [(e_i, ed) for (e_i, ed) in list(enumerate(graph.es)) if e_i not in g_list]:
                x_combs.append((k, g, e.source, e.target, e_id))
                x_combs.append((k, g, e.target, e.source, e_id))

    x = LpVariable.dicts("flow variables x(k,g,i,j,e)", x_combs, lowBound=0, upBound=1, cat=LpInteger)

    # Variables de capacidad necesaria a instalar
    cs_combs = [e_id for e_id in range(len(graph.es))]

    s = LpVariable.dicts("spare capacity s(e)", cs_combs, lowBound=0, cat=LpInteger)

    # Variables de capacidad utilizada por arco por escenario
    cg_combs = []
    for g, g_list in enumerate(scenarios):
        for e_id in [e_i for e_i in range(len(graph.es)) if e_i not in g_list]:
            cg_combs.append((g, e_id))

    cg = LpVariable.dicts("graph capacities c(g,e)", cg_combs, lowBound=0, cat=LpInteger)

    # Función objetivo (1)
    prob += s_total

    # Restriccion de continuidad de los caminos  (2)
    r = 0
    for g, g_list in enumerate(scenarios):
        for k in [ki for ki in kp[g] if ki in ks[g]]:

            for i in range(len(graph.vs)):
                restr = ""
                for e_id, e in [(e_i, ed) for (e_i, ed) in list(enumerate(graph.es)) if e_i not in g_list]:
                    if e.source == i:
                        restr += " + x[(%d,%d,%d,%d,%d)]" % (k, g, i, e.target, e_id)
                        restr += " - x[(%d,%d,%d,%d,%d)]" % (k, g, e.target, i, e_id)
                    elif e.target == i:
                        restr += " + x[(%d,%d,%d,%d,%d)]" % (k, g, i, e.source, e_id)
                        restr += " - x[(%d,%d,%d,%d,%d)]" % (k, g, e.source, i, e_id)
                if restr:

                    if i == sources[k]:
                        restr += " == 1"
                    elif i == destinations[k]:
                        restr += " == -1"
                    else:
                        restr += " == 0"
                    prob += eval(restr)

    # Capacidad necesaria por subgrafo (5)
    for g, g_list in enumerate(scenarios):
        for e_id, e in [(e_i, ed) for (e_i, ed) in list(enumerate(graph.es)) if e_i not in g_list]:

            restr = ""
            for k in [ki for ki in kp[g] if ki in ks[g]]:
                restr += " + %d * x[(%d,%d,%d,%d,%d)]" % (demands[k][0], k, g, e.source, e.target, e_id)
                restr += " + %d * x[(%d,%d,%d,%d,%d)]" % (demands[k][0], k, g, e.target, e.source, e_id)

            restr += " - cg[(%d,%d)] == 0" % (g, e_id)
            prob += eval(restr)

    # Capacidad necesaria por arco por escenario (6)
    for g, g_list in enumerate(scenarios):
        for e_id, e in [(e_i, ed) for (e_i, ed) in list(enumerate(graph.es)) if e_i not in g_list]:
            prob += cg[(g, e_id)] - s[e_id] <= sp[g][e_id]

    # No crecer en este arco (7)
    for e_id, e in enumerate(graph.es):
        if e_avoid[e_id]:
            prob += s[e_id] == 0

    # Relacion entre s y los sije (es la suma de todos) (8)
    prob += s_total + sum([- e_cost[e_id] * s[e_id] for (e_id, e) in enumerate(graph.es)]) == 0, "c%d" % (r)

    # Restriccion que elimina bucles simples (3)
    for g, g_list in enumerate(scenarios):
        for e_id, e in [(e_i, ed) for (e_i, ed) in list(enumerate(graph.es)) if e_i not in g_list]:
            for k in [ki for ki in kp[g] if ki in ks[g]]:
                prob += x[(k, g, e.source, e.target, e_id)] + x[(k, g, e.target, e.source, e_id)] <= 1

    # Restriccion que elimina los posible bucles ocaiconados por arcos multiples (3 bis)
    for (e_id, e) in enumerate(graph.es):
        for e_id2 in range(e_id + 1, len(graph.es)):
            sd = [graph.es[e_id2].source, graph.es[e_id2].target]
            if (e.source in sd) and (e.target in sd):
                for g in range(len(scenarios)):
                    for k in [ki for ki in kp[g] if ki in ks[g]]:
                        prob += x[(k, g, e.source, e.target, e_id)] + x[(k, g, e.target, e.source, e_id)] + x[
                            (k, g, e.source, e.target, e_id2)] + x[(k, g, e.target, e.source, e_id2)] <= 1

    return prob






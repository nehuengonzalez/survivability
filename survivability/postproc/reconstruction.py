# coding=utf-8

from survivability.utils.utils import _e2vpath


def path_reconstruction(graph, variables, ei_index):
    epsilon = 0.0000001
    eids = []
    for var in variables:
        if var.varValue > epsilon:
            s = var.name
            s = s[s.find('_(') + 2:-1]
            s = s.split(",_")
            s = [int(si) for si in s]
            eids.append(s[ei_index])
    epath = [eids[0]]
    eids = eids[1:]
    while len(eids) != 0:
        vpath = _e2vpath(graph, epath)
        is_good = False
        for ei in eids:
            if (graph.es[ei].source == vpath[0]
                    or graph.es[ei].target == vpath[0]):
                epath = [ei] + epath
                eids.remove(ei)
                is_good = True
                break
            if (graph.es[ei].source == vpath[-1]
                or graph.es[ei].target == vpath[-1]):
                epath = epath + [ei]
                eids.remove(ei)
                is_good = True
                break
        if not is_good:
            raise IndexError("Not valid epath")
    return epath


def paths_reconstruction(graph, variables, ei_index, dem_index):
    vars_k = {}
    for var in variables:
        s = var.name
        s = s[s.find('_(') + 2:-1]
        s = s.split(",_")
        s = [int(si) for si in s]
        if not vars_k.get(s[dem_index]):
            vars_k[s[dem_index]] = []
        vars_k[s[dem_index]].append(var)
    paths = [[]] * len(vars_k)
    for k in vars_k:
        epath = path_reconstruction(graph, vars_k[k], ei_index)
        paths[k] = epath[:]
    return paths


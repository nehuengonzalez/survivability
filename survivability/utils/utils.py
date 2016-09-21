# coding=utf-8


def _e2vpath(graph, epath, v=None):
    """
    Toma un camino en formato de secuencia de indices de arcos (epath) y
    devuelve un camino en formato de secuencia de indices de vertices (vpath).
    Al pasar al formato vpath se pierde informacion de caminos que pasan por
    vertices conectados por múltiples arcos.
    """
    vpath = []

    if len(epath) == 0:
        return []
    elif v is not None:
        vpath.append(v)
        if v in ([graph.es[epath[-1]].source, graph.es[epath[-1]].target]):
            epath = epath[::-1]
    elif len(epath) > 1:
        if graph.es[epath[0]].source in ([graph.es[epath[1]].source
                                             , graph.es[epath[1]].target]):
            vpath.append(graph.es[epath[0]].target)
        else:
            vpath.append(graph.es[epath[0]].source)
    elif len(epath) == 1:
        vpath.append(graph.es[epath[0]].source)

    for eid in epath:
        if graph.es[eid].source == vpath[-1]:
            vpath.append(graph.es[eid].target)
        elif graph.es[eid].target == vpath[-1]:
            vpath.append(graph.es[eid].source)
        else:
            raise IndexError("Not valid epath")
    return vpath

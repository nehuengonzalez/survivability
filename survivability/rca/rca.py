# coding=utf-8
from pulp import *
import igraph


def online_ra(graph, s, d, weights=None, instance_name="NN"):
    """
    Online Route Assignment
    Args:
        graph: A graph that represents the logical topology
        s: source index.
        d: destination index.
        weights: A list of edge weights, a label for edge attribute or None
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    assert isinstance(graph, igraph.Graph)

    prob = LpProblem('RA instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for e_id, e in enumerate(graph.es):
        x_combs.append((e.source, e.target, e_id))
        x_combs.append((e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(i,j,e)', x_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for e_id, e in enumerate(graph.es):
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.source
                                           , e.target, e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.target
                                           , e.source, e_id)
    prob += eval(constr)


    # Flow continuity constraint
    for i in range(len(graph.vs)):
        constraint = ""
        for e_id, e in enumerate(graph.es):
            if e.source == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.target, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.target, i, e_id)
            elif e.target == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.source, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.source, i, e_id)
        if constraint:
            if i == s:
                constraint += ' == 1'
            elif i == d:
                constraint += ' == -1'
            else:
                constraint += ' == 0'
            prob += eval(constraint)

    return prob


def offline_ra(graph, s, d, weights=None, instance_name="NN"):
    """
    Offline Route Assignment
    Args:
        graph: A graph that represents the logical topology
        s: A list of source indexes.
        d: A list of destination indexes.
        weights: A list of edge weights, a label for edge attribute or None
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    assert isinstance(graph, igraph.Graph)

    prob = LpProblem('RA instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            x_combs.append((k, e.source, e.target, e_id))
            x_combs.append((k, e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(k,i,j,e)', x_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.source
                                                  , e.target, e_id)
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.target
                                                  , e.source, e_id)
    prob += eval(constr)

    # Flow continuity constraint
    for k in range(len(s)):
        for i in range(len(graph.vs)):
            constraint = ""
            for e_id, e in enumerate(graph.es):
                if e.source == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.target
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.target, i
                                                           , e_id)
                elif e.target == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.source
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.source, i
                                                           , e_id)
            if constraint:
                if i == s[k]:
                    constraint += ' == 1'
                elif i == d[k]:
                    constraint += ' == -1'
                else:
                    constraint += ' == 0'
                prob += eval(constraint)

    return prob


def online_rca(graph, s, d, c, weights=None, spare=None, instance_name="NN"):
    """
    Online Route and Capacity Assignment
    Args:
        graph: A graph that represents the logical topology
        s: source index.
        d: destination index.
        c: capacities demanded
        weights: A list of edge weights, a label for edge attribute or None
        spare: A list of edge spare capacity, a label for edge attribute
               or None (No capacity constraint)
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    assert isinstance(graph, igraph.Graph)

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    if isinstance(spare, str):
        sp = graph.es[spare][:]
    elif isinstance(spare, list):
        sp = spare[:]
    else:
        sp = [c] * len(graph.es)

    prob = LpProblem('OnRCA instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for e_id, e in enumerate(graph.es):
        x_combs.append((e.source, e.target, e_id))
        x_combs.append((e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(i,j,e)', x_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for e_id, e in enumerate(graph.es):
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.source, e.target
                                           , e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.target, e.source
                                           , e_id)
    prob += eval(constr)

    # Flow continuity constraint
    for i in range(len(graph.vs)):
        constraint = ""
        for e_id, e in enumerate(graph.es):
            if e.source == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.target, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.target, i, e_id)
            elif e.target == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.source, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.source, i, e_id)
        if constraint:
            if i == s:
                constraint += ' == 1'
            elif i == d:
                constraint += ' == -1'
            else:
                constraint += ' == 0'
            prob += eval(constraint)

    for e_id, e in enumerate(graph.es):
        prob += (c * x[(e.source, e.target, e_id)]
                 + c * x[(e.target, e.source, e_id)]) <= sp[e_id]

    return prob


def offline_rca(graph, s, d, c, weights=None, spare=None, instance_name="NN"):
    """
    Offline Route and Capacity Assignment
    Args:
        graph: A graph that represents the logical topology
        s: A list of source indexes.
        d: A list of destination indexes.
        c: A list of capacities demanded
        weights: A list of edge weights, a label for edge attribute or None
        spare: A list of edge spare capacity, a label for edge attribute
               or None (No capacity constraint)
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    if isinstance(spare, str):
        sp = graph.es[spare][:]
    elif isinstance(spare, list):
        sp = spare[:]
    else:
        sp = [sum(c)] * len(graph.es)

    assert isinstance(graph, igraph.Graph)

    prob = LpProblem('RA instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            x_combs.append((k, e.source, e.target, e_id))
            x_combs.append((k, e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(k,i,j,e)', x_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.source
                                                  , e.target, e_id)
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.target
                                                  , e.source, e_id)
    prob += eval(constr)

    # Flow continuity constraint
    for k in range(len(s)):
        for i in range(len(graph.vs)):
            constraint = ""
            for e_id, e in enumerate(graph.es):
                if e.source == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.target
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.target, i
                                                           , e_id)
                elif e.target == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.source
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.source, i
                                                           , e_id)
            if constraint:
                if i == s[k]:
                    constraint += ' == 1'
                elif i == d[k]:
                    constraint += ' == -1'
                else:
                    constraint += ' == 0'
                prob += eval(constraint)

    for e_id, e in enumerate(graph.es):
        constr = ""
        for k in range(len(s)):
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (c[k], k, e.source
                                                  , e.target, e_id)
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (c[k], k, e.target
                                                  , e.source, e_id)
        constr += ' <= %f' % (sp[e_id])
        prob += eval(constr)

    return prob


def online_1p1_rca(graph, s, d, c, weights=None, spare=None, instance_name="NN"):
    """
    Online 1+1 Route and Capacity Assignment
    Args:
        graph: A graph that represents the logical topology
        s: source index.
        d: destination index.
        c: capacities demanded
        weights: A list of edge weights, a label for edge attribute or None
        spare: A list of edge spare capacity, a label for edge attribute
               or None
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    assert isinstance(graph, igraph.Graph)

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    if isinstance(spare, str):
        sp = graph.es[spare][:]
    elif isinstance(spare, list):
        sp = spare[:]
    else:
        sp = [c] * len(graph.es)

    big_num = 2 * sum(weight)

    prob = LpProblem('OnRCA 1+1 instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for e_id, e in enumerate(graph.es):
        x_combs.append((e.source, e.target, e_id))
        x_combs.append((e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(i,j,e)', x_combs, lowBound=0
                         , upBound=2, cat=LpInteger)

    j_combs = []
    for e_id, e in enumerate(graph.es):
        j_combs.append((e.source, e.target, e_id))

    j = LpVariable.dicts('jointness variables j(i,j,e)', j_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for e_id, e in enumerate(graph.es):
        constr += ' + %f*j[(%d,%d,%d)]' % (big_num, e.source, e.target
                                           , e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.source, e.target
                                           , e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.target, e.source
                                           , e_id)
    prob += eval(constr)

    # Flow continuity constraint
    for i in range(len(graph.vs)):
        constraint = ""
        for e_id, e in enumerate(graph.es):
            if e.source == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.target, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.target, i, e_id)
            elif e.target == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.source, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.source, i, e_id)
        if constraint:
            if i == s:
                constraint += ' == 2'
            elif i == d:
                constraint += ' == -2'
            else:
                constraint += ' == 0'
            prob += eval(constraint)

    for e_id, e in enumerate(graph.es):
        prob += (c * x[(e.source, e.target, e_id)]
                 + c * x[(e.target, e.source, e_id)]) <= sp[e_id]

    for e_id, e in enumerate(graph.es):
        prob += (x[(e.source, e.target, e_id)]
                 + x[(e.target, e.source, e_id)]) - j[(e.source, e.target, e_id)] <= 1

    return prob


def online_1p1_rca_2(graph, s, d, c, weights=None, spare=None, instance_name="NN"):
    """
    Online 1+1 Route and Capacity Assignment
    Args:
        graph: A graph that represents the logical topology
        s: source index.
        d: destination index.
        c: capacities demanded
        weights: A list of edge weights, a label for edge attribute or None
        spare: A list of edge spare capacity, a label for edge attribute
               or None
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    assert isinstance(graph, igraph.Graph)

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    if isinstance(spare, str):
        sp = graph.es[spare][:]
    elif isinstance(spare, list):
        sp = spare[:]
    else:
        sp = [c] * len(graph.es)

    big_num = 20 * sum(weight)

    prob = LpProblem('OnRCA 1+1 instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for e_id, e in enumerate(graph.es):
        x_combs.append((e.source, e.target, e_id))
        x_combs.append((e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(i,j,e)', x_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    y_combs = []
    for e_id, e in enumerate(graph.es):
        y_combs.append((e.source, e.target, e_id))
        y_combs.append((e.target, e.source, e_id))

    y = LpVariable.dicts('flow variables y(i,j,e)', y_combs, lowBound=0
                         , upBound=1, cat=LpInteger)


    j_combs = []
    for e_id, e in enumerate(graph.es):
        j_combs.append((e.source, e.target, e_id))

    j = LpVariable.dicts('jointness variables j(i,j,e)', j_combs, lowBound=0
                         , upBound=1, cat=LpInteger)

    # Minimize sum of flow variables
    constr = ""
    for e_id, e in enumerate(graph.es):
        constr += ' + %f*j[(%d,%d,%d)]' % (big_num, e.source, e.target
                                           , e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.source, e.target
                                           , e_id)
        constr += ' + %f*x[(%d,%d,%d)]' % (weight[e_id], e.target, e.source
                                           , e_id)
        constr += ' + %f*y[(%d,%d,%d)]' % (weight[e_id], e.source, e.target
                                           , e_id)
        constr += ' + %f*y[(%d,%d,%d)]' % (weight[e_id], e.target, e.source
                                           , e_id)
    prob += eval(constr)

    # Flow continuity constraint X
    for i in range(len(graph.vs)):
        constraint = ""
        for e_id, e in enumerate(graph.es):
            if e.source == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.target, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.target, i, e_id)
            elif e.target == i:
                constraint += ' + x[(%d,%d,%d)]' % (i, e.source, e_id)
                constraint += ' - x[(%d,%d,%d)]' % (e.source, i, e_id)
        if constraint:
            if i == s:
                constraint += ' == 1'
            elif i == d:
                constraint += ' == -1'
            else:
                constraint += ' == 0'
            prob += eval(constraint)

    # Flow continuity constraint  y
    for i in range(len(graph.vs)):
        constraint = ""
        for e_id, e in enumerate(graph.es):
            if e.source == i:
                constraint += ' + y[(%d,%d,%d)]' % (i, e.target, e_id)
                constraint += ' - y[(%d,%d,%d)]' % (e.target, i, e_id)
            elif e.target == i:
                constraint += ' + y[(%d,%d,%d)]' % (i, e.source, e_id)
                constraint += ' - y[(%d,%d,%d)]' % (e.source, i, e_id)
        if constraint:
            if i == s:
                constraint += ' == 1'
            elif i == d:
                constraint += ' == -1'
            else:
                constraint += ' == 0'
            prob += eval(constraint)


    for e_id, e in enumerate(graph.es):
        prob += (c * x[(e.source, e.target, e_id)]
                 + c * x[(e.target, e.source, e_id)]
                 + c * y[(e.source, e.target, e_id)]
                 + c * y[(e.target, e.source, e_id)]) <= sp[e_id]

    for e_id, e in enumerate(graph.es):
        prob += (x[(e.source, e.target, e_id)]
                 + x[(e.target, e.source, e_id)]
                 + y[(e.source, e.target, e_id)]
                 + y[(e.target, e.source, e_id)]) - j[(e.source, e.target, e_id)] <= 1

    return prob


def offline_1p1_rca(graph, s, d, c, weights=None, spare=None, instance_name="NN"):
    """
    Offline 1+1 Route and Capacity Assignment
    Args:
        graph: A graph that represents the logical topology
        s: A list of source indexes.
        d: A list of destination indexes.
        c: A list of capacities demanded
        weights: A list of edge weights, a label for edge attribute or None
        spare: A list of edge spare capacity, a label for edge attribute
               or None (No capacity constraint)
        instance_name: a name for the instance (LPproblem)

    Returns: A Pulp LpProblem instance

    """

    if isinstance(weights, str):
        weight = graph.es[weights][:]
    elif isinstance(weights, list):
        weight = weights[:]
    else:
        weight = [1] * len(graph.es)

    if isinstance(spare, str):
        sp = graph.es[spare][:]
    elif isinstance(spare, list):
        sp = spare[:]
    else:
        sp = [sum(c)] * len(graph.es)

    assert isinstance(graph, igraph.Graph)

    B = 10. * len(s) * sum(weight)

    prob = LpProblem('RA instance: %s' % instance_name, LpMinimize)

    # Flow variables Xij
    x_combs = []
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            x_combs.append((k, e.source, e.target, e_id))
            x_combs.append((k, e.target, e.source, e_id))

    x = LpVariable.dicts('flow variables x(k,i,j,e)', x_combs, lowBound=0
                         , upBound=2, cat=LpInteger)

    j_combs = []
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            j_combs.append((k, e.source, e.target, e_id))

    j = LpVariable.dicts('jointness variables j(k,i,j,e)', j_combs, lowBound=0
                         , upBound=1, cat=LpInteger)
    # Minimize sum of flow variables
    constr = ""
    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.source
                                                  , e.target, e_id)
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (weight[e_id], k, e.target
                                                  , e.source, e_id)
            constr += ' + %f*j[(%d,%d,%d,%d)]' % (B, k, e.source, e.target
                                                  , e_id)
    prob += eval(constr)

    # Flow continuity constraint
    for k in range(len(s)):
        for i in range(len(graph.vs)):
            constraint = ""
            for e_id, e in enumerate(graph.es):
                if e.source == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.target
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.target, i
                                                           , e_id)
                elif e.target == i:
                    constraint += ' + x[(%d,%d,%d,%d)]' % (k, i, e.source
                                                           , e_id)
                    constraint += ' - x[(%d,%d,%d,%d)]' % (k, e.source, i
                                                           , e_id)
            if constraint:
                if i == s[k]:
                    constraint += ' == 1'
                elif i == d[k]:
                    constraint += ' == -1'
                else:
                    constraint += ' == 0'
                prob += eval(constraint)

    for e_id, e in enumerate(graph.es):
        constr = ""
        for k in range(len(s)):
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (c[k], k, e.source
                                                  , e.target, e_id)
            constr += ' + %f*x[(%d,%d,%d,%d)]' % (c[k], k, e.target
                                                  , e.source, e_id)
        constr += ' <= %f' % (sp[e_id])
        prob += eval(constr)

    for k in range(len(s)):
        for e_id, e in enumerate(graph.es):
            prob += j[(k, e.source, e.target, e_id)] - x[(k, e.source, e.target, e_id)] - [(k, e.target, e.source, e_id)] >= -1

    return prob


# coding=utf-8
from itertools import combinations


def multilayer_cuts(entities, entities_av, relate, sregs=None, sregs_av=None):
    """

    Args:
        entities: A list of Low Layer Entities (LLEs) indexes (all different).
        entities_av: A list of LLE availability ordered as entities.
        relate: A list with High Layer Entities (HLEs) related to LLE each
                element is a list of HLEs, ordered as entities.
        sregs: A list of SRLGs, where each SRLG is a list of
               LLE indexes (same as entities).
        sregs_av: A list of SRLGs availability, no superposition
                  of LLE and SRLG is supposed.

    Returns: ret_cuts, ret_cuts_times, ret_cuts_p

        ret_cuts: A list of HLE cuts, each element is a list of HLE
                  indexes
        ret_cuts_times: A list with the times each HLE cut is repeated
        ret_cuts_p: A list with the probability of each HLE cut, same
                    order as ret_cuts.

    """

    if sregs is None:
        sregs = []
        sregs_av = []

    base = [[i] for i in entities] + sregs[:]
    av = entities_av[:] + sregs_av[:]

    low_cuts = []
    low_cuts_p = []
    for comb in combinations(base, 2):
        low_cuts.append(list(set(comb[0] + comb[1])))
        prob = 1
        for c_id, conduit in enumerate(base):
            if conduit in low_cuts[-1]:
                prob *= (1 - av[c_id])
            else:
                prob *= av[c_id]()
        low_cuts_p.append(prob)

    low_cuts = base[:] + low_cuts[:]
    low_cuts_p = [(1 - av_c) for av_c in av] + low_cuts_p

    high_cuts = []
    high_cuts_p = []
    for i, ots_cut in enumerate(low_cuts):
        otu_cut = []
        for ots in ots_cut:
            otu_cut = otu_cut + relate[ots]
        otu_cut = set(otu_cut)

        high_cuts.append(otu_cut)
        high_cuts_p.append(low_cuts_p[i])

    ret_cuts = []
    ret_cuts_p = []
    ret_cuts_times = []
    for otu_cut in high_cuts:
        if list(otu_cut) not in ret_cuts:
            ret_cuts.append(list(otu_cut))
            ret_cuts_times.append(high_cuts.count(otu_cut))

            prob = 0
            for i, otu_cut2 in enumerate(high_cuts):
                if otu_cut == otu_cut2:
                    prob += high_cuts_p[i]
            ret_cuts_p.append(prob)
    return ret_cuts, ret_cuts_p, ret_cuts_times


def inlayer_cuts(entities, entities_av, srlgs, srlgs_av):
    """
    Args:
        entities: A list of single layer entities.
        entities_av: A lis of the availability of each entity
        srlgs: A list with srlgs, each srlg is a list of entities.
        srlgs_av: A list with srlgs availability.
    Returns: ret_cuts, ret_cuts_times, ret_cuts_p
        ret_cuts: A list of entity cuts, each element is a list of entities
        ret_cuts_times: A list with the times each entities cut is repeated
        ret_cuts_p: A list with the probability of each entity cut, same
                    order as ret_cuts.
    """

    cuts = []
    cuts_p = []

    base = [[ent] for ent in entities] + srlgs
    base_av = entities_av + srlgs_av
    for comb in combinations(base, 2):
        cut = []
        prob = 1
        for e_id in comb[0]+comb[1]:
            cut.append(e_id)
            prob *= (1 - base_av[base.index(e_id)])
        cuts.append(set(cut))
        cuts_p.append(prob)

    ret_cuts = list(set(cuts))
    ret_cuts_p = []
    ret_cuts_times =[]

    for cut in ret_cuts:
        ret_cuts_times.append(cuts.count(cut))
        p = 0
        for c_id, cut2 in enumerate(cuts):
            if cut2 == cut:
                p += cuts_p[c_id]
        ret_cuts_p.append(p)
    return ret_cuts, ret_cuts_p, ret_cuts_times


# coding=utf-8


def global_survived(kp, demands):
    s = 0
    for K in kp:
        if len(K) == len(demands):
            s += 1
    return s / float(len(kp))


def survived_dem(kp):
    sk = []
    for k in kp:
        sk.append(len(k))
    return sk


def failed_dem(kp, demands):
    fk = []
    for k in kp:
        fk.append(len(demands) - len(k))
    return fk


def dem_survival(kp, demands):
    dem_s = []
    for k in range(demands):
        gss = []
        for g_i in range(kp):
            if k in kp[g_i]:
                gss.append(g_i)
        dem_s.append(gss)
    return dem_s


def compute_dem_av(Kp, demands, scenarios, scenarios_p):
    dem_av = []
    for k in range(len(demands)):
        k_p = 0
        for g_i in range(scenarios):
            if k not in Kp[g_i]:
                k_p += scenarios_p[g_i]
        dem_av.append(1 - k_p)
    return dem_av


def print_scenario(graph, scenario, scenario_p=None, scenario_rep=None, e_lbl='label'):
    print("----------------------------------------------------------------")
    if scenario_rep:
        print("Physical cuts that generates this scenario: %d"%scenario_rep)
    if scenario_p:
        print("Happening probability of this scenario: " % scenario_p)

    print("Failed links: ")
    for e_i in scenario:
        print("        ", graph.es[e_i][e_lbl])
    print("----------------------------------------------------------------")
import argparse
import random as rd
from heapq import heappop, heappush

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def duree_exp(p):
    return np.random.exponential(1 / p)


def backoff(i, tau):
    """fonction de backoff exponentiel binaire"""
    return np.random.exponential(2**i * tau)


Tmax = 1000
MAX_BACKOFF = 16  # nombre maximum de backoff avant de perdre le paquet
taille_paquet = 2


def simulation_csmacd(
    lamda, N=10, Tmax=1000, MAX_BACKOFF=16, K=10, taille_paquet=2, tau_backoff=0.1
):
    """simulateur de CSMA/CD"""

    t = 0
    events = []
    canal_libre = True
    current_sender = -1

    fin_bouillage = False  # nous sers pour ne pas faire plusique fois fin de brouillage
    tranmission_canselled = set()  # Ensemble pour suivre les transmissions annulées
    stations_a_backoff = set()  # Ensemble pour suivre les stations en backoff
    i_par_station = [0] * N  # Initialisation du nombre de points par station à 0
    nb_packets_par_station = [
        0
    ] * N  # Initialisation du nombre de points par station à 0
    stations_en_attente = (
        set()
    )  # Ensemble pour suivre les stations en attente de transmission

    packets_perdus = 0  # nombre total de paquets perdus
    packets_arrives = 0  # nombre total de paquets arrives vers les machines
    packets_emis = 0  # nombre de paquets emis

    n_t = []  # nombre total de paquet transmis à l'instant t
    clients_t = []  # nombre moyen de paquets en attentes à travers le temps
    perdus_t = []  # nombre de paquet perdu  travers le temps

    for i in range(N):
        t_arrivee = duree_exp(lamda)
        heappush(events, (t_arrivee, "arrivee_paquet", i))

    while t < Tmax:
        n_t.append([t, packets_emis])
        clients_t.append([t, sum(nb_packets_par_station)])
        if packets_arrives > 0:
            perdus_t.append([t, packets_perdus / packets_arrives])
        else:
            perdus_t.append([t, 0])
        t, event, machine = heappop(events)
        match event:
            case "sense":
                if canal_libre:
                    heappush(
                        events, (t + 0.5, "debut_transmission", machine)
                    )  # si le canal est libre on commance a transmettre le paquet 0.05 est le temps pour commencer a transmettre le paquet
                else:
                    stations_en_attente.add(machine)

            case "debut_transmission":
                if canal_libre:
                    # print('temps de debut de transmission canale libre  :',t,'station :',machine,'current sender :',current_sender)

                    canal_libre = False
                    current_sender = machine
                    heappush(
                        events, (t + taille_paquet, "fin_transmission", machine)
                    )  # 10 est le temps de transmission du paquet

                else:
                    # collision

                    machine1 = current_sender
                    machine2 = machine

                    tranmission_canselled.add(
                        machine1
                    )  # Ajouter la machine actuelle à l'ensemble des transmissions annulées car on avait ajoute une fin de transmission pour cette marchine et il faut pas en tenir compte

                    # print('collision current_sender:',current_sender,'temps :',t)
                    # print('tranission cansaled:')
                    # print(tranmission_canselled)

                    if (
                        current_sender not in stations_a_backoff
                    ):  # Si la machine actuelle n'est pas déjà en backoff
                        i_machine1 = i_par_station[machine1]
                        i_par_station[machine1] = i_machine1 + 1

                        if i_par_station[machine1] >= MAX_BACKOFF:
                            packets_perdus += 1
                            nb_packets_par_station[machine1] = max(
                                0, nb_packets_par_station[machine1] - 1
                            )  # Retirer un paquet de la station
                            i_par_station[machine1] = (
                                0  # Réinitialiser le compteur de backoff pour la station
                            )

                            if (
                                nb_packets_par_station[machine1] > 0
                            ):  # S'il reste des paquets à transmettre pour cette station
                                heappush(
                                    events, (t + 0.005, "sense", machine1)
                                )  # on va sense le canal si il est libre ou pas pour le prochain paquet de la station
                        else:
                            stations_a_backoff.add(
                                machine1
                            )  # Ajouter la machine actuelle à l'ensemble des stations en backoff
                            heappush(
                                events,
                                (
                                    t + backoff(i_machine1, tau_backoff),
                                    "sense",
                                    machine1,
                                ),
                            )

                    if machine2 in stations_en_attente:
                        stations_en_attente.remove(
                            machine2
                        )  # retirer cette machine si elle est impliquee dans une collision car son sense est géré par le backoff

                    i_machine2 = i_par_station[machine2]
                    stations_a_backoff.add(
                        machine2
                    )  # Ajouter la machine qui arrive à l'ensemble des stations en backoff

                    i_par_station[machine2] = i_machine2 + 1
                    if i_par_station[machine2] >= MAX_BACKOFF:
                        packets_perdus += 1
                        nb_packets_par_station[machine2] = max(
                            0, nb_packets_par_station[machine2] - 1
                        )  # Retirer un paquet de la station
                        i_par_station[machine2] = (
                            0  # Réinitialiser le compteur de backoff pour la station
                        )

                        if (
                            nb_packets_par_station[machine2] > 0
                        ):  # S'il reste des paquets à transmettre pour cette station
                            heappush(
                                events, (t + 0.005, "sense", machine2)
                            )  # on va sense le canal si il est libre ou pas pour le prochain paquet de la station
                    else:
                        heappush(
                            events,
                            (t + backoff(i_machine2, tau_backoff), "sense", machine2),
                        )

                    if not fin_bouillage:
                        fin_bouillage = True  # Indiquer que le bouillage est en cours
                        heappush(
                            events, (t + 1, "fin_bouillage", None)
                        )  # brouillage pendant 1 s

            case "fin_bouillage":
                # print('fin de bouillage :',t)
                fin_bouillage = False  # Réinitialiser le flag de fin de bouillage
                canal_libre = True  # le canal redevient libre après le bouillage
                current_sender = -1  # il n y a plus de machine qui transmet
                for station in stations_en_attente:
                    heappush(
                        events, (t + 0.005, "sense", station)
                    )  # on va snese le canal pour les autres stations qui sont en attente de transmission

                stations_en_attente.clear()  # Vider l'ensemble des stations en attente après le bouillage

            case "fin_transmission":
                if (
                    machine not in tranmission_canselled
                ):  # Vérifier si la machine n'est pas dans l'ensemble des transmissions annulées
                    # print('*** temps de fin de transmission canale libre  :',t,'station :',machine,'current sender :',current_sender)

                    current_sender = -1  # il n y a plus de machine qui transmet
                    canal_libre = True  # le canal redevient libre
                    packets_emis += 1  # increment le nombre de paquets emis "n(t)"

                    nb_packets_par_station[machine] -= 1
                    if (
                        nb_packets_par_station[machine] > 0
                    ):  # S'il reste des paquets à transmettre pour cette station
                        heappush(
                            events, (t + 0.005, "sense", machine)
                        )  # on va sense le canal si il est libre ou pas pour le prochain paquet de la station

                    if machine in stations_en_attente:
                        stations_en_attente.remove(
                            machine
                        )  # Retirer la station de l'ensemble des stations en attente

                    for station in stations_en_attente:
                        heappush(
                            events, (t + 0.005, "sense", station)
                        )  # on va snese le canal pour les autres stations qui sont en attente de transmission
                    stations_en_attente.clear()  # Vider l'ensemble des stations en attente après la fin de la transmission

                    if machine in stations_a_backoff:
                        stations_a_backoff.remove(
                            machine
                        )  # Retirer la station de l'ensemble des stations en backoff

                    i_par_station[machine] = (
                        0  # Réinitialiser le compteur de backoff pour la station qui a réussi à transmettre
                    )
                else:
                    tranmission_canselled.discard(machine)

            case "arrivee_paquet":
                packets_arrives += 1
                nb_packets_par_station[machine] += 1
                heappush(events, (t + duree_exp(lamda), "arrivee_paquet", machine))

                if (
                    nb_packets_par_station[machine] == 1
                ):  # Si la station était vide avant l'arrivée du paquet
                    heappush(
                        events, (t + 0.005, "sense", machine)
                    )  # si le nombre de  pakets est egale a 1 alors on va snese le canal si il est libre ou pas

                if (
                    nb_packets_par_station[machine] == K + 1
                ):  # verifie si la file était pleine au moment de l'arrivé du paquet
                    # incrementer le nombre de paquet perdu
                    packets_perdus += 1
                    nb_packets_par_station[machine] = K

    return n_t, clients_t, perdus_t


def debit_fenetre_glissante(n_t, fenetre=50):
    """
    Calcule le débit instantané sur une fenêtre glissante.
    Beaucoup plus fiable que la moyenne cumulée.
    """
    times = [x[0] for x in n_t]
    counts = [x[1] for x in n_t]
    debits = []

    for i, (t, n) in enumerate(zip(times, counts)):
        # Trouver le premier point dans la fenêtre
        j = i - 1
        while j >= 0 and times[j] >= t - fenetre:
            j -= 1
        j += 1  # premier point dans la fenêtre

        dt = t - times[j]
        dn = n - counts[j]
        if dt > 0:
            debits.append(dn / dt)
        else:
            debits.append(0)

    return times, debits


def debit_fenetre_glissante(n_t, fenetre=50):
    """
    Calcule le débit instantané sur une fenêtre glissante.
    Beaucoup plus fiable que la moyenne cumulée.
    """
    times = [x[0] for x in n_t]
    counts = [x[1] for x in n_t]
    debits = []

    for i, (t, n) in enumerate(zip(times, counts)):
        # Trouver le premier point dans la fenêtre
        j = i - 1
        while j >= 0 and times[j] >= t - fenetre:
            j -= 1
        j += 1  # premier point dans la fenêtre

        dt = t - times[j]  # le temps de la fenaitre
        dn = n - counts[j]  # le nombre de paquets emis pendent la fenaitre
        if dt > 0:
            debits.append(dn / dt)
        else:
            debits.append(0)

    return times, debits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulateur de CSMA/CD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python Simulation.py --lamda 0.2 --N 50
  python Simulation.py --Tmax 2000 --MAX_BACKOFF 32
  python Simulation.py --lamda 0.15 --N 100 --tau 0.05
        """,
    )

    parser.add_argument(
        "--lamda",
        type=float,
        default=0.1,
        help="Taux d'arrivée des paquets (défaut: 0.1)",
    )
    parser.add_argument(
        "--N", type=int, default=100, help="Nombre de stations (défaut: 100)"
    )
    parser.add_argument(
        "--Tmax",
        type=int,
        default=1000,
        help="Durée maximale de la simulation (défaut: 1000)",
    )
    parser.add_argument(
        "--MAX_BACKOFF",
        type=int,
        default=16,
        help="Nombre maximum de backoff (défaut: 16)",
    )
    parser.add_argument(
        "--K", type=int, default=10, help="Taille de la file d'attente (défaut: 10)"
    )
    parser.add_argument(
        "--taille_paquet", type=float, default=2, help="Taille du paquet (défaut: 2)"
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=0.1,
        help="Temps d'attente moyen du backoff à l'état 1 (défaut: 0.1)",
    )
    parser.add_argument(
        "--fenetre",
        type=int,
        default=50,
        help="Fenêtre de temps pour le débit instantané (défaut: 50)",
    )
    parser.add_argument("--simu", type=str, default="courbes", help="[courbes,lamda,N]")

    args = parser.parse_args()

    # Mise à jour des variables globales avec les arguments
    Tmax = args.Tmax
    MAX_BACKOFF = args.MAX_BACKOFF
    taille_paquet = args.taille_paquet

    lamda = args.lamda
    N = args.N
    K = args.K
    tau_backoff = args.tau

    print(f"Configuration de la simulation:")
    print(f"  λ (lamda): {lamda}")
    print(f"  N (stations): {N}")
    print(f"  Tmax: {Tmax}")
    print(f"  MAX_BACKOFF: {MAX_BACKOFF}")
    print(f"  K (file): {K}")
    print(f"  Taille paquet: {taille_paquet}")
    print(f"  Tau backoff: {tau_backoff}")
    print()

    n_t, clients_t, pertes_t = simulation_csmacd(
        lamda, N, Tmax, MAX_BACKOFF, K, taille_paquet, tau_backoff
    )

    # --- Débit avec fenêtre glissante ---
    times, debit_inst = debit_fenetre_glissante(n_t, fenetre=args.fenetre)

    plt.figure(figsize=(10, 4))
    plt.title("Débit instantané (fenêtre glissante de 50 unités de temps)")
    sns.lineplot(x=times, y=debit_inst)
    plt.xlabel("Temps")
    plt.ylabel("Paquets / unité de temps")
    plt.tight_layout()
    plt.savefig("debit_instantane.pdf")
    plt.close()

    x_values, y_values = zip(*n_t)
    debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
    # affichage du debit
    plt.figure()
    plt.title("nombre de paquets emis par rapport au temps")
    sns.lineplot(x=x_values, y=debit)
    plt.savefig("debit_moyen_duree.pdf")
    plt.close()

    # --- Nombre de paquets en attente ---
    plt.figure(figsize=(10, 4))
    plt.title("Nombre de paquets en attente par rapport au temps")
    x_clients, y_clients = zip(*clients_t)
    sns.lineplot(x=x_clients, y=y_clients)
    plt.xlabel("Temps")
    plt.ylabel("Paquets en attente")
    plt.tight_layout()
    plt.savefig("paquet_attebte.pdf")
    plt.close()

    # --- Taux de perte ---
    plt.figure(figsize=(10, 4))
    plt.title("Taux de perte par rapport au temps")
    x_pertes, y_pertes = zip(*pertes_t)
    sns.lineplot(x=x_pertes, y=y_pertes)
    plt.xlabel("Temps")
    plt.ylabel("Taux de perte")
    plt.tight_layout()
    plt.savefig("taux_perte.pdf")
    plt.close()

    print("Simulation terminée.")
    print(
        f"Débit moyen en régime permanent (t > 500) : {np.mean([d for t, d in zip(times, debit_inst) if t > 500]):.4f} paquets/unité de temps"
    )

    if args.simu == "lamda":
        values = []
        lamdas = []
        for i in range(60, 80):
            n_t, clients_t, pertes_t = simulation_csmacd(
                0.01 * i, N, Tmax, MAX_BACKOFF, K, 1, tau_backoff
            )
            x_values, y_values = zip(*n_t[-10:])
            debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
            values.append(sum(debit) / len(debit))
            lamdas.append(0.01 * i)
        plt.figure()
        plt.xlabel("lambda")
        plt.ylabel("debit(pquets/temps)")
        plt.title("debit d'émission en fonction de lambda")
        sns.lineplot(x=lamdas, y=values, marker="o", linestyle="")
        plt.savefig("csma_debit_lambda.pdf")
        plt.close()
    if args.simu == "N":
        values = []
        Ns = []
        for i in range(80, 125):
            N_i = i * 10
            n_t, clients_t, pertes_t = simulation_csmacd(
                lamda, N_i, Tmax, MAX_BACKOFF, K, 1, tau_backoff
            )
            x_values, y_values = zip(*n_t[-50:])
            debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
            values.append(sum(debit) / len(debit))
            Ns.append(N_i)
        plt.figure()
        plt.title("debit d'émission en fonction de N")
        plt.xlabel("N nombre de stations")
        plt.ylabel("debits(paquets/temps)")
        sns.lineplot(x=Ns, y=values, marker="o", linestyle="")
        plt.savefig("csma_debit_N.pdf")
        plt.close()

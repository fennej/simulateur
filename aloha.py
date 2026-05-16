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


# Tmax = 10_000_000


def simulation_aloha(lamda, N=10, Tmax=1000, K=100, tau=0.1):
    """simulateur de CSMA/CD"""

    t = 0
    events = []
    canal_libre = 0

    i_par_station = [0] * N  # Initialisation du nombre de points par station à 0
    nb_packets_par_station = [
        0
    ] * N  # Initialisation du nombre de points par station à 0

    packets_perdus = 0  # nombre total de paquets perdus
    packets_arrives = 0  # nombre total de paquets arrives vers les machines
    packets_emis = 0  # nombre de paquets emis

    n_t = []  # nombre total de paquet transmis à l'instant t
    clients_t = []  # nombre moyen de paquets en attentes à travers le temps
    perdus_t = []  # nombre de paquet perdu  travers le temps
    last_sender = None

    tau_backoff = tau  # temp d'attente moyen du backoff à l'état 1

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
            case "debut_transmission":
                if canal_libre == 0:
                    # print('temps de debut de transmission canale libre  :',t,'station :',machine,'current sender :',current_sender)
                    canal_libre = 1
                else:
                    # collision
                    last_sender = machine
                    canal_libre += 1

                heappush(
                    events, (t + 1, "fin_transmission", machine)
                )  # 1 est le temps de transmission du paquet

            case "fin_transmission":
                canal_libre -= 1  # le canal redevient libre
                if canal_libre == 0 and machine != last_sender:
                    packets_emis += 1  # increment le nombre de paquets emis "n(t)"
                    nb_packets_par_station[machine] -= 1
                    i_par_station[machine] = 0
                    if (
                        nb_packets_par_station[machine] > 0
                    ):  # S'il reste des paquets à transmettre pour cette station
                        heappush(
                            events, (t + 0.005, "debut_transmission", machine)
                        )  # on va sense le canal si il est libre ou pas pour le prochain paquet de la station
                else:
                    i_machine = i_par_station[machine]
                    i_par_station[machine] = i_machine + 1
                    heappush(
                        events,
                        (
                            t + backoff(i_machine, tau_backoff),
                            "debut_transmission",
                            machine,
                        ),
                    )
                    if machine == last_sender:
                        last_sender == None

            case "arrivee_paquet":
                packets_arrives += 1
                nb_packets_par_station[machine] += 1
                heappush(events, (t + duree_exp(lamda), "arrivee_paquet", machine))

                if (
                    nb_packets_par_station[machine] == 1
                ):  # Si la station était vide avant l'arrivée du paquet
                    heappush(
                        events, (t + 0.005, "debut_transmission", machine)
                    )  # si le nombre de  pakets est egale a 1 alors on va snese le canal si il est libre ou pas

                if (
                    nb_packets_par_station[machine] == K + 1
                ):  # verifie si la file était pleine au moment de l'arrivé du paquet
                    # incrementer le nombre de paquet perdu
                    packets_perdus += 1
                    nb_packets_par_station[machine] = K

    return n_t, clients_t, perdus_t


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulateur de CSMA/CD",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python aloha.py --lamda 0.2 --N 50
  python aloha.py --Tmax 2000 --MAX_BACKOFF 32
  python aloha.py --lamda 0.15 --N 100 --tau 0.05
        """,
    )

    parser.add_argument(
        "--lamda",
        type=float,
        default=0.1,
        help="Taux d'arrivée des paquets (défaut: 0.1)",
    )
    parser.add_argument(
        "--N", type=int, default=10, help="Nombre de stations (défaut: 100)"
    )
    parser.add_argument(
        "--Tmax",
        type=int,
        default=1000000,
        help="Durée maximale de la simulation (défaut: 1000)",
    )
    parser.add_argument(
        "--K", type=int, default=100, help="Taille de la file d'attente (défaut: 10)"
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=1,
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

    lamda = args.lamda
    N = args.N
    K = args.K
    tau_backoff = args.tau

    print(f"Configuration de la simulation:")
    print(f"  λ (lamda): {lamda}")
    print(f"  N (stations): {N}")
    print(f"  Tmax: {Tmax}")
    print(f"  K (file): {K}")
    print(f"  Tau backoff: {tau_backoff}")
    print()
    if args.simu == "courbes":
        n_t, clients_t, pertes_t = simulation_aloha(lamda, N, Tmax, K, tau_backoff)

        x_values, y_values = zip(*n_t)
        debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
        # affichage du debit
        plt.figure()
        plt.xlabel("temps")
        plt.ylabel("paquets/temps")
        plt.title("nombre de paquets emis par rapport au temps")
        sns.lineplot(x=x_values, y=debit)
        plt.savefig("aloha_debits.pdf")
        plt.close()
        print("debit final:", sum(debit[-500:]) / 500)

        # affichage du nombre de client
        plt.figure()
        plt.title("nombre de paquets en attentre par rapport au temps")
        plt.xlabel("temps")
        plt.ylabel("nombre de paquets")
        plt.ylim(500, 1000)
        x_clients, y_clients = zip(*clients_t)

        sns.lineplot(x=x_clients, y=y_clients)
        plt.savefig("aloha_paquets.pdf")
        plt.close()

        plt.figure()
        plt.xlabel("temps")
        plt.ylabel("paquets perdus")
        plt.title("taux de perte par rapport au temps")
        x_pertes, y_pertes = zip(*pertes_t)
        sns.lineplot(x=x_pertes, y=y_pertes)
        plt.savefig("aloha_pertes.pdf")
        plt.close()
        print("taux de pertes moyen final", sum(y_pertes[-500:]) / 500)
        print("Simulation terminée.")
    if args.simu == "lamda":
        values = []
        lamdas = []
        for i in range(15, 30):
            n_t, clients_t, pertes_t = simulation_aloha(
                0.1 * i, N, Tmax, K, tau_backoff
            )
            x_values, y_values = zip(*n_t[-500:])
            debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
            values.append(sum(debit) / len(debit))
            lamdas.append(0.1 * i)
        plt.figure()
        plt.xlabel("lambda")
        plt.ylabel("debit(pquets/temps)")
        plt.title("debit d'émission en fonction de lambda")
        sns.lineplot(x=lamdas, y=values, marker="o", linestyle="")
        plt.savefig("aloha_debit_lambda.pdf")
        plt.close()
    if args.simu == "N":
        values = []
        Ns = []
        for i in range(1, 100):
            n_t, clients_t, pertes_t = simulation_aloha(lamda, i, Tmax, K, tau_backoff)
            x_values, y_values = zip(*n_t[-500:])
            debit = [b / a if a != 0 else 0 for a, b in zip(x_values, y_values)]
            values.append(sum(debit) / len(debit))
            Ns.append(i)
        plt.figure()
        plt.title("debit d'émission en fonction de N")
        plt.xlabel("N nombre de stations")
        plt.ylabel("debits(paquets/temps)")
        sns.lineplot(x=Ns, y=values, marker="o", linestyle="")
        plt.savefig("aloha_debit_N.pdf")
        plt.close()

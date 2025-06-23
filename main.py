from simulacion import Simulador

if __name__ == "__main__":
    sim = Simulador()
    sim.iniciar_simulacion(tiempo_simulacion=900)  # 1 día laboral (900 minutos)
    print("Simulación finalizada.")

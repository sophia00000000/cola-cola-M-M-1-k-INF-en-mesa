import mesa
import random

class Customer(mesa.Agent):
    def __init__(self, unique_id, model):  # Cambiado a __init__
        super().__init__(unique_id, model)  # Cambiado a __init__
        self.time_entered_queue = model.current_time  # Usar current_time en lugar de schedule.time
        self.time_entered_service = None

class Server(mesa.Agent):
    def __init__(self, unique_id, model):  # Cambiado a __init__
        super().__init__(unique_id, model)  # Cambiado a __init__
        self.customer_being_served = None
        self.next_completion_time = None

    def step(self):
        if self.customer_being_served:
            # Completar el servicio si el tiempo de finalización se ha alcanzado
            if self.model.current_time >= self.next_completion_time:
                self.complete_service()
        else:
            # Iniciar servicio si no se está atendiendo a ningún cliente
            self.begin_service()

    def begin_service(self):
        if self.model.queue:  # Si hay clientes en la cola
            self.customer_being_served = self.model.queue.pop(0)  # Tomar al primer cliente
            self.customer_being_served.time_entered_service = self.model.current_time  # Registrar tiempo de inicio del servicio
            self.next_completion_time = self.model.current_time + random.expovariate(1.0 / self.model.mean_service_time)  # Tiempo para completar el servicio

    def complete_service(self):
        # Calcular el tiempo total que el cliente pasó en el sistema
        self.model.total_time_in_system += self.model.current_time - self.customer_being_served.time_entered_queue
        self.model.total_system_throughput += 1  # Incrementar el throughput
        self.model.schedule.remove(self.customer_being_served)  # Eliminar el cliente del sistema
        self.customer_being_served = None
        self.next_completion_time = None
        self.begin_service()  # Intentar atender al siguiente cliente


class StoreModel(mesa.Model):
    def __init__(self, num_servers, mean_arrival_rate, mean_service_time):
        super().__init__()  # Inicializa la clase base
        self.num_servers = num_servers
        self.mean_arrival_rate = mean_arrival_rate
        self.mean_service_time = mean_service_time
        self.queue = []
        self.schedule = mesa.time.RandomActivation(self)  # Inicializa el scheduler
        self.current_time = 0  # Usar una variable para controlar el tiempo manualmente
        self.next_arrival_time = self.current_time + random.expovariate(self.mean_arrival_rate)  # Tiempo para la siguiente llegada
        self.total_time_in_system = 0
        self.total_system_throughput = 0

        # Crear servidores
        for i in range(self.num_servers):
            server = Server(i, self)
            self.schedule.add(server)

    def step(self):
        # Verificar si es el momento para una nueva llegada de cliente
        if self.current_time >= self.next_arrival_time:
            self.new_customer_arrival()

        # Hacer que los agentes (servidores) avancen en sus pasos
        self.schedule.step()

        # Avanzar el tiempo manualmente
        self.current_time += 1

    def new_customer_arrival(self):
        # Crear un nuevo cliente y añadirlo a la cola
        customer = Customer(self.next_id(), self)
        self.queue.append(customer)
        self.schedule.add(customer)
        # Calcular el tiempo para la próxima llegada
        self.next_arrival_time = self.current_time + random.expovariate(self.mean_arrival_rate)

    def run_model(self, step_count):
        for _ in range(step_count):
            self.step()


# Ejemplo de uso
model = StoreModel(num_servers=1, mean_arrival_rate=1.0, mean_service_time=2.5)
model.run_model(1000)

print(f"Average time in system: {model.total_time_in_system / model.total_system_throughput if model.total_system_throughput else 0}")
print(f"Queue length: {len(model.queue)}")
print(f"Throughput: {model.total_system_throughput}")

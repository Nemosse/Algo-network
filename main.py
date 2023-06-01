import threading
import socket
import time
from queue import Queue

CITIES_AMT = 4
PORTS_LIST = [8001, 8002, 8003, 8004]

class CityNode:
    def __init__(self, city_num, port, lock, distances, visited):
        self.city_num = city_num
        self.port = port
        self.lock = lock
        self.adjacent = ["Node " + str(i + 1) for i in range(CITIES_AMT) if i + 1 != city_num]
        self.received = []
        self.distances = distances
        self.visited = visited

    def run(self):
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('localhost', self.port))
            server_socket.listen()

            print(f"\nNode {self.city_num} : running : port {self.port}\n")

            with self.lock:
                if not hasattr(self, 'isSent'):
                    self.isSent = False
                if not self.isSent:
                    for i in range(0, CITIES_AMT):
                        if (i + 1) != self.city_num:
                            self.send_num(f"Node {i + 1}", str(self.city_num))
                    self.isSent = True

            received_message = 0
            while received_message < CITIES_AMT - 1:
                print(f"Node {self.city_num} : waiting")
                client_socket, _ = server_socket.accept()
                message = client_socket.recv(1024).decode()
                self.received.append(message)
                received_message += 1
                print(f"Node {self.city_num} : received : {message}")

            server_socket.close()
        except Exception as e:
            print(e)

    def send_num(self, receiver, message):
        try:
            receiver_name = receiver.split(" ")
            receiver_host = "localhost"
            receiver_port = PORTS_LIST[int(receiver_name[1]) - 1]
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((receiver_host, receiver_port))
                sock.sendall(message.encode())
            time.sleep(2)
        except Exception as e:
            print(e)

    def calculate_distances(self):
        visited = set()
        queue = Queue()
        queue.put((self.city_num, 0))

        while not queue.empty():
            city, level = queue.get()

            if city not in visited:
                visited.add(city)
                self.visited[city] = level

                for adjacent_city in self.adjacent:
                    adjacent_num = int(adjacent_city.split(" ")[1])
                    if adjacent_num not in visited:
                        queue.put((adjacent_num, level + 1))

        distance = sum(self.visited.values())
        self.distances.put((self.city_num, distance))

    def print_distances(self):
        while not self.distances.empty():
            city_num, distance = self.distances.get()
            print(f"Node {city_num} : distance : {distance}")
        print()

def run_node(node):
    node.run()
    node.calculate_distances()

def main():
    distances = Queue()
    visited = {}
    nodes = []
    threads = []
    lock = threading.Lock()

    for i in range(CITIES_AMT):
        port = PORTS_LIST[i]
        node = CityNode(i + 1, port, lock, distances, visited)
        nodes.append(node)
        thread = threading.Thread(target=run_node, args=(node,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for node in nodes:
        node.print_distances()

if __name__ == '__main__':
    main()

#64090500432
#64090500437
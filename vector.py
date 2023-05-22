import socket
import pickle
import time
import threading


class Process:
    def __init__(self, pid: int, total_process: int = 4) -> None:
        self.pid = pid
        self.total_process = total_process
        self.vector_clock = [0] * total_process
        self.aux_vector_clock = [0] * total_process
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 5000 + pid))
        self.socket.listen()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, recipient_pid: int) -> None:
        self.vector_clock[self.pid] += 1
        message = (self.pid, self.vector_clock)
        recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient_socket.connect(('localhost', 5000 + recipient_pid))
        recipient_socket.sendall(pickle.dumps(message))
        recipient_socket.close()

    def receive_messages(self) -> None:
        while True:
            conn = self.socket.accept()[0]
            data = conn.recv(4096)
            sender_pid, sender_vector_clock = pickle.loads(data)

            for p in range(self.total_process):
                max_value = max(self.vector_clock[p], sender_vector_clock[p])
                self.vector_clock[p] = max_value

            print(f"processo: {self.pid} vector de clock que tá vindo do processo {sender_pid} {sender_vector_clock} já com o incremento do valor do evento")
            print(f"processo: {self.pid} vector de clock atualizado {self.vector_clock}")

            conn.close()


process_count = 4
proc0, proc1, proc2, *_ = [Process(i, process_count)
                           for i in range(process_count)]

# process 0 send message to process two and wait 2 seconds
proc0.send_message(1)
time.sleep(2)

# process one send message to process three and wait 2 seconds
proc1.send_message(2)
time.sleep(2)

proc2.send_message(3)

proc2.send_message(1)

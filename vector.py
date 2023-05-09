import socket
import pickle
import time
import threading


class VectorProcess:
    def __init__(self, id: int, number_of_process: int = 4) -> None:
        self.id = id
        self.number_of_process = number_of_process
        self.vector_clock = [0] * number_of_process
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('localhost', 5000 + id))
        self.socket.listen()
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, recipient_id: int) -> None:
        self.vector_clock[self.id] += 1
        message = (self.id, self.vector_clock)
        recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient_socket.connect(('localhost', 5000 + recipient_id))
        recipient_socket.sendall(pickle.dumps(message))
        recipient_socket.close()

    def receive_messages(self) -> None:
        while True:
            conn = self.socket.accept()[0]
            data = conn.recv(4096)
            sender_id, sender_vector_clock = pickle.loads(data)

            # update vector clock with max values from sender vector clock and self vector clock
            self.vector_clock[sender_id] = max(
                self.vector_clock[sender_id], sender_vector_clock[sender_id])
            self.vector_clock[self.id] += 1

            print(
                f"O Processo {self.id}: recebeu mensagem do processo {sender_id} com a vetor de clock {sender_vector_clock}")
            conn.close()


number_of_process = 4
proc0, proc1, proc2, *_ = [VectorProcess(i, number_of_process)
                           for i in range(number_of_process)]

# process 0 send message to process two and wait 2 seconds
proc0.send_message(1)
time.sleep(2)

# process one send message to process three and wait 2 seconds
proc1.send_message(2)
time.sleep(2)

# process 2 send message to process 3 and wait 2 seconds
proc2.send_message(3)
time.sleep(2)

# process 0 send message to process 3 and wait 2 seconds
proc0.send_message(3)
time.sleep(2)

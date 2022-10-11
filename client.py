from rich.console import Console
import threading
import socket
import sys

console = Console()

nickname = input("Enter nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 55555))


def receive():
    while True:
        try:
            message = client.recv(1024).decode()

            if message == "NICK":
                client.send(nickname.encode())
            elif message == "":
                console.print("[red][!] A server connection error occurred!")
                client.close()
                exit(1)
            elif message == "BAN":
                console.print("[red][!] Banned from server!")
                client.close()
                exit(1)
            elif message == "KICK":
                console.print("[yellow][-] Kicked from server!")
                client.close()
                exit(1)
            elif message == "STOP":
                console.print("[Server shutting down]")
                client.close()
                exit(0)
            else:
                console.print(message)
        except Exception as e:
            console.print_exception(show_locals=True)
            client.close()
            exit(1)


def write():
    try:
        while True:
            message = f"{nickname}: {input()}".encode()

            client.send(message)
    except Exception as e:
        console.print_exception(show_locals=True)
        exit(1)


write_thread = threading.Thread(target=write)
write_thread.daemon = True
write_thread.start()

receive()

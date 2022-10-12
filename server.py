import json
import socket
import threading
import time

from rich.console import Console

host = "127.0.0.1"
port = 55555

console = Console()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
data = json.load(open("data.json", "r"))


def brodcast(message):
    for client in clients:
        client.send(message)


def handle(client, admin=False):
    while True:
        try:
            message = client.recv(1024)
            is_command = False

            if admin == True:
                client_index = clients.index(client)
                nickname = len(nicknames[client_index])
                command = message.decode()[nickname+2:]

                print(f"{nicknames[client_index]} executed server command: {command}")

                if command.startswith("/stop"):

                    brodcast("STOP".encode())

                    is_command = True

                    for client in clients:
                        client.close()

                    print("[Server shutting down]")
                    print("[Processing request]")
                    time.sleep(2)
                    print("[Saving settings]")
                    json.dump(data, open("data.json", "w"))
                    time.sleep(1)
                    print("[Turning off in 3]")
                    time.sleep(0.1)
                    print("[Turning off in 2]")
                    time.sleep(0.1)
                    print("[Turning off in 1]")

                    server.close()

                    exit(0)
                elif command.startswith("/ban "):
                    is_command = True

                    command = command[5:]

                    try:
                        client_index = nicknames.index(command)

                        ban_client = clients[client_index]

                        ban_client.send("BAN".encode())
                        ban_client.close()
                    except Exception as ex:
                        print(ex)

                    data["banned"].append(command)
                elif command.startswith("/kick "):
                    is_command = True
                    command = command[6:]

                    try:
                        client_index = nicknames.index(command)

                        kick_client = clients[client_index]

                        kick_client.send("KICK".encode())
                        kick_client.close()
                    except Exception as ex:
                        client.send(f"[red][!] A error occurred: {str(ex)}".encode())
                elif command.startswith("/unban "):
                    is_command = True
                    command = command[7:]

                    data["banned"].remove(command)

                else:
                    is_command = False

                print(is_command)



            if is_command == False:
                brodcast(message)






        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()

            nickname = nicknames[index]
            nicknames.remove(nickname)

            try:
                brodcast(f"[yellow]{nickname} left the server.".encode())
                console.print(f"[yellow][-] {nickname} left the server.")
            finally:
                break


def receive():
    try:
        while True:
            client, address = server.accept()

            admin = False

            console.print(f"[green][+] {str(address)} connected to the server.")

            client.send("NICK".encode())
            nickname = client.recv(1024).decode()

            if nickname in data["admins"]:
                admin = True

            print(admin)

            print(client.getpeername())

            if nickname in data["banned"] or client.getpeername()[0] in data["banned"]:
                client.send("BAN".encode())
                client.close()
            else:
                nicknames.append(nickname)
                clients.append(client)

                console.print(f"[blue][i] Nickname of client is {nickname}")
                brodcast(f"[yellow]{nickname} joined the chat!".encode())

                client.send("\nConnected to the server!".encode())

                thread = threading.Thread(target=lambda: handle(client, admin=admin))
                thread.start()
    except:
        exit(1)


def commands():
    while True:
        try:
            command = input()
        except:
            command = ""
            exit(0)

        if command.startswith("kick "):
            command = command[5:]

            try:
                client_index = nicknames.index(command)

                client = clients[client_index]

                client.send("KICK".encode())
                client.close()

                console.print(f"[green][+] Successfully kicked {command}")
            except Exception as ex:
                print(ex)

        elif command.startswith("ban "):
            command = command[4:]

            try:
                try:
                    banned_clients = []
                    for client in clients:
                        if client.getpeername()[0] == command:
                            client.send("BAN".encode())
                            banned_clients.append(client)

                    for client in banned_clients:
                        client.close()

                    client_index = nicknames.index(command)

                    client = clients[client_index]
                    client.send("BAN".encode())
                    client.close()
                except:
                    pass

                data["banned"].append(command)
            except Exception as ex:
                print(ex)
        elif command.startswith("unban "):
            command = command[6:]

            try:
                data["banned"].remove(command)
                console.print(f"[green][+] Successfully unbanned {command}")
            except Exception as ex:
                print(ex)
        elif command.startswith("stop"):
            brodcast("STOP".encode())
            for client in clients:
                client.close()

            print("[Server shutting down]")
            print("[Processing request]")
            time.sleep(2)
            print("[Saving settings]")
            json.dump(data, open("data.json", "w"))
            time.sleep(1)
            print("[Turning off in 3]")
            time.sleep(0.1)
            print("[Turning off in 2]")
            time.sleep(0.1)
            print("[Turning off in 1]")

            server.close()
            exit(0)
        elif command.startswith("brodcast "):
            command = command[8:]

            brodcast(f"Server: {command}".encode())
            print(f"Server: {command}")
        elif command.startswith("op "):
            command = command[3:]

            data["admins"].append(command)
        elif command.startswith("deop "):
            command = command[5:]

            try:
                data["admins"].remove(command)
                console.print(f"[green][+] Successfully deoped {command}!")
            except Exception as ex:
                print(ex)
            except KeyboardInterrupt:
                pass
        elif command == None:
            pass
        else:
            print("Invalid command")



console.print("[green][+] Server is listening on port 55555")
thread = threading.Thread(target=receive)
thread.daemon = True
thread.start()

commands()

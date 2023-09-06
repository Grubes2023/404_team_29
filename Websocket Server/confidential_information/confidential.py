import hashlib
import json

# files to read information from
client_credential_file = 'confidential_information\\client_logins.txt'
server_connection_information_file = 'confidential_information\\server_connection_information.txt'


with open(server_connection_information_file, 'r') as file:
    server_info = json.load(file)
    host = server_info['Host']
    port = server_info['Port']


with open(client_credential_file, 'r') as file:
    client_credentials = json.load(file)

# new client_credential list -> {username : [hashed_password, zipcode]}

"""for user in client_credentials:
    print(f"user : {user}    Pass: {client_credentials[user][0]}    zip : {client_credentials[user][1]}")"""


def write_to_file(dictionary, filename):
    with open(filename, "w") as file:
        json.dump(dictionary, file)



    
# Dictionary to store personal information for each client  -> {username : [zipcode, websocket_1, websocket_2, etc]}
# this style allows one user to have multiple connections (aka multiple devices hooked up to the same zipcode)

#  coding: utf-8 

import socketserver
import os


# Copyright 2022 Hang Ngo
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Receive data from the request
        self.data = self.request.recv(1024).strip()
		#print ("Got a request of: %s\n" % self.data)

        # Split request data and put the data args into a list: headers
        headers = self.data.decode("utf-8").split(' ')

        try:
            method = headers[0]
            path = headers[1]
            if method == 'GET':
                fullpath = os.path.abspath(os.getcwd())+'/www'+os.path.normpath(path)
                try:
                    if os.path.isdir(fullpath): #path exists
                        if path[-1] == '/':
                            self.respond(200, fullpath)
                        else:
                            self.respond(301, path)
                    elif os.path.isfile(fullpath): #path is html or css files
                        self.respond(200, fullpath)
                    else:  # path is invalid
                        self.respond(404, fullpath)
                except IOError:
                    pass
            else:  # NOT A GET REQUEST
                self.respond(405, None)
        except IndexError:
            pass

    def respond(self, code, path):
        
        if code == 404:
            message = """
            <html>
            <head><title>404 Not Found</title></head>
			<body>
            <h1>404 Not Found</h1>
            <p>PAGE IS NOT FOUND.</p>
            </body>
            </html>
            """
            res = f'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(message)}\r\n\r\n\r\n{message}'
        elif code == 301:
            res=  f'HTTP/1.1 301 Moved Permanently\r\nContent-Type: text/html\r\nLocation: {path}/\r\n\n\n'
        elif code == 200:
            if os.path.isfile(path):
                file = open(path, "r")
                fileRead= file.read()
                fileType = path[path.rfind('.') + 1:len(path)]
                res = f'HTTP/1.1 200 OK\r\nContent-Type: text/{fileType}\r\nContent-Length: {len(fileRead)}\r\n\r\n{fileRead}'
                file.close()

            else: #path.endswith('/')
                file = open(f'{path}/index.html', "r")
                fileRead= file.read()
                fileLen = len(fileRead)
                res = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {fileLen}\r\n\r\n{fileRead}'

        elif code == 405:
            message = """
            <html>
            <head><title>405 Method Not Allowed</title></head>
            <body><h1>405 Method Not Allowed</h1></body>
            </html>
            """
            res = f'HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\nContent-Length: {len(message)}\r\n\r\n\r\n{message}'
        self.request.sendall(bytearray(res, 'utf-8'))
        return
        



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

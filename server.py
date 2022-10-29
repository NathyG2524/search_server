import socket
import threading
from timeit import timeit
import logging
import timeit
# from daemonize import Daemonize


HEADER = 64
PORT = 64511
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECTED!"



# create formatter
logging.basicConfig(
    filename='log.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

# create logger
logger = logging.getLogger('[SEARCH]')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def changePath(winpath):
        """
        Change windows path to linux Path

        This is a function simply takes window Path
        split the path on the backslash and make a new linux
        Path by concatnating

        Parameter
        --------
        winpath: str
            windows path

        Returns
        -------
        str
            linux path

        Example
        -------
        >>> changePath("z:\\mypath\\foobar\\200k.txt")
        /mnt/storage/meat/foobar/200k.txt
        """
        p = winpath.split('\\')
        ubupath = '/mnt/storage/meat/' + p[-2] + '/' + p[-1]
        return ubupath


    def checkForString(string, path):
        """
        Check if string exist or not

        This is a function search for a string exist in a file or not

        Parameter
        --------

        string: str
            string to search for in the file
        path: str
            Path containing the file location

        Returns
        -------
        str:
            "STRING EXISTS" - if the string is in the file
            "STRING NOT FOUND" - if the string is not in the file
        """
        with open(path, "rb") as f:
            for index, line in enumerate(f):
                if string in line:
                    return "STRING EXISTS"
            return "STRING NOT FOUND"

    def close():
        server.shutdown(socket.SHUT_RDWR)
        server.close()

    def handle_client(conn, addr):
        """
        Handels clients requesst

        Parameter
        --------

        conn: object
            an object used to reciev or send data from the client
        addr: object
            Contain IP address and Port of the client connected

        Returns
        -------
        
        """
        logger.debug(f'[NEW CONNECTION {addr} connected.')
        # logger.debug(f'[{addr}]')
        CONNECTED = True
        msg_list = []
        while CONNECTED:
            msg_length = conn.recv(HEADER).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT).rstrip('\x00')
                if msg == DISCONNECT_MESSAGE:
                    CONNECTED = False

                msg_list.append(msg)
        string = msg_list[0]
        path = msg_list[1]
        logger.debug(f'[SEARCHING FOR] - {string}')
        logger.debug(f'[SEARCHING IN] - {path}')
        #change windows path to linux
        # path = changePath(path)
        result = checkForString(string.encode(FORMAT), path).encode(FORMAT)
        conn.send(result)
        logger.debug(f'{result.decode(FORMAT)}')
        logger.debug(f'[Connection closed {addr}')
        conn.close()
        return msg_list

if __name__ == '__main__':
    import socket
    import threading
    
    logger.debug('[STARTING] server is starting ...')
    logger.debug(f'[STARTING] Server is listening on {SERVER}')

    # server using IPV4 and TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #Bind server to port number and IP address
    server.bind(ADDR)

    server.listen()

    while True:
        # ip, port = server.server_address
        conn, addr = server.accept()

        starttime = timeit.default_timer()
        thread = threading.Thread(target=Server.handle_client, args=(conn, addr))
        thread.start()

        exec_time = timeit.default_timer() - starttime
        logger.debug(f'''
        millisecond execution time per file: {round(exec_time * 1000, 1)}ms''')


#     def start():
#         """
#         Starts a server

#         Parameter
#         --------

#         Returns
#         -------
        
#         """
#         # become a server socket
#         server.listen()
#         logger.debug(f'[STARTING] Server is listening on {SERVER}')

#         while True:
#             conn, addr = server.accept()
#             #record starting time
            

#             #use multithreading to handle different users
#             thread = threading.Thread(target=handle_client, args=(conn, addr))
#             thread.start()

#             #calculate the time taken to excute the trade
#             exec_time = timeit.default_timer() - starttime
#             logger.debug(f'''
#             millisecond execution time per file: {round(exec_time * 1000, 1)}ms''')

#             #log number of active connection
#             logger.debug(f'[ACTIVE CONNECTIONS] {threading.activeCount() -1}')
#             close()
#             print(f'closed')

# logger.debug('[STARTING] server is starting ...')
# # # daemon = Daemonize(app="server", pid=pid, action=main)
# # # daemon.start()
# # start()



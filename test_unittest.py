import unittest
import socket


from server import changePath
from server import checkForString
from server import FORMAT
# from server import handle_client

class Server(unittest.TestCase):

    # def setUp(self):
    #     PORT = 64511
    #     SERVER = socket.gethostbyname(socket.gethostname())
    #     ADDR = (SERVER, PORT)
    #     self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.server.bind(ADDR)
    #     self.conn, self.addr = self.server.accept()
    #     print(f'addr ')


    # def tearDown(self):
    #     self.server.close()
        
    # def test_handleClient(self):
    #     handle_client = handle_client(self.conn, self.addr)
    #     print(f'addr {self.addr}')

    def test_changePath(self):
        path = changePath("z:\mypath\\foobar\\200k.txt")
        self.assertEqual(path,  "/mnt/storage/meat/foobar/200k.txt")


    def test_checkForString_Exists(self):
        string = "0"
        path = "/home/nathy/algo_test/socket_with_tim/200k.txt"
        check = checkForString(string.encode(FORMAT), path)
        self.assertEqual(check, "STRING EXISTS")

    def test_checkForString_Not_Found(self):
            string = "JJJJ"
            path = "/home/nathy/algo_test/socket_with_tim/200k.txt"
            check = checkForString(string.encode(FORMAT), path)
            self.assertEqual(check, "STRING NOT FOUND")

if __name__ == '__main__':
    unittest.main()

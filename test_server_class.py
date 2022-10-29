import unittest
from test import test_support

import errno
import socket
import select
import time
import traceback
import queue
import sys
import os
import array
import contextlib
from weakref import proxy
import signal
import math
# from threading import thread

from server import FORMAT, changePath, checkForString
from server import handle_client

def try_address(host, port=64511, family=socket.AF_INET):
    """Try to bind a socket on the given host:port and return True
    if that has been possible."""
    try:
        sock = socket.socket(family, socket.SOCK_STREAM)
        sock.bind((host, port))
    except (socket.error, socket.gaierror):
        return False
    else:
        sock.close()
        return True

HOST = socket.gethostbyname(socket.gethostname())
MSG = b'Michael Gilfix was here\n'
SUPPORTS_IPV6 = socket.has_ipv6 and try_address('::1', family=socket.AF_INET6)

try:
    # import thread
    import threading
except ImportError:
    thread = None
    threading = None

HOST = socket.gethostbyname(socket.gethostname())

MSG = 'Michael Gilfix was here\n   '



class SocketTCPTest(unittest.TestCase):

    def setUp(self):
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = test_support.bind_port(self.serv)
        self.serv.listen(1)

    def tearDown(self):
        self.serv.close()
        self.serv = None

class ThreadableTest:
    """Threadable Test class
    The ThreadableTest class makes it easy to create a threaded
    client/server pair from an existing unit test. To create a
    new threaded class from an existing unit test, use multiple
    inheritance:
        class NewClass (OldClass, ThreadableTest):
            pass
    This class defines two new fixture functions with obvious
    purposes for overriding:
        clientSetUp ()
        clientTearDown ()
    Any new test functions within the class must then define
    tests in pairs, where the test name is preceeded with a
    '_' to indicate the client portion of the test. Ex:
        def testFoo(self):
            # Server portion
        def _testFoo(self):
            # Client portion
    Any exceptions raised by the clients during their tests
    are caught and transferred to the main thread to alert
    the testing framework.
    Note, the server setup function cannot call any blocking
    functions that rely on the client thread during setup,
    unless serverExplicitReady() is called just before
    the blocking call (such as in setting up a client/server
    connection and performing the accept() in setUp().
    """

    def __init__(self):
        # Swap the true setup function
        self.__setUp = self.setUp
        self.__tearDown = self.tearDown
        self.setUp = self._setUp
        self.tearDown = self._tearDown

    def serverExplicitReady(self):
        """This method allows the server to explicitly indicate that
        it wants the client thread to proceed. This is useful if the
        server is about to execute a blocking routine that is
        dependent upon the client thread during its setup routine."""
        self.server_ready.set()

    def _setUp(self):
        self.server_ready = threading.Event()
        self.client_ready = threading.Event()
        self.done = threading.Event()
        self.queue = queue.Queue(1)

        # Do some munging to start the client test.
        methodname = self.id()
        i = methodname.rfind('.')
        methodname = methodname[i+1:]
        test_method = getattr(self, '_' + methodname)
        self.client_thread = thread.start_new_thread(
            self.clientRun, (test_method,))

        self.__setUp()
        if not self.server_ready.is_set():
            self.server_ready.set()
        self.client_ready.wait()

    def _tearDown(self):
        self.__tearDown()
        self.done.wait()

        if not self.queue.empty():
            msg = self.queue.get()
            self.fail(msg)

    def clientRun(self, test_func):
        self.server_ready.wait()
        self.clientSetUp()
        self.client_ready.set()
        if not callable(test_func):
            raise TypeError("test_func must be a callable function.")
        try:
            test_func()
        except Exception as strerror:
            self.queue.put(strerror)
        self.clientTearDown()

    def clientSetUp(self):
        raise NotImplementedError("clientSetUp must be implemented.")

    def clientTearDown(self):
        self.done.set()
        thread.exit()

class ThreadedTCPSocketTest(SocketTCPTest, ThreadableTest):

    def __init__(self, methodName='runTest'):
        SocketTCPTest.__init__(self, methodName=methodName)
        ThreadableTest.__init__(self)

    def clientSetUp(self):
        self.cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def clientTearDown(self):
        self.cli.close()
        self.cli = None
        ThreadableTest.clientTearDown(self)

class SocketConnectedTest(ThreadedTCPSocketTest):

    def __init__(self, methodName='runTest'):
        ThreadedTCPSocketTest.__init__(self, methodName=methodName)

    def setUp(self):
        ThreadedTCPSocketTest.setUp(self)
        # Indicate explicitly we're ready for the client thread to
        # proceed and then perform the blocking call to accept
        self.serverExplicitReady()
        conn, addr = self.serv.accept()
        self.cli_conn = conn

    def tearDown(self):
        self.cli_conn.close()
        self.cli_conn = None
        ThreadedTCPSocketTest.tearDown(self)

    def clientSetUp(self):
        ThreadedTCPSocketTest.clientSetUp(self)
        self.cli.connect((HOST, self.port))
        self.serv_conn = self.cli

    def clientTearDown(self):
        self.serv_conn.close()
        self.serv_conn = None
        ThreadedTCPSocketTest.clientTearDown(self)

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
    
class BasicTCPTest(SocketConnectedTest):

    def __init__(self, methodName='runTest'):
        SocketConnectedTest.__init__(self, methodName=methodName)

    def test_handleCilent(self):
        port = 64511
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(sock.close)
        sock.bind(("0.0.0.0", port))
        sock.listen()
        conn, addr = sock.accept()
        CONNECTED = True
        msg_list = []
        while CONNECTED:
            msg_length = conn.recv(64).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT).rstrip('\x00')
                if msg == 'DISCONNECTED!':
                    CONNECTED = False

                msg_list.append(msg)

        recived = handle_client(conn, addr)
        self.assertEqual(recived[0], msg)
        self.assertEqual

#     def testSockName(self):
#         # Testing getsockname()
#         port = 64511
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.addCleanup(sock.close)
#         sock.bind(("0.0.0.0", port))
#         name = sock.getsockname()
#         try:
#             my_ip_addr = socket.gethostbyname(socket.gethostname())
#         except socket.error:
#             # Probably name lookup wasn't set up right; skip this test
#             return
#         self.assertIn(name[0], ("0.0.0.0", my_ip_addr), '%s invalid' % name[0])
#         self.assertEqual(name[1], port)
        

#     def testSocketError(self):
#         # Testing socket module exceptions
#         def raise_error(*args, **kwargs):
#             raise socket.error
#         def raise_herror(*args, **kwargs):
#             raise socket.herror
#         def raise_gaierror(*args, **kwargs):
#             raise socket.gaierror
#         self.assertRaises(socket.error, raise_error,
#                               "Error raising socket exception.")
#         self.assertRaises(socket.error, raise_herror,
#                               "Error raising socket exception.")
#         self.assertRaises(socket.error, raise_gaierror,
#                               "Error raising socket exception.")
    
    
#     def testDefaultTimeout(self):
#         # Testing default timeout
#         # The default timeout should initially be None
#         self.assertEqual(socket.getdefaulttimeout(), None)
#         s = socket.socket()
#         self.assertEqual(s.gettimeout(), None)
#         s.close()

#         # Set the default timeout to 10, and see if it propagates
#         socket.setdefaulttimeout(10)
#         self.assertEqual(socket.getdefaulttimeout(), 10)
#         s = socket.socket()
#         self.assertEqual(s.gettimeout(), 10)
#         s.close()

#         # Reset the default timeout to None, and see if it propagates
#         socket.setdefaulttimeout(None)
#         self.assertEqual(socket.getdefaulttimeout(), None)
#         s = socket.socket()
#         self.assertEqual(s.gettimeout(), None)
#         s.close()

#         # Check that setting it to an invalid value raises ValueError
#         self.assertRaises(ValueError, socket.setdefaulttimeout, -1)

#         # Check that setting it to an invalid type raises TypeError
#         self.assertRaises(TypeError, socket.setdefaulttimeout, "spam")




# @unittest.skipUnless(thread, 'Threading required for this test.')
# class BasicTCPTest(SocketConnectedTest):

#     def __init__(self, methodName='runTest'):
#         SocketConnectedTest.__init__(self, methodName=methodName)

#     def testRecv(self):
#         # Testing large receive over TCP
#         msg = self.cli_conn.recv(1024)
#         self.assertEqual("msg", "MSG")

#     def _testRecv(self):
#         self.serv_conn.send(MSG)

#     def testOverFlowRecv(self):
#         # Testing receive in chunks over TCP
#         seg1 = self.cli_conn.recv(len(MSG) - 3)
#         seg2 = self.cli_conn.recv(1024)
#         msg = seg1 + seg2
#         self.assertEqual(msg, MSG)

#     def _testOverFlowRecv(self):
#         self.serv_conn.send(MSG)

#     def testRecvFrom(self):
#         # Testing large recvfrom() over TCP
#         msg, addr = self.cli_conn.recvfrom(1024)
#         self.assertEqual(msg, MSG)

#     def _testRecvFrom(self):
#         self.serv_conn.send(MSG)

#     def testOverFlowRecvFrom(self):
#         # Testing recvfrom() in chunks over TCP
#         seg1, addr = self.cli_conn.recvfrom(len(MSG)-3)
#         seg2, addr = self.cli_conn.recvfrom(1024)
#         msg = seg1 + seg2
#         self.assertEqual(msg, MSG)

#     def _testOverFlowRecvFrom(self):
#         self.serv_conn.send(MSG)

#     def testSendAll(self):
#         # Testing sendall() with a 2048 byte string over TCP
#         msg = ''
#         while 1:
#             read = self.cli_conn.recv(1024)
#             if not read:
#                 break
#             msg += read
#         self.assertEqual(msg, 'f' * 2048)

#     def _testSendAll(self):
#         big_chunk = 'f' * 2048
#         self.serv_conn.sendall(big_chunk)

#     def testFromFd(self):
#         # Testing fromfd()
#         if not hasattr(socket, "fromfd"):
#             return # On Windows, this doesn't exist
#         fd = self.cli_conn.fileno()
#         sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
#         self.addCleanup(sock.close)
#         msg = sock.recv(1024)
#         self.assertEqual(msg, MSG)

#     def _testFromFd(self):
#         self.serv_conn.send(MSG)

#     def testDup(self):
#         # Testing dup()
#         sock = self.cli_conn.dup()
#         self.addCleanup(sock.close)
#         msg = sock.recv(1024)
#         self.assertEqual(msg, MSG)

#     def _testDup(self):
#         self.serv_conn.send(MSG)

#     def testShutdown(self):
#         # Testing shutdown()
#         msg = self.cli_conn.recv(1024)
#         self.assertEqual(msg, MSG)
#         # wait for _testShutdown to finish: on OS X, when the server
#         # closes the connection the client also becomes disconnected,
#         # and the client's shutdown call will fail. (Issue #4397.)
#         self.done.wait()

#     def _testShutdown(self):
#         self.serv_conn.send(MSG)
#         self.serv_conn.shutdown(2)

if __name__ == '__main__':
    unittest.main()

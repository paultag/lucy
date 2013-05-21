from lucy.models.machine import Machine
from lucy.models.report import Report

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import socketserver
import threading

NAMESPACE = threading.local()


class LucyAuthMixIn(SimpleXMLRPCRequestHandler):
    def authenticate(self):
        (basic, _, encoded) = self.headers.get('Authorization').partition(' ')
        if basic.lower() != 'basic':
            self.send_error(401, 'Only allowed basic type thing')

        machine, password = b64decode(encoded.encode()).decode().split(":", 1)
        machine = Machine.load(machine)
        if machine.auth(password):
            NAMESPACE.machine = machine
            return True
        NAMESPACE.machine = None
        return False

    def parse_request(self, *args):
        if super(LucyAuthMixIn, self).parse_request(*args):
            if self.authenticate():
                return True
            else:
                self.send_error(401, 'Authentication failed')
        return False


class AsyncXMLRPCServer(socketserver.ThreadingMixIn, LucyAuthMixIn):
    pass


class LucyInterface(object):
    def version(self):
        return "1.0"

    def identify(self):
        return NAMESPACE.machine['_id']

    def submit_report(self, package, report):
        r = Report(builder=NAMESPACE.machine['_id'],
                   report=report,
                   package=package)
        return r.save()


def serve(server, port):
    print("Serving on `{server}' on port `{port}'".format(**locals()))
    server = SimpleXMLRPCServer((server, port),
                                requestHandler=AsyncXMLRPCServer,
                                allow_none=True)
    server.register_introspection_functions()
    server.register_instance(LucyInterface())
    server.serve_forever()


if __name__ == "__main__":
    main()


def main():
    serve("localhost", 20017)

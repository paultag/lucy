from lucy import Machine, Job, Source, Binary
from lucy.core import get_config

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import datetime as dt
import socketserver
import threading

NAMESPACE = threading.local()


class LucyInterface(object):

    def get_source_package(self, package):
        pass

    def get_binary_package(self, package):
        pass

    def get_dsc(self):
        pass

    def get_debs(self):
        pass

    #

    def get_current_job(self):
        pass

    def get_lint_job(self):
        pass

    def get_build_job(self):
        pass

    def submit_report(self, report, log, package, package_type, job, failed):
        pass

    def close_job(self, job):
        pass


# =================== ok, boring shit below ===================


def get_builder_id():
    return NAMESPACE.machine['_id']


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


def serve(server, port):
    print("Serving on `{server}' on port `{port}'".format(**locals()))
    server = SimpleXMLRPCServer((server, port),
                                requestHandler=AsyncXMLRPCServer,
                                allow_none=True)
    server.register_introspection_functions()
    server.register_instance(LucyInterface())
    server.serve_forever()


def main():
    serve("localhost", 20017)


if __name__ == "__main__":
    main()

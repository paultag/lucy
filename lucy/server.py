from lucy.models.machine import Machine
from lucy.models.report import Report
from lucy.models.job import Job

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import datetime as dt
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

    def get_next_job(self, job_type):
        ajobs = list(Job.assigned_jobs(NAMESPACE.machine['_id']))
        if len(ajobs) != []:
            return dict(ajobs[0])

        job = Job.next_job(type=job_type)
        job['builder'] = NAMESPACE.machine['_id']
        job['assigned_at'] = dt.datetime.utcnow()
        job.save()
        return dict(job)

    def submit_report(self, job, report):
        job = Job.load(job)
        if job.is_finished():
            raise ValueError("Job has already been submited")

        builder = job.get_builder()
        builder = builder['_id'] if builder else None

        if builder != NAMESPACE.machine['_id']:
            raise ValueError("Machine isn't assigned.")

        r = Report(builder=NAMESPACE.machine['_id'],
                   job=job['_id'],
                   report=report,
                   package=job['package'])
        report = r.save()

        job['finished_at'] = dt.datetime.utcnow()
        job.save()
        return report


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

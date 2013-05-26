from lucy import Machine, Job, Source
from lucy.core import get_config

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import datetime as dt
import socketserver
import threading

NAMESPACE = threading.local()


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


class LucyInterface(object):
    def version(self):
        return "1.0"

    def identify(self):
        return get_builder_id()

    def get_next_job(self, job_type):
        ajobs = list(Job.assigned_jobs(get_builder_id()))
        if ajobs != []:
            return dict(ajobs[0])

        try:
            job = Job.next_job(type=job_type)
        except KeyError:
            return None

        job['builder'] = get_builder_id()
        job['assigned_at'] = dt.datetime.utcnow()
        job.save()
        return dict(job)

    def get_dsc_url(self, package):
        config = get_config()
        package = Source.load(package)
        url = "{public}/{path}/{source}_{version}.dsc".format(
            public=config['public'],
            path=package['path'],
            source=package['source'],
            version=package['version'])
        return url

    def get_source(self, package):
        return dict(Source.load(package))

    def submit_report(self, job, report):
        job = Job.load(job)
        if job.is_finished():
            raise ValueError("Job is finished")

        builder = job.get_builder()
        builder = builder['_id'] if builder else None

        if builder != get_builder_id():
            raise ValueError("Machine isn't assigned.")

        r = Report(builder=get_builder_id(),
                   job=job['_id'],
                   report=report,
                   package=job['package'])
        return r.save()

    def close_job(self, job):
        job = Job.load(job)
        if job.is_finished():
            raise ValueError("job is already closed")

        builder = job.get_builder()
        builder = builder['_id'] if builder else None

        if builder != get_builder_id():
            raise ValueError("Machine isn't assigned.")

        job['finished_at'] = dt.datetime.utcnow()
        return job.save()


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

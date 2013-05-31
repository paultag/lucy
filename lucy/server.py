from lucy import Machine, Job, Source, Binary, Report
from lucy.archive import uuid_to_path
from lucy.core import get_config

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import datetime as dt
import socketserver
import threading

NAMESPACE = threading.local()
config = get_config()


class LucyInterface(object):

    def get_source_package(self, package):
        """
        Get the DB entry for the source package. Return None if it doesn't
        exist.
        """
        try:
            return dict(Source.load(package))
        except KeyError:
            return None

    def get_binary_package(self, package):
        """
        Get the DB entry for the binary package. Return None if it doesn't
        exist.
        """
        try:
            return dict(Binary.load(package))
        except KeyError:
            return None

    def get_dsc(self, package):
        """
        Get the .dsc path if the package is a valid source package. Otherwise
        return None.
        """
        public = config['public']
        package = Source.load(package)
        return "{public}/{pool}/{source}_{version}.dsc".format(
            public=public,
            pool=package['path'],
            source=package['source'],
            version=package['version'],
        )

    def get_deb_info(self, package):
        """
        Get a list of .debs for the given Binary package, otherwise None.
        """
        pkg = Binary.load(package)
        source = pkg.get_source()
        public = config['public']

        root = "{public}/{pool}/{arch}".format(
            public=public,
            pool=source['path'],
            arch=pkg['arch'],
        )

        return {"root": root, "packages": pkg['binaries']}

    #

    def get_current_jobs(self):
        """
        Get the current job for the builder or return None.
        """
        return list(Job.assigned_jobs(get_builder_id()))

    def forfeit_job(self, job):
        j = Job.load(job)
        buildd = j.get_builder()
        if buildd['_id'] != get_builder_id():
            return None  # meh

        j['assigned_at'] = None
        j['builder'] = None
        return j.save()

    def get_next_job(self, suites, arches, types):
        """
        Get an unassigned lint job from suite suites, arches arches
        """
        try:
            nj = Job.next_job(suites, arches, types)
        except KeyError:
            return None

        nj['assigned_at'] = dt.datetime.utcnow()
        nj['builder'] = get_builder_id()
        nj.save()
        return dict(nj)

    def submit_report(self, report, log, job, failed):
        """
        Submit a report from a run.

        report - firehose lint job
        log - full text of the run
        job - job ID this relates to
        failed - was it able to complete properly
        """
        job = Job.load(job)
        package = job.get_package()
        report = Report(report=report,
                        builder=get_builder_id(),
                        package=package['_id'],
                        package_type=job['package_type'],
                        job=job['_id'],
                        failed=failed)

        path = os.path.join(
            config['pool'],
            uuid_to_path(job['_id'])
        )
        os.makedirs(path)
        path = os.path.join(path, 'log')

        with open(path, 'w') as fd:
            fd.write(log)

        return report.save()

    def close_job(self, job):
        """
        Close a job after pushing reports / binaries up.
        """
        j = Job.load(job)
        j['finished_at'] = dt.datetime.utcnow()
        return j.save()


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

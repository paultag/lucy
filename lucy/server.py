from lucy import Machine, Job, Source, Binary, Report
from lucy.archive import uuid_to_path
from lucy.core import get_config
from lucy.mail import send_mail

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from base64 import b64decode
import datetime as dt
import socketserver
import threading
import os.path
import os

NAMESPACE = threading.local()
config = get_config()


def send_failed_email(job, package, report):
    return  # fixme

    source = package
    if package._type == 'binaries':
        source = package.get_source()
    uploader = source.get_owner()

    send_mail(
        'failed',
        uploader=uploader,
        package=package,
        job=job,
        report=report,
        source=source
    )


def machine_method(fn):
    def _(*args, **kwargs):
        try:
            get_builder_id()
            fn(*args, **kwargs)
        except KeyError:
            raise Exception("You can't do that")
    return _


def user_method(fn):
    def _(*args, **kwargs):
        try:
            get_user_id()
            fn(*args, **kwargs)
        except KeyError:
            raise Exception("You can't do that")


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
        return "{public}/{pool}/{dsc}".format(
            public=public,
            pool=package['path'],
            dsc=package['dsc'],
        )

    def get_log_write_location(self, report):
        report = Report.load(report)
        path = os.path.join(config['pool'], report['log_path'])
        return path

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

    @machine_method
    def get_current_jobs(self):
        """
        Get the current job for the builder or return None.
        """
        return list(Job.assigned_jobs(get_builder_id()))

    @machine_method
    def forfeit_job(self, job):
        j = Job.load(job)
        buildd = j.get_builder()
        if buildd['_id'] != get_builder_id():
            return None  # meh

        j['assigned_at'] = None
        j['builder'] = None
        return j.save()

    @machine_method
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

    @machine_method
    def submit_report(self, report, job, failed):
        """
        Submit a report from a run.

        report - firehose lint job
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

        uuid_path = uuid_to_path(job['_id'])

        path = os.path.join(config['pool'], uuid_path)
        if not os.path.exists(path):
            os.makedirs(path)

        report['log_path'] = os.path.join(uuid_path, 'log')
        rid = report.save()

        if failed:
            send_failed_email(job, package, report)

        return rid

    @machine_method
    def close_job(self, job):
        """
        Close a job after pushing reports / binaries up.
        """
        j = Job.load(job)
        j['finished_at'] = dt.datetime.utcnow()
        return j.save()


# =================== ok, boring shit below ===================


def get_builder_id():
    if NAMESPACE.machine is None:
        raise KeyError("What the shit, doing something you can't do")
    return NAMESPACE.machine['_id']


def get_user_id():
    if NAMESPACE.user is None:
        raise KeyError("What the shit, doing something you can't do")
    return NAMESPACE.user['_id']


class LucyAuthMixIn(SimpleXMLRPCRequestHandler):
    def authenticate(self):
        NAMESPACE.machine = None
        NAMESPACE.user = None
        (basic, _, encoded) = self.headers.get('Authorization').partition(' ')
        if basic.lower() != 'basic':
            self.send_error(401, 'Only allowed basic type thing')
        entity, password = b64decode(encoded.encode()).decode().split(":", 1)

        if self.authenticate_machine(entity, password):
            return True
        return self.authenticate_user()

    def authenticate_user(self, user, password):
        user = User.load(user)
        if user.auth(password):
            NAMESPACE.user = user
            return True
        return False

    def authenticate_machine(self, machine, password):
        machine = Machine.load(machine)
        if machine.auth(password):
            NAMESPACE.machine = machine
            machine.ping()
            return True
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
    serve("0.0.0.0", 20017)


if __name__ == "__main__":
    main()

from fabric.api import run, cd, settings, put, sudo
from braid import tasks, service, package
from braid.utils import tempfile
from braid.debian import debconf

from braid import config
_hush_pyflakes = [ config ]


class Service(tasks.Service):

    serviceUser = 'list'

    def task_dump(self, dump):
        """
        Dump mailman data.
        """
        with settings(user=self.serviceUser), \
             tempfile(saveTo=dump) as tar, \
             cd('/var/lib/mailman'):
            run('/bin/tar -c -j -f {} lists data archives'.format(tar))

    def task_restore(self, dump):
        """
        Restore mailman data.
        """
        with settings(user=self.serviceUser), \
             tempfile(uploadFrom=dump) as tar, \
             cd('/var/lib/mailman'):
            run('/bin/tar -x -j -f {}'.format(tar))

    def task_install(self):
        """
        Install mailman.
        """
        debconf.setDebconfValue('mailman', 'mailman/site_languages', 'multiselect', 'en')
        debconf.setDebconfValue('mailman', 'mailman/create_site_list', 'note', '')
        package.install(['mailman'])
        put('mm_cfg.py', '/etc/mailman/mm_cfg.py', use_sudo=True)
        sudo('/usr/sbin/usermod -a -G service --home /var/lib/mailman {}'.format(self.serviceUser))

    def task_start(self):
        """
        Start mailman.
        """
        service.start('mailman')

    def task_stop(self):
        """
        Stop mailman.
        """
        service.stop('mailman')




globals().update(Service().getTasks())

# -*- coding: utf-8 -*-
import textwrap
import functools

class Composer(object):
    def __init__(self, modules, cuda_ver, cudnn_ver, ubuntu_ver, workspace, versions={}):
        if len(modules) == 0:
            raise ValueError('Modules should contain at least one module')
        pending = self._traverse(modules)
        self.modules = [m for m in self._toposort(pending)]
        self.instances = self._get_instances(versions)
        self.cuda_ver = cuda_ver
        self.cudnn_ver = cudnn_ver
        self.ubuntu_ver = ubuntu_ver
        self.workspace = workspace

    def get(self):
        return self.modules

    def ver(self, module):
        for ins in self.instances:
            if ins.__class__ is module:
                return ins.version
        return None

    def to_dockerfile(self):
        def _indent(n, s):
            prefix = ' ' * 4 * n
            return ''.join(prefix + l for l in s.splitlines(True))

        ports = ' '.join([str(p) for m in self.instances for p in m.expose()])
        return textwrap.dedent(''.join([
            _indent(3, ''.join([
                self._split('module list'),
                ''.join('# %s\n' % repr(m)
                    for m in self.instances if repr(m)),
                self._split(),
            ])),
            r'''
            FROM %s
            RUN APT_INSTALL="apt-get install -y --no-install-recommends" && \
                PIP_INSTALL="python3 -m pip --no-cache-dir install --upgrade" && \
                GIT_CLONE="git clone --depth 10" && \
                rm -rf /var/lib/apt/lists/* \

                       /etc/apt/sources.list.d/cuda.list \
                       /etc/apt/sources.list.d/nvidia-ml.list && \
                       apt-get update && \
                %s
            ''' % ('manosriram/base-tools' if self.cuda_ver is None
                     else 'manosriram/base-tools-gpu-%s' % (
                #    else 'nvidia/cuda:%s%s-devel-ubuntu%s' % (
                    self.cuda_ver,
                    ), _indent(2, 'apt-get install --yes curl python3-venv && \\ \n \
                    curl --silent --location https://deb.nodesource.com/setup_14.x | bash - && \\ \n \
                    apt-get install --yes nodejs && \\ \n \
                    apt-get install --yes build-essential && \\ \n \
                    apt install -y python3-pip && \\ \n \
                    pip3 install pipenv termcolor==1.1.0 && \\ \n  \
                    pip3 install poetry && \\ \n \
                    ') if self.workspace in ["jlab"] else ''),
                    # curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 - && \\ \n \
            '\n',
            '\n'.join([
                ''.join([
                    _indent(3, self._split(m.name())),
                    _indent(1, m.build()),
                ]) for m in self.instances
            ]),
            '\n',
            _indent(3, self._split('config & cleanup')),
            r'''
                ldconfig && \
                apt-get clean && \
                apt-get autoremove && \
                rm -rf /var/lib/apt/lists/* /tmp/* ~/*
            ''',
            r'''
            EXPOSE %s
            ''' % ports if ports else '',
            ]))

    def _traverse(self, modules):
        seen = set(modules)
        current_level = modules
        while current_level:
            next_level = []
            for module in current_level:
                yield module
                for child in (dep for dep in module.deps if dep not in seen):
                    next_level.append(child)
                    seen.add(child)
            current_level = next_level

    def _toposort(self, pending):
        data = {m: set(m.deps) for m in pending}
        for k, v in data.items():
            v.discard(k)
        extra_items_in_deps = functools.reduce(
            set.union, data.values()) - set(data.keys())
        data.update({item: set() for item in extra_items_in_deps})
        while True:
            ordered = set(item for item, dep in data.items() if len(dep) == 0)
            if not ordered:
                break
            for m in sorted(ordered, key=lambda m: m.__name__):
                yield m
            data = {
                item: (dep - ordered)
                for item, dep in data.items()
                if item not in ordered
            }
        if len(data) != 0:
            raise ValueError(
                'Circular dependencies exist among these items: '
                '{{{}}}'.format(', '.join(
                    '{!r}:{!r}'.format(
                        key, value) for key, value in sorted(
                        data.items()))))

    def _split(self, title=None):
        split_l = '# ' + '=' * 66 + '\n'
        split_s = '# ' + '-' * 66 + '\n'
        s = split_l if title is None else (
            split_l + '# %s\n' % title + split_s)
        return s

    def _get_instances(self, versions):
        inses = []
        for m in self.modules:
            ins = m(self)
            if m in versions:
                ins.version = versions[m]
            inses.append(ins)
        return inses


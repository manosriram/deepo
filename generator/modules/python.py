# -*- coding: utf-8 -*-
from .__module__ import Module, dependency, source, version
from .tools import Tools


@dependency(Tools)
@version('3.8')
@source('apt')
class Python(Module):

    def __init__(self, manager, **args):
        super(self.__class__, self).__init__(manager, **args)
        if float(self.version) < 3.8:
            raise NotImplementedError('Only support python >= 3.8 currently.')

    def build(self):
        return ""
        # return (
        #     r'''
        #     DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        #         software-properties-common \
        #         && \
        #     add-apt-repository ppa:deadsnakes/ppa && \
        #     apt-get update && \
        #     DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        #         python%s \
        #         python%s-dev \
        #         python3-distutils%s \
        #         python-setuptools \
        #         && \
        #     wget -O ~/get-pip.py \
        #         https://bootstrap.pypa.io/get-pip.py && \
        #     python%s ~/get-pip.py && \
        #       ln -sf /usr/bin/python%s /usr/local/bin/python3 && \
        #       ln -sf /usr/bin/python%s /usr/local/bin/python && \
        #       $PIP_INSTALL \
        #           setuptools \
        #           && \
        #       ''' % (
        #           self.version,
        #           self.version,
        #           '-extra' if self.composer.ubuntu_ver.startswith('18.') else '',
        #           self.version,
        #           self.version,
        #           self.version,
        #           ) if self.version.startswith('3') else
        #       r'''
        #       DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
        #           python3-pip \
        #           python-dev \
        #           && \
        #       $PIP_INSTALL \
        #           setuptools \
        #           pip \
        #           && \
        #       '''
        #   ).rstrip() + r'''
        #       $PIP_INSTALL \
        #           numpy \
        #           scipy \
        #           pandas \
        #           cloudpickle \
        #           scikit-image>=0.14.2 \
        #           scikit-learn \
        #           matplotlib \
        #           cython \
        #           tqdm \
        #           && \
        # '''

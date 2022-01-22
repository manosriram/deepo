# -*- coding: utf-8 -*-
from .__module__ import Module, dependency, source, version
from .tools import Tools
from .python import Python


@dependency(Tools, Python)
@source('git')
class Theano(Module):

    def build(self):
        return r'''
            DEBIAN_FRONTEND=noninteractive $APT_INSTALL \
                libblas-dev \
                && \
        ''' + (
            '' if self.composer.cuda_ver is None else r'''
            pip install -U pip setuptools && \
            wget -qO- https://github.com/Theano/libgpuarray/archive/v0.7.6.tar.gz | tar xz -C ~ && \
            cd ~/libgpuarray* && mkdir -p build && cd build && \
            cmake -D CMAKE_BUILD_TYPE=RELEASE \
                  -D CMAKE_INSTALL_PREFIX=/usr/local \
                  .. && \
            make -j"$(nproc)" install && \
            cd ~/libgpuarray* && \
            python3 setup.py build && \
            python3 setup.py install && \
            printf '[global]\nfloatX = float32\ndevice = cuda0\n\n[dnn]\n'''
            + r'''include_path = /usr/local/cuda/targets'''
            + r'''/x86_64-linux/include\n' > ~/.theanorc && \
        ''') + r'''
            $PIP_INSTALL \
                https://github.com/Theano/Theano/archive/master.zip \
                && \
        '''


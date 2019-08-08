# Copyright (c) '2015' Cisco Systems, Inc. All Rights Reserved

import importlib


class ClassLoader(object):
    @classmethod
    def loadClass(cls, fqClassName):
        fqClassName = str(fqClassName)
        moduleName, className = fqClassName.rsplit('.', 1)
        module = importlib.import_module(moduleName)
        return getattr(module, className)

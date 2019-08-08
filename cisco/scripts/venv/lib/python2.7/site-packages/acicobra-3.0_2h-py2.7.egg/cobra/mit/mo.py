# *************************************************************************
# Copyright (c) 2013 Cisco Systems, Inc.  All rights reserved.
# *************************************************************************
from cobra.internal.base.moimpl import BaseMo


class Mo(BaseMo):
    """
    A class to create managed objects (MOs), which represent a physical or 
    logical entity with a set of configurations and properties.
    """
    def __init__(self, parentMoOrDn, markDirty, *namingVals, **creationProps):
        if self.__class__ == Mo:
            raise NotImplementedError('Mo cannot be instantiated.')
        BaseMo.__init__(self, parentMoOrDn, markDirty, *namingVals, **creationProps)

    def delete(self):
        """
        Marks the mo as deleted. If this mo is committed, the corresponding mo
        in the backend will be deleted.
        """
        BaseMo._delete(self)

    @property
    def dn(self):
        """
        Returns the distinguished name (Dn) of the managed object (MO).
        """    
        return BaseMo._dn(self)

    @property
    def rn(self):
        """
        Returns the relative name (Rn) of the managed object (MO).
        """    
        return BaseMo._rn(self)

    @property
    def status(self):
        """
        Returns the managed object (MO) status.
        """    
        return BaseMo._status(self)

    @property
    def parentDn(self):
        """
         Returns the distinguished name (Dn) of the parent managed object (MO).
        """    
        return BaseMo._parentDn(self)

    @property
    def parent(self):
        """
        Returns the parent managed object (MO).
        """    
        return BaseMo._parent(self)

    @property
    def dirtyProps(self):
        """
        Returns modified properties that have not been committed.
        """    
        return BaseMo._dirtyProps(self)

    @property
    def children(self):
        """
        Returns the child managed objects (MOs).
        """    
        return BaseMo._children(self)

    @property
    def numChildren(self):
        """
        Returns the number of child managed objects (MOs).
        """    
        return BaseMo._numChildren(self)

    @property
    def contextRoot(self):
        return self.dn.contextRoot

    def isPropDirty(self, propName):
        """
        Returns a value indicating whether a given property has a new value that has not been committed.
        """    
        return BaseMo._isPropDirty(self, propName)

    def resetProps(self):
        """
        Resets managed object (MO) properties, discarding uncommitted changes.
        """    
        BaseMo._resetProps(self)

    def __getattr__(self, propName):
        """
        Returns a managed object (MO) attribute.
        """    
        return BaseMo.__getattr__(self, propName)

    def __setattr__(self, propName, propValue):
        """
        Sets a managed object (MO) attribute.
        """    
        BaseMo.__setattr__(self, propName, propValue)

    def __hash__(self):
        return hash(self.dn)


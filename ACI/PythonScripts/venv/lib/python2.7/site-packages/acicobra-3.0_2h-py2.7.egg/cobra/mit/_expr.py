# Copyright (c) '2015' Cisco Systems, Inc. All Rights Reserved


class Expression(object):
    def __init__(self):
        pass

    def evaluate(self, mo):
        raise NotImplementedError()


def eq(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) == lValue


def ne(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) != lValue


def gt(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) > lValue


def lt(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) < lValue


def ge(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) >= lValue


def le(mo, className, propName, lValue):
    return mo.meta.moClassName == className and getattr(mo, propName, None) <= lValue


def wcard(mo, className, propName, lValue):
    if mo.meta.moClassName == className:
        pVal = getattr(mo, propName, None)
        if pVal is not None:
            return lValue in pVal

    return False


class MoPropExpr(Expression):
    def __init__(self, className, propName, lValue, opFunc):
        self.className = className
        self.propName = propName
        self.lValue = lValue
        self.opFunc = opFunc

    def evaluate(self, mo):
        return self.opFunc(mo, self.className, self.propName, self.lValue)


class CompositeExpression(Expression):
    def __init__(self, eList):
        self.expressionList = eList

    def evaluate(self, mo):
        raise NotImplementedError()


class And(CompositeExpression):
    def __init__(self, eList):
        super(And, self).__init__(eList)

    def evaluate(self, mo):
        for expression in self.expressionList:
            if not expression.evaluate(mo):
                return False
        return True


class Or(CompositeExpression):
    def __init__(self, eList):
        super(Or, self).__init__(eList)

    def evaluate(self, mo):
        for expression in self.expressionList:
            if expression.evaluate(mo):
                return True
        return False


class Not(Or):
    def __init__(self, eList):
        super(Not, self).__init__(eList)

    def evaluate(self, mo):
        return not super(Not, self).evaluate(mo)

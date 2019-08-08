# Copyright (c) '2015' Cisco Systems, Inc. All Rights Reserved

from ._expr import MoPropExpr, And, Or, Not
from ._expr import eq, ne, gt, ge, lt, le, wcard
from codetalker.pgm import Grammar, Translator
from codetalker.pgm.tokens import STRING, ID, NUMBER, CharToken, WHITE, NEWLINE, re, StringToken, ReToken
from codetalker.pgm.special import commas


## TOKENS
class OP(StringToken):
    strings = ['eq', 'ne', 'gt', 'ge', 'le', 'lt', 'and', 'or', 'wcard', 'not']
    composite = ['and', 'or', 'not']
    num = 8


class SYMBOL(CharToken):
    chars = '().,'
    num = 4


def className(rule):
    rule | (ID)
    rule.astAttrs = {
        "id": ID
    }


className.astName = 'ClassName'


def propertyName(rule):
    rule | (className, '.', ID)
    rule.astAttrs = {
        'className': className,
        'propertyName': ID
    }


propertyName.astName = 'PropertyName'


def value(rule):
    rule | STRING
    rule.astAttrs = {
        "string": STRING
    }


value.astName = 'Value'


def expression(rule):
    rule | (OP, '(', propertyName, ',', value, ')')
    rule.astAttrs = {
        'operator': OP,
        'propertyName': propertyName,
        'value': value
    }


expression.astName = 'Expression'


def subExpression(rule):
    rule | expression | compositeExpression
    rule.astAttrs = {
        'expression': expression,
        'compositeExpression': compositeExpression
    }


subExpression.astName = "SubExpression"


def expressionList(rule):
    rule | [commas(subExpression)]
    rule.astAttrs = {
        'expressions': [subExpression]
    }


expressionList.astName = 'ExpressionList'


def compositeExpression(rule):
    rule | expression | (OP, '(', expressionList, ')')
    rule.astAttrs = {
        'operator': OP,
        'expressionList': expressionList,
        'expression': expression
    }


compositeExpression.astName = 'CompositeExpression'

grammar = Grammar(start=compositeExpression, tokens=[SYMBOL, OP],
                  ignore=[WHITE, NEWLINE], ast_tokens=[STRING])
filterParser = Translator(grammar)
ast = grammar.ast_classes

opTable = {
    'and': And,
    'or': Or,
    'not': Not,
    'eq': eq,
    'ne': ne,
    'lt': lt,
    'gt': gt,
    'ge': ge,
    'le': le,
    'wcard': wcard
}


@filterParser.translates(ast.ClassName)
def translateClassName(node):
    return filterParser.translate(node.id)


@filterParser.translates(ast.PropertyName)
def translatePropertyName(node):
    return filterParser.translate(node.className), filterParser.translate(node.propertyName)


@filterParser.translates(ast.Value)
def translateValue(node):
    return filterParser.translate(node.string).strip('"')


@filterParser.translates(ast.Expression)
def translateExpression(node):
    operator = filterParser.translate(node.operator)
    if operator in OP.composite:
        raise ValueError('Invalid leaf operator %s' % operator)
    className, propName = filterParser.translate(node.propertyName)
    value = filterParser.translate(node.value)
    return MoPropExpr(className, propName, value, opTable[operator])


@filterParser.translates(ast.SubExpression)
def translateSubExpression(node):
    if node.expression:
        return filterParser.translate(node.expression)
    else:
        return filterParser.translate(node.compositeExpression)


@filterParser.translates(ast.ExpressionList)
def translateExpressionList(node):
    return [filterParser.translate(expr) for expr in node.expressions]


@filterParser.translates(ast.CompositeExpression)
def translateCompositeExpression(node):
    if node.expression:
        compExpr = filterParser.translate(node.expression)
    else:
        operator = filterParser.translate(node.operator)
        opClass = opTable[operator]
        eList = filterParser.translate(node.expressionList)
        compExpr = opClass(eList)
    return compExpr

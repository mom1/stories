from stories import Success, story


# Mixins.


class WrongMethod(object):
    def one(self, ctx):
        return Success(foo="<boom>")


class UnknownMethod(object):
    def one(self, ctx):
        return Success(bar="1")


# Parent mixins.


class NormalParentMethod(object):
    def before(self, ctx):
        return Success()

    def after(self, ctx):
        return Success()


# Base classes.


class Child(object):
    @story
    def x(I):
        I.one

    contract = x.contract({"foo": lambda value: isinstance(value, int)})


class ParentWithNull(object):
    @story
    def a(I):
        I.before
        I.x
        I.after
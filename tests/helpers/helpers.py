import stories._context


def make_collector():

    storage = []

    origin_context_init = stories._context.Context.__init__

    def wrapper(ctx, ns, history):
        origin_context_init(ctx, ns, history)
        storage.append(ctx)

    stories._context.Context.__init__ = wrapper

    def getter():
        length = len(storage)
        error_message = "Context() was called {length} times".format(length=length)
        assert length == 1, error_message
        return storage[0]

    return getter

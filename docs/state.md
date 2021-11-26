# State

It's hard to figure out what variables could be set by story. Or what arguments
it does expect as input. It is possible to make this state contract explicit.
You could inherit from `State` class and define allowed variables and arguments
on it.

## Principles

- [Attribute assignment validates variable value](#attribute-assignment-validates-variable-value)
- [Validation errors are propagated as usual errors](#validation-errors-are-propagated-as-usual-errors)
- [Validation could normalize value](#validation-could-normalize-value)
- [State union joins all defined variables](#state-union-joins-all-defined-variables)

### Attribute assignment validates variable value

When story step assign attributes to the state, validator passed to the
`Variable` would be applied to the value.

Validator is a function of single argument. It should return attribute value or
raise exception if value is wrong.

If validator returns a value, it will be assigned to the state attribute.

=== "sync"

    ```pycon

    >>> from dataclasses import dataclass
    >>> from typing import Callable
    >>> from stories import Story, I, State, Variable
    >>> from app.repositories import load_order
    >>> from app.entities import Order

    >>> def is_order(value):
    ...     if isinstance(value, Order):
    ...         return value
    ...     else:
    ...         raise Exception(f"{value!r} is not valid order")

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...
    ...     def find_order(self, state):
    ...         state.order = self.load_order(state.order_id)
    ...
    ...     load_order: Callable

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)

    >>> purchase = Purchase(load_order=load_order)

    >>> state = PurchaseState(order_id=1)

    >>> purchase(state)

    >>> state.order
    Order(product=Product(name='Books'), cost=Cost(at=datetime.datetime(1999, 12, 31, 0, 0), amount=7))

    ```

=== "async"

    ```pycon

    >>> import asyncio
    >>> from dataclasses import dataclass
    >>> from typing import Coroutine
    >>> from stories import Story, I, State, Variable
    >>> from aioapp.repositories import load_order
    >>> from aioapp.entities import Order

    >>> def is_order(value):
    ...     if isinstance(value, Order):
    ...         return value
    ...     else:
    ...         raise Exception(f'{value!r} is not valid order')

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...
    ...     async def find_order(self, state):
    ...         state.order = await self.load_order(state.order_id)
    ...
    ...     load_order: Coroutine

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)

    >>> purchase = Purchase(load_order=load_order)

    >>> state = PurchaseState(order_id=1)

    >>> asyncio.run(purchase(state))

    >>> state.order
    Order(product=Product(name='Books'), cost=Cost(at=datetime.datetime(1999, 12, 31, 0, 0), amount=7))

    ```

### Validation errors are propagated as usual errors

If validation function raises exception, story execution would stops. It would
be propagated as usual exception which could happend inside the step.

=== "sync"

    ```pycon

    >>> from dataclasses import dataclass
    >>> from typing import Callable
    >>> from stories import Story, I, State, Variable

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...
    ...     def find_order(self, state):
    ...         state.order = self.load_order(state.order_id)
    ...
    ...     load_order: Callable

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)

    >>> purchase = Purchase(load_order=lambda order_id: None)

    >>> state = PurchaseState(order_id=1)

    >>> purchase(state)
    Traceback (most recent call last):
      ...
    Exception: None is not valid order

    ```

=== "async"

    ```pycon

    >>> import asyncio
    >>> from dataclasses import dataclass
    >>> from typing import Coroutine
    >>> from stories import Story, I, State, Variable

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...
    ...     async def find_order(self, state):
    ...         state.order = await self.load_order(state.order_id)
    ...
    ...     load_order: Coroutine

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)

    >>> async def load_order(order_id):
    ...     pass

    >>> purchase = Purchase(load_order=load_order)

    >>> state = PurchaseState(order_id=1)

    >>> asyncio.run(purchase(state))
    Traceback (most recent call last):
      ...
    Exception: None is not valid order

    ```

### Validation could normalize value

Validator function could cast value passed to it to the new type. It's a similar
process to normalization common to API schema libraries. To convert passed value
to something new, just return new thing. New value returned by validator
function would be assigned to the state attribute.

=== "sync"

    ```pycon

    >>> from dataclasses import dataclass
    >>> from typing import Callable
    >>> from stories import Story, I, State
    >>> from app.entities import Customer

    >>> def is_customer(value):
    ...     if isinstance(value, dict) and value.keys() == {'balance'} and isinstance(value['balance'], int):
    ...         return Customer(value['balance'])
    ...     else:
    ...         raise Exception(f'{value!r} is not valid customer')

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_customer
    ...
    ...     def find_customer(self, state):
    ...         state.customer = self.load_customer(state.customer_id)
    ...
    ...     load_customer: Callable

    >>> class PurchaseState(State):
    ...     customer = Variable(is_customer)

    >>> def load_customer(customer_id):
    ...     return {'balance': 100}

    >>> purchase = Purchase(load_customer=load_customer)

    >>> state = PurchaseState(customer_id=1)

    >>> purchase(state)

    >>> state.customer
    Customer(balance=100)

    ```

=== "async"

    ```pycon

    >>> import asyncio
    >>> from dataclasses import dataclass
    >>> from typing import Coroutine
    >>> from stories import Story, I, State, Variable
    >>> from app.entities import Customer

    >>> def is_customer(value):
    ...     if isinstance(value, dict) and value.keys() == {'balance'} and isinstance(value['balance'], int):
    ...         return Customer(value['balance'])
    ...     else:
    ...         raise Exception(f'{value!r} is not valid customer')

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_customer
    ...
    ...     async def find_customer(self, state):
    ...         state.customer = await self.load_customer(state.customer_id)
    ...
    ...     load_customer: Coroutine

    >>> class PurchaseState(State):
    ...     customer = Variable(is_customer)

    >>> async def load_customer(customer_id):
    ...     return {'balance': 100}

    >>> purchase = Purchase(load_customer=load_customer)

    >>> state = PurchaseState(customer_id=1)

    >>> asyncio.run(purchase(state))

    >>> state.customer
    Customer(balance=100)

    ```

### State union joins all defined variables

Story composition requires complicated state object which would define variables
necessary for both stories. If you defined separate state classes for both
stories, you could join variables with `State` union operation.

State union would include all variables defined in separate State classes.

=== "sync"

    ```pycon

    >>> from dataclasses import dataclass
    >>> from typing import Callable
    >>> from stories import Story, I, State, Variable
    >>> from app.repositories import load_order, load_customer, create_payment
    >>> from app.entities import Order, Customer, Payment

    >>> def is_order(value):
    ...     assert isinstance(value, Order)
    ...     return value

    >>> def is_customer(value):
    ...     assert isinstance(value, Customer)
    ...     return value

    >>> def is_payment(value):
    ...     assert isinstance(value, Payment)
    ...     return value

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...     I.find_customer
    ...     I.pay
    ...
    ...     def find_order(self, state):
    ...         state.order = self.load_order(state.order_id)
    ...
    ...     def find_customer(self, state):
    ...         state.customer = self.load_customer(state.customer_id)
    ...
    ...     load_order: Callable
    ...     load_customer: Callable
    ...     pay: Story

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)
    ...     customer = Variable(is_customer)

    >>> @dataclass
    ... class Pay(Story):
    ...     I.persist_payment
    ...
    ...     def persist_payment(self, state):
    ...         state.payment = self.create_payment(
    ...             order_id=state.order_id, customer_id=state.customer_id
    ...         )
    ...
    ...     create_payment: Callable

    >>> class PayState(State):
    ...     payment = Variable(is_payment)

    >>> pay = Pay(create_payment=create_payment)

    >>> purchase = Purchase(
    ...     load_order=load_order,
    ...     load_customer=load_customer,
    ...     pay=pay,
    ... )

    >>> state_class = PurchaseState & PayState

    >>> state = state_class(order_id=1, customer_id=1)

    >>> purchase(state)

    >>> state.payment
    Payment(due_date=datetime.datetime(1999, 12, 31, 0, 0))

    ```

=== "async"

    ```pycon

    >>> import asyncio
    >>> from dataclasses import dataclass
    >>> from typing import Coroutine
    >>> from stories import Story, I, State, Variable
    >>> from aioapp.repositories import load_order, load_customer, create_payment
    >>> from aioapp.entities import Order, Customer, Payment

    >>> def is_order(value):
    ...     assert isinstance(value, Order)
    ...     return value

    >>> def is_customer(value):
    ...     assert isinstance(value, Customer)
    ...     return value

    >>> def is_payment(value):
    ...     assert isinstance(value, Payment)
    ...     return value

    >>> @dataclass
    ... class Purchase(Story):
    ...     I.find_order
    ...     I.find_customer
    ...     I.pay
    ...
    ...     async def find_order(self, state):
    ...         state.order = await self.load_order(state.order_id)
    ...
    ...     async def find_customer(self, state):
    ...         state.customer = await self.load_customer(state.customer_id)
    ...
    ...     load_order: Callable
    ...     load_customer: Callable
    ...     pay: Story

    >>> @dataclass
    ... class Pay(Story):
    ...     I.persist_payment
    ...
    ...     async def persist_payment(self, state):
    ...         state.payment = await self.create_payment(
    ...             order_id=state.order_id, customer_id=state.customer_id
    ...         )
    ...
    ...     create_payment: Callable

    >>> class PurchaseState(State):
    ...     order = Variable(is_order)
    ...     customer = Variable(is_customer)

    >>> class PayState(State):
    ...     payment = Variable(is_payment)

    >>> pay = Pay(create_payment=create_payment)

    >>> purchase = Purchase(
    ...     load_order=load_order,
    ...     load_customer=load_customer,
    ...     pay=pay,
    ... )

    >>> state_class = PurchaseState & PayState

    >>> state = state_class(order_id=1, customer_id=1)

    >>> asyncio.run(purchase(state))

    >>> state.payment
    Payment(due_date=datetime.datetime(1999, 12, 31, 0, 0))

    ```

<p align="center">&mdash; ⭐ &mdash;</p>
<p align="center"><i>The <code>stories</code> library is part of the SOLID python family.</i></p>
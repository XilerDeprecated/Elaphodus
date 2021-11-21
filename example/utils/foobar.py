"""Handles your foobar like no other!"""


class FooBar:
    def __init__(self, amount: int):
        self.amount = amount

    def __call__(self):
        return self.construct(self.amount)

    @staticmethod
    def construct(amount: int) -> str:
        # TODO: Figure a way out to properly let users document parameters & return values
        """Constructs a FooBar"""
        return ("foobar\n" * amount).strip()

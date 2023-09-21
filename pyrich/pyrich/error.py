class EmptySymbolError(Exception):
    pass


class ArrayLengthDoesNotMatchError(Exception):
    pass


class SearchError(Exception):
    pass


class CurrencyError(Exception):
    pass


class UnknownFormat(Exception):
    pass


class InvalidInputFormatError(Exception):

    def __init__(self, input_: str, input_type: str,
                 expected_input: str, example: str) -> None:
        self.input_ = input_
        self.input_type = input_type
        self.expected_input = expected_input
        self.example = example
        super().__init__(self.message)

    @property
    def message(self) -> str:
        message = (f"Invalid input '{self.input_}'. '{self.input_type}' format "
                   f"must be in {self.expected_input} e.g. {self.example}")
        return message


class ZeroValueError(Exception):
    pass

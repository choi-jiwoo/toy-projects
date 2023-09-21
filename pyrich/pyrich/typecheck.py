from datetime import datetime
import re
from pyrich.error import InvalidInputFormatError
from pyrich.error import ZeroValueError


class Date:

    def __init__(self, name: str, date: str) -> None:
        self.name = name
        self.date = date

    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, date: str) -> None:
        try:
            self._date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise InvalidInputFormatError(
                input_=date,
                input_type=self.name,
                expected_input='%Y-%m-%d',
                example='2022-2-12',
            ) from None


class Country:

    def __init__(self, name: str, country: str) -> None:
        self.name = name
        self.country = country

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, country: str) -> None:
        try:
            self._country = re.search(r'\b[A-Z]{3}\b', country).group()
        except AttributeError:
            raise InvalidInputFormatError(
                input_=country,
                input_type=self.name,
                expected_input='alpha-3 code (ISO 3166)',
                example='USA',
            ) from None


class Type:

    TYPE = {
        'b': 'buy',
        's': 'sell',
    }

    def __init__(self, name: str, type_: str) -> None:
        self.name = name
        self.type_ = type_

    @property
    def type_(self) -> str:
        return self._type_
    
    @type_.setter
    def type_(self, type_: str) -> None:
        try:
            self._type_ = Type.TYPE[type_]
        except KeyError:
            raise InvalidInputFormatError(
                input_=type_,
                input_type=self.name,
                expected_input="'b' for buy or 's' for sell",
                example="'b' or 's'",
            ) from None 

class Float:

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        try:
            self._value = float(value)
            self.check_zero_value()
        except ValueError:
            raise InvalidInputFormatError(
                input_=value,
                input_type=self.name,
                expected_input='real number',
                example='1, 123.45',
            ) from None

    def check_zero_value(self) -> None:
        if self.value == 0:
            raise ZeroValueError(
                f"'0' is not a valid input for argument '{self.name}'."
            )

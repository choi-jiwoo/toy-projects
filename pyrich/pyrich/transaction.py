from pyrich.typecheck import Date
from pyrich.typecheck import Country
from pyrich.typecheck import Type
from pyrich.typecheck import Float


class Transaction:

    def __init__(self, record: list, headers: list) -> None:
        self.headers = headers
        self.record = record

    @property
    def record(self) -> dict:
        return self._record

    @record.setter
    def record(self, record: list) -> None:
        mapped_record = zip(self.headers, record)
        mapped_record = {
            header: item
            for header, item in mapped_record
        }
        self._record = self._typecheck_and_convert(mapped_record)

    def _typecheck_and_convert(self, record: dict) -> dict:
        for key, value in record.items():
            match key:
                case 'date':
                    date_ = Date(key, value)
                    record[key] = date_.date
                case 'country':
                    country_ = value.upper()
                    country_ = Country(key, country_)
                    record[key] = country_.country
                case 'type':
                    transaction_type = Type(key, value.lower())
                    record[key] = transaction_type.type_
                case 'symbol' | 'currency':
                    record[key] = record[key].upper()
                case 'quantity' | 'price' | 'dividend':
                    float_value = Float(key, value)
                    record[key] = float_value.value
                case _:
                    continue
        return record

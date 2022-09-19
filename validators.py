from abc import abstractmethod, ABCMeta
from typing import Generic, TypeVar


T = TypeVar('T')


class ValidatorBase(Generic[T], metaclass=ABCMeta):
    def __init__(self, value: T) -> None:
        self._value = value

    @abstractmethod
    def is_valid(self) -> bool:
        raise NotImplementedError


class RtsfUrlValidator(ValidatorBase[str]):
    def is_valid(self) -> bool:
        return True

class PhoneValidator(ValidatorBase[str]):
    def is_valid(self) -> bool:
        return True

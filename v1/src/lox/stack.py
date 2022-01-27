from typing import List, TypeVar, Generic, Iterator

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()

    def empty(self) -> bool:
        return not self.items

    def peek(self) -> T:
        return self.items[-1]

    def __len__(self) -> int:
        return self.items.__len__()

    def __iter__(self) -> Iterator[T]:
        return self.items.__iter__()

    def __getitem__(self, key: int) -> T:
        return self.items[key]

from abc import ABC, abstractclassmethod
from dataclasses import dataclass


class Sampler(ABC):
    """
    Sampler Interface

    Any sampler needs to work with:
    - random.choice
    - for loops, enumerate...
    """
    @abstractclassmethod
    def __len__(self):
        ...

    @abstractclassmethod
    def __iter__(self):
        ...

    @abstractclassmethod
    def __getitem__(self):
        ...


@dataclass
class RandomSampler(Sampler):
    count: int = 25

    def __len__(self):
        return self.count

    def __iter__(self):
        return iter((self[i] for i in range(len(self))))

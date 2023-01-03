from abc import ABC, abstractclassmethod


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


class RandomSampler(Sampler):
    def __len__(self):
        return 100

    def __iter__(self):
        return iter((self[0], ))

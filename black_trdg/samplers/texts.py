from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from typing import Tuple, Optional
from functools import lru_cache, cached_property
import random
import toolz


@dataclass(frozen=True, eq=True)
class VocabSampler(ABC):
    max_length: int
    vocab: Optional[str] = None
    vocab_file: Optional[str] = None
    encoding: str = 'utf-8'

    @cached_property
    def _vocab(self):
        if self.vocab is not None:
            return self.vocab
        elif self.vocab_file is not None:
            with open(self.vocab_file, encoding=self.encoding) as f:
                return ''.join(set(f.read()))
        else:
            raise RuntimeError("Either vocab or vocab_file must present")

    @cached_property
    def vocab_size(self):
        return len(self._vocab)

    @abstractclassmethod
    def __len__(self):
        ...

    @abstractclassmethod
    def __getitem__(self, *a, **k):
        ...


@dataclass(frozen=True, eq=True)
class VocabRep(VocabSampler):
    max_length: int

    @lru_cache
    def __len__(self):
        return self.nz_vocab_size * self.max_length

    @cached_property
    def nz_vocab(self):
        return self._vocab.replace("\n", "").replace("\t", "").replace(" ", "")

    @cached_property
    def nz_vocab_size(self):
        return len(self.nz_vocab)

    @lru_cache
    def __getitem__(self, i):
        # A grid like structure
        # where sampler[i, j] = chars[j] at #i length
        # samples shape is [max_length, n_vocabs]
        text_length = (i % self.max_length) + 1
        char_index = (i // self.max_length)
        return self.nz_vocab[char_index] * text_length


@dataclass(frozen=True, eq=True)
class VocabRand(VocabSampler):
    max_length: int
    min_length: int = 1

    @lru_cache
    def __len__(self):
        return (self.vocab_size) * (self.max_length + self.min_length) // 2

    def __iter__(self):
        for i in range(len(self)):
            yield self[0]

    def __getitem__(self, i):
        k = random.randint(self.min_length, self.max_length)
        text = ''.join(random.choices(self._vocab, k=k))
        return text


@dataclass(frozen=True, eq=True)
class TextFile:
    file: str
    encoding: str = 'utf-8'

    @cached_property
    def lines(self):
        with open(self.file, encoding=self.encoding) as f:
            lines = [line.strip() for line in f.readlines()]
        return lines

    @lru_cache
    def __len__(self):
        return len(self.lines)

    @lru_cache
    def __getitem__(self, i):
        return self.lines[i]


@dataclass
class LongTextFile:
    file: str
    min_length: int
    max_length: int
    encoding: str = 'utf-8'
    delim: str = '\n'

    @cached_property
    def queue(self):
        from queue import Queue
        return Queue()

    @cached_property
    def io(self):
        return open(self.file, self.encoding)

    def __len__(self):
        return 1000000

    def __getitem__(self, i):
        while self.queue.qsize() == 0:
            line = self.io.readline()
            if line == '':
                reset = True
                for i in range(5):
                    line = self.io.readline()
                    if line != '':
                        reset = False
                        break
                if reset:
                    self.io.seek(0)
                    line = self.io.readline()
            line = line.replace("\t", " ").replace("\n", " ").strip()
            splits = max_size_split(line, self.min_length, self.max_length)
            for split in splits:
                split = split.strip()
                if len(split) == 0:
                    continue
                self.queue.put(split)

        s = self.queue.get()
        return s


def max_size_split(line, a, b):
    n = len(line)
    if n <= b:
        return [line]

    mod = -1
    length = None
    for i in range(a, b+1):
        mod_ = n % i
        if mod_ == 0:
            length = i
            break
        if mod_ > mod:
            length = i
            mod = mod_

    words = toolz.partition_all(length, line)
    words = [''.join(word) for word in words]
    return words

from .texts import VocabRep, VocabRand
from .bg import Color, ImageDir
from .other import FontDir, FontFile


class CombineSampler:
    def __init__(self, samplers):
        self.samplers = samplers
        self.lens = list(map(len, self.samplers))
        self.n_samplers = len(samplers)
        for i, l in enumerate(self.lens):
            if l < 1:
                raise RuntimeError(f"sampler {samplers[i]} has length {l}")

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return max(self.lens) * self.n_samplers

    def __getitem__(self, idx):
        sampler_idx = idx % self.n_samplers
        sample_idx = (idx // self.n_samplers) % self.lens[sampler_idx]
        # try:
        return self.samplers[sampler_idx][sample_idx]
        # except Exception:
        #     s = self.samplers[sampler_idx]
        #     print("+"*300)
        #     print(s, len(s), s[sample_idx])
        #     print("+"*300)
        #     return

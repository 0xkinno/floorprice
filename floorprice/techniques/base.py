"""Common interface for all seven techniques."""
from abc import ABC, abstractmethod

from ..receipt import make_receipt


class Technique(ABC):
    id = "T?"
    name = "technique"
    version = "0.1.0"
    recompute_cmd = "make reproduce"

    @abstractmethod
    def score(self, source) -> float:
        """Score in [0, 1]. NaN means the technique produced no score (for example a parse failure)."""

    @abstractmethod
    def threshold(self) -> float:
        """The technique's own 'reliable' cut: the median score it gives the real pc1 >= 0.7 band,
        or its documented cut."""

    def crosses(self, source) -> bool:
        s = self.score(source)
        return s == s and s >= self.threshold()

    def inputs(self, source) -> dict:
        return {"source": str(source)}

    def receipt(self, source) -> dict:
        return make_receipt(str(source), self.id, self.version, self.inputs(source),
                            self.score(source), self.threshold(), self.recompute_cmd)

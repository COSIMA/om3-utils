from pathlib import Path

from om3utils.profiling import ProfilingParser
from om3utils.esmf_trace import ESMFTrace, MultiPETTimingNode


class ESMFProfilingParser(ProfilingParser):
    def __init__(self, dirname):
        # ESMF provides the following metrics:
        super().__init__()
        self._metrics = ["hits", "tmin", "tmax", "tavg", "ttot"]
        self._dirname = dirname

    @property
    def metrics(self) -> list:
        return self._metrics

    def read(self, path: Path) -> dict:
        profiling_dir = path / self._dirname
        if not profiling_dir.is_dir():
            raise FileNotFoundError(f"Directory not found: {profiling_dir.as_posix()}")

        trace = ESMFTrace(profiling_dir)

        stats = {"region": trace.regions}
        stats.update({key: [0] * len(trace.regions) for key in self.metrics})

        for name, child in trace.multiPETTree.children.items():
            self._add_node_stats(child, name, stats)

        return stats

    def _add_node_stats(self, node: MultiPETTimingNode, name: str, stats: dict):
        index = stats["region"].index(name)
        stats["hits"][index] += node.count_each
        stats["tmin"][index] += node.total_min_s
        stats["tmax"][index] += node.total_max_s
        stats["tavg"][index] += node.total_mean_s
        stats["ttot"][index] += node.total_sum_s

        for name, child in node.children.items():
            self._add_node_stats(child, name, stats)

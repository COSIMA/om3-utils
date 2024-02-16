from pathlib import Path
import xarray as xr

from om3utils.payu_config_yaml import read_payu_config_yaml


def scaling_ncpus(run_dir):
    config_file = Path(run_dir) / "config.yaml"
    config = read_payu_config_yaml(config_file.as_posix())
    return config["ncpus"]


def scaling_speedup(stats: xr.Dataset) -> xr.Dataset:
    speedup = stats.tavg.sel(ncpus=stats["ncpus"].min()) / stats.tavg
    speedup.name = "speedup"
    return speedup


def scaling_efficiency(stats: xr.Dataset) -> xr.Dataset:
    speedup = scaling_speedup(stats)
    eff = speedup / speedup.ncpus * 100 * stats["ncpus"].min()
    eff.name = "parallel efficiency [%]"
    return eff

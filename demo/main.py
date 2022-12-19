""" Main process """
import argparse
from datetime import datetime
from time import sleep
from typing import Optional
from pyummeter import (
    UMmeter,
    UMmeterInterface,
    UMmeterInterfaceTTY,
    UMmeterInterfaceBT
)
from pyummeter.export_csv import ExportCSV


def parse_args():
    """ Parse input arguments """
    args = argparse.ArgumentParser()
    args.add_argument("--tty", "-t", type=str, default=None,
                      help="Serial interface")
    args.add_argument("--bluetooth", "-b", type=str, default=None,
                      help="BT interface")
    args.add_argument("--refresh", "-r", type=float, default=1.0,
                      help="Refresh period between each data dump")
    args.add_argument("--export", "-e", type=str, default="",
                      help="CSV export file")
    return args.parse_args()


if __name__ == "__main__":
    params = parse_args()
    # Check interface.
    if params.tty is None and params.bluetooth is None:
        print("No interface provided")
        exit(1)
    if params.tty is not None and params.bluetooth is not None:
        print("Multiple interface provided")
        exit(1)
    interface: Optional[UMmeterInterface] = None
    if params.tty is not None:
        interface = UMmeterInterfaceTTY(params.tty)
    elif params.bluetooth is not None:
        interface = UMmeterInterfaceBT(params.bluetooth)
    assert interface is not None
    # Prepare export instance if required.
    export: Optional[ExportCSV] = None
    if params.export != "":
        export = ExportCSV(params.export)
    # Run data dump process.
    with UMmeter(interface) as meter:
        try:
            while True:
                data = meter.get_data()
                now = datetime.now()
                if export is not None:
                    export.update(now, data)
                print(
                    f"[{data['model']}] {now.time()}"
                    f" {data['voltage']:1.04f}V {data['intensity']:1.04f}A"
                    f" {data['power']:1.04f}W {data['resistance']}Ohm"
                )
                sleep(params.refresh)
        except KeyboardInterrupt:
            pass

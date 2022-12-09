""" Main process """
import argparse
from datetime import datetime
from time import sleep
from typing import Optional
from pyummeter.export_csv import ExportCSV
from pyummeter import UMmeter


def parse_args():
    """ Parse input arguments """
    args = argparse.ArgumentParser()
    args.add_argument("--tty", "-t", type=str, required=True,
                      help="Serial interface")
    args.add_argument("--refresh", "-r", type=float, default=1.0,
                      help="Refresh period between each data dump")
    args.add_argument("--export", "-e", type=str, default="",
                      help="CSV export file")
    return args.parse_args()


if __name__ == "__main__":
    params = parse_args()
    # Prepare export instance if required.
    export: Optional[ExportCSV] = None
    if params.export != "":
        export = ExportCSV(params.export)

    try:
        # Run data dump process.
        with UMmeter(params.tty) as meter:
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
        # Handle keyboard interrupt
        pass
    finally:
        meter.close()

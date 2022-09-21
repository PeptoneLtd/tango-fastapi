import datetime
import os
import re
import subprocess
import concurrent.futures

import logging
from contextlib import contextmanager
import platform
from typing import List, Dict, Any


logger = logging.getLogger(__name__)

header_re = re.compile(r'^res\s+aa\s+Beta\s+Turn\s+Helix\s+Aggregation\s+Conc-Stab_Aggregation\s*$')
line_re = re.compile(
    r'^(?P<res>\d+)\s+(?P<aa>\S+)\s+(?P<beta>\S+)\s+(?P<turn>\S+)\s+(?P<helix>\S+)\s+(?P<aggregation>\S+)\s+\S+\s*$')
error_re = re.compile(r'^ERROR:\s*(.*)')
tmp_path = "/tmp"

def producer(name: str = "p0", **kwargs) -> None:
    pl = platform.system()
    if pl == 'Darwin':
        cmd = "../bin/tango2_3_1_macosx"
    elif pl == 'Linux':
        cmd = "../bin/tango_x86_64_release"
    else:
        logger.critical(f"platform {pl} not supported")
        # write to pipe to avoid hanging consumer
        with open(f"{name}.txt", "w") as f:
            f.write(f"ERROR: platform {pl} not supported")
        return
    args = [cmd, name]
    args += [f"{k}={v}" for (k, v) in kwargs.items()]
    logger.debug(f"starting tango thread: {args}")
    try:
        subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        logger.error(f"error executing tango binary: {e.output}")
        # write to pipe to avoid hanging consumer
        with open(f"{name}.txt", "w") as f:
            f.write(f"ERROR: {e.output}")


def consumer(name: str = "p0") -> List[Dict[str, Any]]:
    logger.debug(f"opening named pipe {name}.txt")
    results = []
    with open(f"{name}.txt") as f:
        for line in f:
            if header_re.match(line):
                continue
            if error_re.match(line):
                raise Exception(line)
            m = line_re.match(line)
            if m is None:
                logger.error(f"can't parse tango result: {line}")
                break
            d = m.groupdict()
            d['res'] = int(d['res'])
            d['beta'] = float(d['beta']) / 100.0
            d['turn'] = float(d['turn']) / 100.0
            d['helix'] = float(d['helix']) / 100.0
            d['aggregation'] = float(d['aggregation']) / 100.0
            results.append(d)
    return results


@contextmanager
def fifo(path: str):
    logger.debug(f"creating named pipe {path}")
    os.mkfifo(path)
    try:
        yield
    finally:
        logger.debug(f"removing named pipe {path}")
        os.remove(path)


def run(name: str = "p0", **kwargs):
    name = os.path.join(tmp_path, f"{name}_{datetime.datetime.utcnow().isoformat()}")
    with fifo(f"{name}.txt"), concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        logger.debug("starting consumer")
        c = executor.submit(consumer, name=name)

        logger.debug("starting producer")
        p = executor.submit(producer, name=name, **kwargs)

        logger.debug("waiting producer and consumer")
        concurrent.futures.as_completed([p, c])
        return c.result()


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
    res = run(name='asd', ct='N', nt='N', ph='7.4', te=303, io=0.05, seq="GATTACA")
    print(res)

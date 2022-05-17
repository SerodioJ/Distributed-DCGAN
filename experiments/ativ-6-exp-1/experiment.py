import argparse
import os
import time

import fabric

PROJECT_FOLDER = "/home/ubuntu/Distributed-DCGAN/experiments/ativ-6-exp-1"


def init_env_file(con_group):
    for i, con in enumerate(con_group):
        con.run(
            f'cd {PROJECT_FOLDER} && echo "OMP_NUM_THREADS=1\nNODE_RANK={i}" > .env'
        )


def exec(
    con_group, master_addr: str, nnodes: int, nproc_per_node: int, batch_size: int
) -> list:
    start = time.perf_counter()
    results = con_group.run(
        f"cd {PROJECT_FOLDER} && docker run --env-file .env --rm --network=host -v=$(pwd):/root dist_dcgan:latest ./run.sh {nproc_per_node} {nnodes} {master_addr} {batch_size}"
    )
    end = time.perf_counter() - start
    csv_line = [end]
    if isinstance(results, dict):
        for _, res in results.items():
            csv_line.extend(res.stdout.strip()[:-1].split(","))
    else:
        csv_line.extend(results.stdout.strip()[:-1].split(","))
    return csv_line


def experiment(
    con_group,
    samples: int,
    master_addr: str,
    nnodes: int,
    nproc_per_node: int,
    batch_size: int,
):
    header = ["total"]
    header.extend([f"t{i}" for i in range(nnodes * nproc_per_node)])
    csv_lines = []
    for i in range(samples):
        print(
            f"Starting sample {i}/{samples} of nproc = {nproc_per_node}, batch_size={batch_size}"
        )
        csv_lines.append(
            exec(
                con_group=con_group,
                master_addr=master_addr,
                nnodes=nnodes,
                nproc_per_node=nproc_per_node,
                batch_size=batch_size,
            )
        )
        print(
            f"Finishing sample {i}/{samples} of nproc = {nproc_per_node}, batch_size={batch_size}"
        )
    with open(
        os.path.join(
            "results",
            f"nnode-{nnodes}_nproc-{nproc_per_node}_batch_size-{batch_size}.csv",
        ),
        "w",
    ) as f:
        f.write(",".join(header))
        f.write("\n")
        for line in csv_lines:
            f.write(",".join(list(map(str, line))))
            f.write("\n")


def experiment_all(hosts: list, batch_size: int, samples: int):
    con_group = fabric.ThreadingGroup(*hosts)
    init_env_file(con_group)
    for con in con_group:
        experiment(
            con,
            samples=samples,
            batch_size=batch_size,
            master_addr=hosts[0],
            nnodes=1,
            nproc_per_node=1,
        )
        break
    for proc in [1, 2, 4]:
        experiment(
            con_group,
            samples=samples,
            batch_size=batch_size,
            master_addr=hosts[0],
            nnodes=len(hosts),
            nproc_per_node=proc,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hosts",
        default=None,
        type=str,
        required=True,
        help="List of host IPs",
    )
    parser.add_argument(
        "--batch_size",
        default=16,
        type=int,
        required=False,
        help="Training Batch Size",
    )
    parser.add_argument(
        "--samples",
        default=3,
        type=int,
        required=False,
        help="Number of samples for each configuration",
    )

    args = parser.parse_args()

    hosts = args.hosts.split(",")  # improve IP parsing
    if not hosts:
        exit(1)
    experiment_all(
        hosts=hosts,
        batch_size=args.batch_size,
        samples=args.samples,
    )

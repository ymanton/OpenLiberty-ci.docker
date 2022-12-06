#!/usr/bin/env python3

import sys
import subprocess
import itertools
import argparse

p = argparse.ArgumentParser()
p.add_argument('-t', '--tag', required = True)

known_args, unknown_args = p.parse_known_args()

print(known_args)
print(unknown_args)
print(sys.argv)

pre_checkpoint_tag = f"{known_args.tag}-pre-checkpoint"

docker_build_args = ["docker", "build"] + ["-t", pre_checkpoint_tag] + unknown_args
try:
    subprocess.run(docker_build_args, check = True)
    pass
except subprocess.CalledProcessError as cpe:
    sys.exit(cpe.returncode)

docker_checkpoint_caps = [
    "--cap-add", "CAP_CHECKPOINT_RESTORE",
    "--cap-add", "CAP_SYS_PTRACE",
    "--cap-add", "CAP_NET_ADMIN"
]
docker_checkpoint_args = [
    "-d",
    "-e", "WLP_CHECKPOINT=applications",
    "--privileged"
]
docker_run_args = ["docker", "run"] + docker_checkpoint_caps + docker_checkpoint_args + [pre_checkpoint_tag]
try:
    chkpt = subprocess.run(docker_run_args, check = True, capture_output = True, text = True)
except subprocess.CalledProcessError as cpe:
    print(sys.stderr)
    sys.exit(cpe.returncode)

print(chkpt)

checkpoint_container_id = chkpt.stdout.rstrip()

docker_wait_args = ["docker", "wait", checkpoint_container_id]
try:
    subprocess.run(docker_wait_args, check = True)
except subprocess.CalledProcessError as cpe:
    sys.exit(cpe.returncode)

docker_commit_args = ["docker", "commit", checkpoint_container_id, known_args.tag]
print(docker_commit_args)
try:
    subprocess.run(docker_commit_args, check = True)
except subprocess.CalledProcessError as cpe:
    sys.exit(cpe.returncode)

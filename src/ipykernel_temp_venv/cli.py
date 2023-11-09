import argparse
import json
import os
import sys

from ipykernel.kernelspec import install

KERNEL_NAME = f"temp-venv-python{sys.version_info[0]}"


def main(args):
    parser = argparse.ArgumentParser(
        description="Create an IPython kernel launched within a temporary virtual "
        "environment"
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="Install for the current user instead of system-wide",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=KERNEL_NAME,
        help="Specify a name for the kernelspec."
        " This is needed to have multiple IPython kernels at the same time.",
    )
    parser.add_argument(
        "--display-name",
        type=str,
        help="Specify the display name for the kernelspec."
        " This is helpful when you have multiple IPython kernels.",
    )
    parser.add_argument(
        "--profile",
        type=str,
        help="Specify an IPython profile to load. "
        "This can be used to create custom versions of the kernel.",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        help="Specify an install prefix for the kernelspec."
        " This is needed to install into a non-default location, such as a "
        "conda/virtual-env.",
    )
    parser.add_argument(
        "--sys-prefix",
        action="store_const",
        const=sys.prefix,
        dest="prefix",
        help="Install to Python's sys.prefix."
        f" Shorthand for --prefix='{sys.prefix}'. For use in conda/virtual-envs.",
    )
    parser.add_argument(
        "--env",
        action="append",
        nargs=2,
        metavar=("ENV", "VALUE"),
        help="Set environment variables for the kernel.",
    )
    opts = parser.parse_args(args)
    if opts.env:
        opts.env = dict(opts.env)
    dest = install(
        user=opts.user,
        kernel_name=opts.name,
        profile=opts.profile,
        prefix=opts.prefix,
        display_name=opts.display_name,
        env=opts.env,
    )

    kernel_file = os.path.join(dest, "kernel.json")
    with open(kernel_file) as f:
        kernel_json = json.load(f)
    kernel_json["argv"] = ["{executable}"] + kernel_json["argv"][1:]
    kernel_json["metadata"]["kernel_provisioner"] = {
        "provisioner_name": "temp-venv-provisioner"
    }

    print(kernel_json)
    with open(kernel_file, "w") as f:
        kernel_json = json.dump(kernel_json, f, indent=2)
    print(f"Installed kernelspec {opts.name} in {dest}")


if __name__ == "__main__":
    main(sys.argv[1:])

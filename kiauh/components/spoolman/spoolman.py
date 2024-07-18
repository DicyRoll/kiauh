# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #


import json
import shutil
from os import chdir, getcwd
from pathlib import Path
from subprocess import run
from typing import List

from components.moonraker.moonraker import Moonraker
from components.spoolman import (
    SPOOLMAN_BACKUP_DIR,
    SPOOLMAN_DB_DIR,
    SPOOLMAN_DIR,
    SPOOLMAN_REPO,
)
from core.backup_manager.backup_manager import BackupManager
from core.instance_manager.instance_manager import InstanceManager
from utils.common import get_install_status
from utils.config_utils import (
    add_config_section,
    remove_config_section,
)
from utils.constants import SYSTEMD
from utils.fs_utils import remove_with_sudo, unzip
from utils.git_utils import get_latest_tag
from utils.input_utils import get_confirm
from utils.logger import Logger
from utils.sys_utils import cmd_sysctl_service, download_file, get_ipv4_addr
from utils.types import ComponentStatus

spoolman_port: int = 7912
spoolman_db: str = ""


def install_spoolman() -> None:
    mr_instances: List[Moonraker] = InstanceManager(Moonraker).instances

    dw_client = True
    if Path(SPOOLMAN_DIR).exists():
        question = f"'{SPOOLMAN_DIR}' already exists. Overwrite?"
        if not get_confirm(question, default_choice=False):
            Logger.print_info("Skip cloning of repository ...")
            dw_client = False
        else:
            shutil.rmtree(SPOOLMAN_DIR)

    try:
        if dw_client:
            setup_spoolman_dir()
        start_install_script()
    except Exception as e:
        Logger.print_error(f"Something went wrong! Please try again...\n{e}")
        return

    if mr_instances and get_confirm("Enable Moonraker integration?"):
        add_config_section(
            "spoolman",
            mr_instances,
            [
                ("server", f"http://{get_ipv4_addr()}:{spoolman_port}"),
            ],
        )

        add_config_section(
            "update_manager Spoolman",
            mr_instances,
            [
                ("type", "zip"),
                ("channel", "stable"),
                ("repo", "Donkie/Spoolman"),
                ("path", str(SPOOLMAN_DIR)),
                ("virtualenv", ".venv"),
                ("requirements", "requirements.txt"),
                ("persistent_files", "\n.venv\n.env"),
                ("managed_services", "Spoolman"),
            ],
        )

    cmd_sysctl_service("moonraker", "restart")


def update_spoolman() -> None:
    if not Path(SPOOLMAN_DIR).exists():
        Logger.print_info("Spoolman is not installed! Skipping ...")
        return

    cmd_sysctl_service("Spoolman", "stop")
    cmd_sysctl_service("Spoolman", "disable")

    Logger.print_status("Updating Spoolman ...")

    shutil.move(SPOOLMAN_DIR, f"{SPOOLMAN_DIR}.old")
    setup_spoolman_dir()
    # copy old .env
    shutil.copy(f"{SPOOLMAN_DIR}.old/.env", f"{SPOOLMAN_DIR}/.env")
    start_install_script()

    shutil.rmtree(f"{SPOOLMAN_DIR}.old")


def remove_spoolman() -> None:
    if Path(SPOOLMAN_DIR).exists():
        Logger.print_status("Removing spoolman service ...")
        cmd_sysctl_service("Spoolman", "stop")
        cmd_sysctl_service("Spoolman", "disable")
        remove_with_sudo(f"{SYSTEMD}/Spoolman.service")
        Logger.print_status("Removing service removed!")

        Logger.print_status("Removing spoolman directory ...")
        shutil.rmtree(SPOOLMAN_DIR)
        Logger.print_status("Directory removed!")

    if Path(SPOOLMAN_DB_DIR).exists():
        Logger.print_status("Removing spoolman database ...")
        shutil.rmtree(SPOOLMAN_DB_DIR)
        Logger.print_status("Database removed!")

    mr_instances: List[Moonraker] = InstanceManager(Moonraker).instances
    if mr_instances:
        remove_config_section("spoolman", mr_instances)
        remove_config_section("update_manager Spoolman", mr_instances)

    cmd_sysctl_service("moonraker", "restart")

    Logger.print_ok("Spoolman successfully removed!")


def backup_spoolman_dir() -> None:
    bm = BackupManager()
    bm.backup_directory("spoolman", SPOOLMAN_DIR, SPOOLMAN_BACKUP_DIR)
    bm.backup_directory("spoolman-db", SPOOLMAN_DB_DIR, SPOOLMAN_BACKUP_DIR)


def setup_spoolman_dir() -> None:
    Logger.print_status("Downloading Spoolman...")

    download_url = f"{SPOOLMAN_REPO}/latest/download/spoolman.zip"

    zip_path = Path.home().joinpath("spoolman.zip")
    download_file(download_url, zip_path)
    unzip(zip_path, SPOOLMAN_DIR)
    zip_path.unlink()

    run(["chmod", "+x", f"{SPOOLMAN_DIR}/scripts/install.sh"], check=True)


def start_install_script() -> None:
    kiauh_dir = getcwd()
    # change cwd to spoolman to not mess with install.sh context
    chdir(SPOOLMAN_DIR)
    run(["chmod", "+x", f"{SPOOLMAN_DIR}/scripts/install.sh"], check=True)
    run(f"{SPOOLMAN_DIR}/scripts/install.sh", shell=True, check=True)
    # reset cwd
    chdir(kiauh_dir)


def get_spoolman_status() -> ComponentStatus:
    status = get_install_status(
        SPOOLMAN_DIR,
        files=[
            Path(SPOOLMAN_DB_DIR),
            Path(f"{SYSTEMD}/Spoolman.service"),
        ],
    )

    if Path(SPOOLMAN_DIR).exists():
        with open(Path(SPOOLMAN_DIR) / "release_info.json") as f:
            data = json.load(f)
        local_version = data["version"]
        status.local = local_version

    remote_version = get_latest_tag("Donkie/Spoolman")
    status.remote = remote_version

    return status

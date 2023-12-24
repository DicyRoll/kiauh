#!/usr/bin/env python3

# ======================================================================= #
#  Copyright (C) 2020 - 2023 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

import json
import os
import shutil
from pathlib import Path
from typing import List

from kiauh.core.backup_manager.backup_manager import BackupManager
from kiauh.modules.klipper.klipper import Klipper
from kiauh.modules.mainsail import MAINSAIL_CONFIG_JSON
from kiauh.utils.logger import Logger


def backup_config_json(is_temp=False) -> None:
    Logger.print_status(f"Backup '{MAINSAIL_CONFIG_JSON}' ...")
    bm = BackupManager()
    if is_temp:
        fn = Path(Path.home(), "config.json.kiauh.bak")
        bm.backup_file([MAINSAIL_CONFIG_JSON], custom_filename=fn)
    else:
        bm.backup_file([MAINSAIL_CONFIG_JSON])


def restore_config_json() -> None:
    try:
        Logger.print_status(f"Restore '{MAINSAIL_CONFIG_JSON}' ...")
        source = os.path.join(Path.home(), "config.json.kiauh.bak")
        shutil.copy(source, MAINSAIL_CONFIG_JSON)
    except OSError:
        Logger.print_info("Unable to restore config.json. Skipped ...")


def enable_mainsail_remotemode() -> None:
    with open(MAINSAIL_CONFIG_JSON, "r") as f:
        config_data = json.load(f)

    if config_data["instancesDB"] == "browser":
        return

    Logger.print_status("Setting instance storage location to 'browser' ...")
    config_data["instancesDB"] = "browser"

    with open(MAINSAIL_CONFIG_JSON, "w") as f:
        json.dump(config_data, f, indent=4)


def symlink_webui_nginx_log(klipper_instances: List[Klipper]) -> None:
    Logger.print_status("Link NGINX logs into log directory ...")
    access_log = Path("/var/log/nginx/mainsail-access.log")
    error_log = Path("/var/log/nginx/mainsail-error.log")

    for instance in klipper_instances:
        desti_access = Path(instance.log_dir).joinpath("mainsail-access.log")
        if not desti_access.exists():
            desti_access.symlink_to(access_log)

        desti_error = Path(instance.log_dir).joinpath("mainsail-error.log")
        if not desti_error.exists():
            desti_error.symlink_to(error_log)

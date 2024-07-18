# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

import textwrap
from typing import Optional, Type

from components.crowsnest.crowsnest import install_crowsnest
from components.klipper import klipper_setup
from components.klipperscreen.klipperscreen import install_klipperscreen
from components.mobileraker.mobileraker import install_mobileraker
from components.moonraker import moonraker_setup
from components.octoeverywhere.octoeverywhere_setup import install_octoeverywhere
from components.spoolman.spoolman import install_spoolman
from components.webui_client import client_setup
from components.webui_client.client_config import client_config_setup
from components.webui_client.fluidd_data import FluiddData
from components.webui_client.mainsail_data import MainsailData
from core.menus import Option
from core.menus.base_menu import BaseMenu
from utils.constants import COLOR_GREEN, RESET_FORMAT


# noinspection PyUnusedLocal
# noinspection PyMethodMayBeStatic
class InstallMenu(BaseMenu):
    def __init__(self, previous_menu: Optional[Type[BaseMenu]] = None):
        super().__init__()
        self.previous_menu = previous_menu

    def set_previous_menu(self, previous_menu: Optional[Type[BaseMenu]]) -> None:
        from core.menus.main_menu import MainMenu

        self.previous_menu: Type[BaseMenu] = (
            previous_menu if previous_menu is not None else MainMenu
        )

    def set_options(self) -> None:
        self.options = {
            "1": Option(method=self.install_klipper, menu=False),
            "2": Option(method=self.install_moonraker, menu=False),
            "3": Option(method=self.install_mainsail, menu=False),
            "4": Option(method=self.install_fluidd, menu=False),
            "5": Option(method=self.install_mainsail_config, menu=False),
            "6": Option(method=self.install_fluidd_config, menu=False),
            "7": Option(method=self.install_klipperscreen, menu=False),
            "8": Option(method=self.install_mobileraker, menu=False),
            "9": Option(method=self.install_crowsnest, menu=False),
            "10": Option(method=self.install_octoeverywhere, menu=False),
            "11": Option(method=self.install_spoolman, menu=False),
        }

    def print_menu(self):
        header = " [ Installation Menu ] "
        color = COLOR_GREEN
        count = 62 - len(color) - len(RESET_FORMAT)
        menu = textwrap.dedent(
            f"""
            ╔═══════════════════════════════════════════════════════╗
            ║ {color}{header:~^{count}}{RESET_FORMAT} ║
            ╟───────────────────────────┬───────────────────────────╢
            ║ Firmware & API:           │ Android / iOS:            ║
            ║  1) [Klipper]             │  8) [Mobileraker]         ║
            ║  2) [Moonraker]           │                           ║
            ║                           │ Webcam Streamer:          ║
            ║ Webinterface:             │  9) [Crowsnest]           ║
            ║  3) [Mainsail]            │                           ║
            ║  4) [Fluidd]              │ Remote Access:            ║
            ║                           │ 10) [OctoEverywhere]      ║
            ║ Client-Config:            │                           ║
            ║  5) [Mainsail-Config]     │ Spool Manager:            ║
            ║  6) [Fluidd-Config]       │ 11) [Spoolman]            ║
            ║                           │                           ║
            ║ Touchscreen GUI:          │                           ║
            ║  7) [KlipperScreen]       │                           ║
            ║                           │                           ║
            ╟───────────────────────────┴───────────────────────────╢
            """
        )[1:]
        print(menu, end="")

    def install_klipper(self, **kwargs):
        klipper_setup.install_klipper()

    def install_moonraker(self, **kwargs):
        moonraker_setup.install_moonraker()

    def install_mainsail(self, **kwargs):
        client_setup.install_client(MainsailData())

    def install_mainsail_config(self, **kwargs):
        client_config_setup.install_client_config(MainsailData())

    def install_fluidd(self, **kwargs):
        client_setup.install_client(FluiddData())

    def install_fluidd_config(self, **kwargs):
        client_config_setup.install_client_config(FluiddData())

    def install_klipperscreen(self, **kwargs):
        install_klipperscreen()

    def install_mobileraker(self, **kwargs):
        install_mobileraker()

    def install_crowsnest(self, **kwargs):
        install_crowsnest()

    def install_octoeverywhere(self, **kwargs):
        install_octoeverywhere()

    def install_spoolman(self, **kwargs):
        install_spoolman()

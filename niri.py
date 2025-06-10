import subprocess
import json
import os
import os.path
import logging
from xdg.IconTheme import getIconPath

logger = logging.getLogger(__name__)


class Window:
    def __init__(self, data: dict):
        self._id = data.get("id")
        self._title = data.get("title")
        self._app_id = data.get("app_id")
        self._pid = data.get("pid")
        self._workspace_id = data.get("workspace_id")
        self._is_focused = data.get("is_focused", False)
        self._is_floating = data.get("is_floating", False)
        self._is_urgent = data.get("is_urgent", False)
        self._icon = Window.calculate_icon(self)

    def __repr__(self):
        return (f"Window(id={self._id}, title={self._title}, "
                f"app_id={self._app_id}, workspace_id={self._workspace_id}, "
                f"is_focused={self._is_focused}, "
                f"is_floating={self._is_floating}, "
                f"is_urgent={self._is_urgent}")

    def get_id(self):
        return self._id

    def get_title(self):
        return self._title

    def get_icon(self):
        return self._icon

    def get_app_id(self):
        return self._app_id

    def get_pid(self):
        return self._pid

    def get_workspace_id(self):
        return self._workspace_id

    def is_focused(self):
        return self._is_focused

    def is_floating(self):
        return self._is_floating

    def is_urgent(self):
        return self._is_urgent

    def calculate_icon(self):
        logger.debug("Getting icon for window: %s", self.get_id())
        # See: https://lists.freedesktop.org/archives/wayland-devel/2018-April/
        # 037998.html
        suppliers = [
            # Wayland native apps - should just work
            Window.icon_loader(self.get_app_id()),
        ]
        pid = self.get_pid()
        exe_path = os.readlink(f"/proc/{pid}/exe") if pid else None
        if exe_path and os.path.exists(exe_path):
            suppliers.append(Window.icon_loader(os.path.basename(exe_path)))

        for f in suppliers:
            res = f()
            if res is not None:
                return res

        logger.info("Unable to find icon for container %d \"%s\"",
                    window.get_id(),
                    window.get_title())

        return "images/default.svg"

    def focus(self):
        command = ["niri", "msg", "action", "focus-window", "--id",
                   str(self.get_id())]
        response = subprocess.check_output(command)
        logger.debug("Focus command response: %s", response.decode().strip())

    @staticmethod
    def icon_loader(name):
        '''Returns a helper function for lazily loading an icon'''

        def f():
            if name is None:
                return None

            res = getIconPath(name)
            logger.debug("Resolving %s: %s", name, "failed" if res is None 
                         else "succeeded")
            return res

        return f


class Niri:

    @staticmethod
    def get_windows():
        response = subprocess.check_output(["niri", "msg", "-j", "windows"])
        return [Window(w) for w in json.loads(response)]


if __name__ == "__main__":
    windows = Niri.get_windows()
    for window in windows:
        print(window)
        print("Icon:", window.get_icon())


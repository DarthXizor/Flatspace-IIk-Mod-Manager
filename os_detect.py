import platform


class OSDetect:
    """
    Standalone OS detection class for the Flatspace 2K mod manager.
    Supported platforms: Windows, Linux.
    """

    WINDOWS = "Windows"
    LINUX = "Linux"
    UNSUPPORTED = "Unsupported"

    def __init__(self):
        self._system = platform.system().lower()
        self._os = self._detect()

    def _detect(self):
        if self._system == "windows":
            return self.WINDOWS
        elif self._system == "linux":
            return self.LINUX
        else:
            return self.UNSUPPORTED

    @property
    def os(self):
        return self._os

    @property
    def is_supported(self):
        return self._os != self.UNSUPPORTED

    @property
    def raw_system(self):
        return platform.system()

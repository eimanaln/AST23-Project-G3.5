from abc import ABC, abstractmethod
from typing import Generator

from host import Host


class HostManager(ABC):
    @abstractmethod
    def destroy_host(self, host: Host):
        pass

    @abstractmethod
    def host_generator(self) -> Generator[Host, None, None]:
        pass

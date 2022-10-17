"""The Stagers Model"""
import importlib
from typing import TYPE_CHECKING

from Creator.available import AVAILABLE_KITS
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from .base import Base

if TYPE_CHECKING:
    from Commander import Commander

    from Server.Kits.base_stager import BaseStager

    from .listeners import ListenerModel


class StagerModel(Base):
    """The Stagers Model"""
    __tablename__ = "Stagers"
    id: int = Column(Integer, primary_key=True, nullable=False)
    name: str = Column(String(100))
    listener_id: int = Column(Integer, ForeignKey("Listeners.id"))
    listener: "ListenerModel" = relationship(
        "ListenerModel", back_populates="stagers")
    payload_type: str = Column(String(100))
    encoding: str = Column(String(10))
    random_size: bool = Column(Boolean)
    timeout: int = Column(Integer)
    delay: int = Column(Integer)
    options: dict = Column(JSON)

    def to_dict(self, commander: "Commander", show_listener: bool = True) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "listener": self.listener.to_dict(commander, show_stagers=False) if show_listener else self.listener.id,
            "payload_type": self.payload_type,
            "encoding": self.encoding,
            "random_size": self.random_size,
            "timeout": self.timeout,
            "delay": self.delay
        }

    @staticmethod
    def get_stager_class_from_type(type: str) -> "BaseStager":
        """Return the stager class based on its type."""
        if type not in AVAILABLE_KITS:
            raise ValueError(f"Stager '{type}' isn't available.")

        try:
            open("Kits/" + type + "/stager.py", "r").close()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Stager {type} does not exist") from e
        return importlib.import_module("Kits." + type + ".stager").Stager

    @property
    def stager_class(self) -> "BaseStager":
        """Returns the stager class."""
        return self.get_stager_class_from_type(self.listener.type)

    @staticmethod
    def get_all_stagers() -> list["BaseStager"]:
        """Get all stager classes."""
        return [StagerModel.get_stager_class_from_type(stager) for stager in AVAILABLE_KITS]

    def edit(self, data: dict):
        """Edit the listener"""
        for key, value in data.items():
            if not hasattr(self, key):
                if key in self.options:
                    self.options[key] = value
            else:
                setattr(self, key, value)

    @classmethod
    def create_stager_from_data(cls, data: dict):
        """Create the stager using custom validated data"""
        standard = []
        # gets standard values present in every stager and remove them to only leave options
        for st_value in ["name", "listener", "payload_type", "encoding", "random_size", "timeout", "delay"]:
            standard.append(data.pop(st_value))
        return cls(
            name=standard[0],
            listener=standard[1],
            payload_type=standard[2],
            encoding=standard[3],
            random_size=standard[4],
            timeout=standard[5],
            delay=standard[6],
            options=data
        )

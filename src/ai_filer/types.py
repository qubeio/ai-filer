from typing import TypedDict


class Config(TypedDict):
    """Config for the AI Filing System."""
    watch_folder: str
    dest_folder: str
    model: str
    debug: bool
    testing: bool

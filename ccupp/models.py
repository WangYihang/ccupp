"""Data models for user profile information."""
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import model_validator


class Profile(BaseModel):
    """User profile for password generation.

    All personal information fields that can be used to generate
    potential weak passwords.
    """

    surname: str = ''
    first_name: str = ''
    phone_numbers: list[str] = Field(default_factory=list)
    identity: str = ''
    birthdate: tuple[str, ...] = ()
    hometowns: list[str] = Field(default_factory=list)
    places: list[list[str]] = Field(default_factory=list)
    social_media: list[str] = Field(default_factory=list)
    workplaces: list[list[str]] = Field(default_factory=list)
    educational_institutions: list[list[str]] = Field(default_factory=list)
    accounts: list[str] = Field(default_factory=list)
    passwords: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra='ignore')

    @model_validator(mode='before')
    @classmethod
    def normalize_nested_lists(cls, data: dict) -> dict:
        """Convert tuples/nested structures to consistent list[list[str]] format."""
        if not isinstance(data, dict):
            return data

        # Normalize birthdate to tuple
        if 'birthdate' in data and isinstance(data['birthdate'], list):
            data['birthdate'] = tuple(data['birthdate'])

        # Normalize nested list fields: ensure inner items are lists
        for field in ('places', 'workplaces', 'educational_institutions'):
            if field in data and isinstance(data[field], list):
                data[field] = [
                    list(item) if isinstance(item, (list, tuple)) else [item]
                    for item in data[field]
                ]

        return data

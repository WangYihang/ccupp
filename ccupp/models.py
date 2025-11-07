"""Data models for person information and configuration."""
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from ccupp.pinyin import extract_components


class PersonConfig(BaseModel):
    """Pydantic model for person configuration from YAML file."""

    surname: str | None = None
    first_name: str | None = None
    phone_numbers: list[str] = Field(default_factory=list)
    identity: str | None = None
    birthdate: list[str] | tuple | None = None
    hometowns: list[str] | tuple | None = None
    places: list[str | list[str] | tuple] = Field(default_factory=list)
    social_media: list[str] = Field(default_factory=list)
    workplaces: list[str | list[str] | tuple] = Field(default_factory=list)
    educational_institutions: list[
        str | list[str] | tuple
    ] = Field(default_factory=list)
    accounts: list[str] = Field(default_factory=list)
    passwords: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra='ignore')


class Person:
    """Represents a person with attributes for password generation."""

    def __init__(self) -> None:
        self.attributes: dict = {}

    def set_surname(self, surname: str) -> None:
        """Set surname."""
        self.attributes['surname'] = surname

    def set_first_name(self, first_name: str) -> None:
        """Set first name."""
        self.attributes['first_name'] = first_name

    def set_phone_numbers(self, phone_numbers: list[str]) -> None:
        """Set phone numbers."""
        self.attributes['phone_numbers'] = phone_numbers

    def set_identity(self, identity: str) -> None:
        """Set identity number."""
        self.attributes['identity'] = identity

    def set_birthdate(self, birthdate: list[str] | tuple) -> None:
        """Set birthdate."""
        self.attributes['birthdate'] = birthdate

    def set_hometowns(self, hometowns: list[str] | tuple) -> None:
        """Set hometowns."""
        self.attributes['hometowns'] = hometowns

    def set_places(self, places: list[str | tuple]) -> None:
        """Set places."""
        self.attributes['places'] = places

    def set_social_media(self, social_media: list[str]) -> None:
        """Set social media accounts."""
        self.attributes['social_media'] = social_media

    def set_workplaces(self, workplaces: list[str | tuple]) -> None:
        """Set workplaces."""
        self.attributes['workplaces'] = workplaces

    def set_educational_institutions(self, institutions: list[str | tuple]) -> None:
        """Set educational institutions."""
        self.attributes['educational_institutions'] = institutions

    def set_accounts(self, accounts: list[str]) -> None:
        """Set accounts."""
        self.attributes['accounts'] = accounts

    def set_passwords(self, passwords: list[str]) -> None:
        """Set passwords."""
        self.attributes['passwords'] = passwords

    def get_components(self) -> dict[str, list[str]]:
        """
        Extract components from all attributes for password generation.
        Returns a dictionary mapping component types to lists of component strings.
        """
        return {
            'name': list(
                extract_components((
                    self.attributes.get('surname', ''),
                    self.attributes.get('first_name', ''),
                )),
            ),
            'phone_numbers': list(
                extract_components(
                    self.attributes.get('phone_numbers', []),
                    use_pinyin=False,
                ),
            ),
            'identity': list(
                extract_components(
                    self.attributes.get('identity', ''),
                    use_pinyin=False,
                ),
            ),
            'birthdate': list(
                extract_components(
                    self.attributes.get('birthdate', ''),
                    use_pinyin=False,
                ),
            ),
            'hometowns': list(extract_components(self.attributes.get('hometowns', []))),
            'places': list(extract_components(self.attributes.get('places', []))),
            'social_media': list(
                extract_components(
                    self.attributes.get('social_media', []),
                    use_pinyin=False,
                ),
            ),
            'workplaces': list(extract_components(self.attributes.get('workplaces', []))),
            'educational_institutions': list(
                extract_components(
                    self.attributes.get('educational_institutions', []),
                ),
            ),
            'accounts': list(
                extract_components(
                    self.attributes.get('accounts', []),
                    use_pinyin=False,
                ),
            ),
        }

"""The person's own details (name, gender, date of birth ...). Kept encrypted, one per user id, never used in a letter unless the user types it into a case."""
import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

GENDERS = ("female", "male", "non_binary", "prefer_not_to_say")
LANGUAGES = ("en", "hi", "ta")
MIN_AGE = 18


def age_on(dob: date, today: date) -> int:
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=80)
    gender: str
    date_of_birth: date
    phone: str | None = None
    email: str | None = None
    city: str | None = Field(default=None, max_length=60)
    preferred_language: str = "en"

    @field_validator("full_name", "city")
    @classmethod
    def _clean(cls, v):
        if v is None:
            return v
        v = " ".join(v.split())
        if not v:
            raise ValueError("this field cannot be empty")
        return v

    @field_validator("gender")
    @classmethod
    def _gender(cls, v):
        if v not in GENDERS:
            raise ValueError(f"gender must be one of: {', '.join(GENDERS)}")
        return v

    @field_validator("preferred_language")
    @classmethod
    def _lang(cls, v):
        if v not in LANGUAGES:
            raise ValueError(f"language must be one of: {', '.join(LANGUAGES)}")
        return v

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        if v in (None, ""):
            return None
        digits = re.sub(r"[\s\-()]", "", v)
        if not re.fullmatch(r"\+?\d{10,13}", digits):
            raise ValueError("phone must be 10 to 13 digits, for example +919876543210")
        return digits

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        if v in (None, ""):
            return None
        v = v.strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("email does not look right")
        return v

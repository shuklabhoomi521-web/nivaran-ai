import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app.auth import current_user
from app.profiles.models import MIN_AGE, Profile, age_on
from app.profiles.store import ProfileStore

router = APIRouter(prefix="/profile", tags=["profile"])


def get_profiles() -> ProfileStore:
    return ProfileStore(os.getenv("PROFILE_STORE_FILE", ".profiles.json"))


def _today() -> date:
    return date.today()


@router.get("")
def read_profile(store: ProfileStore = Depends(get_profiles), user: str = Depends(current_user)):
    """The signed-in person's own profile, or {"profile": null} if they have not filled it in yet."""
    p = store.get(user)
    return {"profile": p.model_dump(mode="json") if p else None}


@router.put("")
def save_profile(profile: Profile, store: ProfileStore = Depends(get_profiles), user: str = Depends(current_user)):
    today = _today()
    if profile.date_of_birth > today:
        raise HTTPException(422, "date of birth cannot be in the future")
    if age_on(profile.date_of_birth, today) < MIN_AGE:
        raise HTTPException(422, f"Nivaran is for people aged {MIN_AGE} or older")
    store.save(user, profile)
    return {"profile": profile.model_dump(mode="json")}


@router.delete("")
def delete_profile(store: ProfileStore = Depends(get_profiles), user: str = Depends(current_user)):
    return {"deleted": store.delete(user)}

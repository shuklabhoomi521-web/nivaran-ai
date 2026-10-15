from pydantic import BaseModel

from app.directory.picker import ContactChoice
from app.models.case import Channel, Plan


class PlanResponse(BaseModel):
    plan: Plan                       # what the AI wrote (opening line, proof to keep, its suggested channel)
    channel: Channel | None          # the channel we will really use, after checking the directory
    channel_note: str | None         # why it differs from the AI's suggestion, if it does
    contact: ContactChoice | None    # the official contact from the verified directory
    can_proceed: bool                # False when there is no verified contact to use
    note: str | None

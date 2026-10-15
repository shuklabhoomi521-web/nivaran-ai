"""Phone provider interface. Phase 4 uses the Twilio trial; other providers
(Exotel, Telnyx, ...) can be added later by implementing PhoneProvider."""
from abc import ABC, abstractmethod


class PhoneProvider(ABC):
    @abstractmethod
    async def place_call(self, to_number: str, webhook_url: str) -> str:
        """Start an outbound call. Returns the provider's call id."""

    @abstractmethod
    async def send_dtmf(self, call_id: str, digits: str) -> None:
        """Press keypad buttons during a call (menu navigation)."""

    @abstractmethod
    async def hang_up(self, call_id: str) -> None:
        """End the call. The user must always be able to trigger this."""

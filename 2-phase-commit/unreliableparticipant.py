from participant import Participant

class UnreliableParticipant(Participant):
    """Always votes NO, regardless of data."""
    def _validate(self, data: dict) -> bool:
        return False  # always rejects
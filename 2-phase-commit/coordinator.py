from participant import Participant
import uuid
import logging
logging.basicConfig(level=logging.INFO)
class Coordinator:
    def __init__(self) -> None:
        self.participants: list[Participant] = []

    def register(self, participant: Participant):
        
        self.participants.append(participant)

    def execute(self, data:dict) -> bool:
        txn_id = str(uuid.uuid4())
        logging.info("Registering")

        # Phase 1: Prepare
        prepare_results = [(p, p.prepare(txn_id, data)) for p in self.participants]
        all_agreed = all(v for _, v  in prepare_results)

        # Phase 2: Commit or Abort
        for p, _ in prepare_results:
            p.commit(txn_id) if all_agreed else p.abort(txn_id)
        
        return all_agreed
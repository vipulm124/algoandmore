
import logging

logger = logging.getLogger(__name__)

class Participant:
    def __init__(self, name: str) -> None:
        self.name = name
        self.prepared: dict[str, dict] = {}
    
    def prepare(self, txn_id: str, data: dict) -> bool:
        if not self._validate(data):
            logger.error(f"[{self.name}] Validation failed for {txn_id}")
            return False
        self.prepared[txn_id] = {"data": data, "status": "prepared"}
        logger.info(f"[{self.name}] Prepared for {txn_id}")
        return True
    
    def commit(self, txn_id: str) -> bool:
        if txn_id not in self.prepared:
            return False
        self.prepared[txn_id]["status"] = "committed"
        logger.info(f"[{self.name}] Commited {txn_id}")
        return True
    
    def abort(self, txn_id: str) -> bool:
        if txn_id in self.prepared:
            self.prepared[txn_id]["status"] = "aborted"
            logger.info(f"[{self.name}] Aborted {txn_id}")
        
        return True
    
    def _validate(self, data:dict) -> bool:
        return data.get("amount", 0) > 0
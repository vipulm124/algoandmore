import logging
from coordinator import Coordinator
from participant import Participant
from unreliableparticipant import UnreliableParticipant

# Without any aborting

coordinator = Coordinator()
coordinator.register(Participant("DB-A"))
coordinator.register(Participant("DB-B"))
coordinator.register(Participant("DB-C"))


coordinator.execute({"amount": 1000})

print("*" * 100)

# Validation fails on all nodes
coordinator.execute({"amount": 0})     # → False

coordinator = Coordinator()
coordinator.register(Participant("DB-A"))       # will vote YES
coordinator.register(Participant("DB-B"))       # will vote YES
coordinator.register(UnreliableParticipant("DB-C"))  # will vote NO

print("*" * 100)

result = coordinator.execute({"amount": 100})
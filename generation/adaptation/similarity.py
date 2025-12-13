from generation.constructive_adaptation.node import Node
from generation.constructive_adaptation.query import Query
import random

def event_similarity(node: Node, query: Query):
    return random.uniform(0, 1)
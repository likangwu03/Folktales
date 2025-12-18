from generation.adaptation.node import Node
from generation.adaptation.query import Query
import random

def event_similarity(node: Node, query: Query):
    return random.uniform(0, 1)
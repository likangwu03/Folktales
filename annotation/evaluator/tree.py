from annotation.evaluator.node import EvaluatorNode
from typing import Optional

class EvaluatorTree():
	_root_node: EvaluatorNode
	_nodes: list[EvaluatorNode]
		
	def __init__(self, data: dict):
		self._nodes = self._build(data)
		self._root_node = self._nodes[0]

	def _build(self, data: dict, parent: Optional[EvaluatorNode] = None):
		nodes = []
		for event, values in data.items():
			node = EvaluatorNode(id=event,
							    description=values.get("description", ""),
							    parent=parent)
			nodes.append(node)
			
			children = values.get("children", {})
			if len(children) > 0:
				node.children = self._build(children, node)

		return nodes
	
	def _print(self, nodes: list[EvaluatorNode], n_tabs: int):
		for node in nodes:
			print("\t"*n_tabs+f"- {node.id}")
			if len(node.children) > 0:
				self._print(node.children, n_tabs + 1)
	
	def print(self):
		self._print(self._nodes, 0)
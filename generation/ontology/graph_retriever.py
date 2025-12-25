from rdflib import Graph

class GraphRetriever:
	graph: Graph
	cache: dict
	
	def __init__(self, graph: Graph):
		self.graph = graph
		self.cache = {}

	def execute_query(self, query: str):
		cache_key = hash(query)
		if cache_key in self.cache:
			return self.cache[cache_key]

		try:
			results = self.graph.query(query)
			result_list = list(results)
			self.cache[cache_key] = result_list
			return result_list
		except Exception as e:
			print("Error in SPARQL query:", e)
			return []
from rdflib import Graph
from generation.ontology.namespaces import ONT
from rdflib.namespace import RDF, RDFS

class EventRetriever:
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
			print(f"Error en consulta SPARQL: {e}")
			return []
		
	def get_instances_of_class(self, class_id: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?instance
		WHERE {{
			?subClass rdfs:subClassOf* ont:{class_id} .
  			?instance rdf:type ?subClass .
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.instance) for result in results]
		return []

	def count_post_events(self, instance_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT (COUNT(DISTINCT ?instance) AS ?number)
		WHERE {{
			<{instance_uri}> ont:postEvent ?instance .
		}}
		"""

		results = self.execute_query(query)
		if results:
			return int(results[0].number)
		return 0
	
	def get_post_event_instances(self, instance_uri: str, exclude_list: list[str] = []):
		filter_clause = ""
		if len(exclude_list) > 0:
			exclude_uris = ", ".join(f"<{uri}>" for uri in exclude_list)
			filter_clause = f"FILTER(?instance NOT IN ({exclude_uris}))"

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?instance
		WHERE {{
			<{instance_uri}> ont:postEvent ?postEventInstance .
			?postEventInstance rdf:type ?class .
			?subClass rdfs:subClassOf* ?class .
			?instance rdf:type ?subClass .

			{filter_clause}
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.instance) for result in results]
		return []
	
	def get_all_event_instances(self):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?instance
		WHERE {{
			?instance rdf:type ?class .
			?class rdfs:subClassOf* ont:Event .
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.instance) for result in results]
		return []
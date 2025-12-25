from generation.ontology.namespaces import ONT
from rdflib.namespace import RDF, RDFS
from generation.ontology.graph_retriever import GraphRetriever
from rdflib import Graph

class EventRetriever(GraphRetriever):
	def __init__(self, graph: Graph):
		super().__init__(graph)
		
	def get_instances_of_class(self, class_id: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?event
		WHERE {{
			?subClass rdfs:subClassOf* ont:{class_id} .
  			?event rdf:type ?subClass .
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.event) for result in results]
		return []

	def count_post_events(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT (COUNT(DISTINCT ?event) AS ?number)
		WHERE {{
			<{event_uri}> ont:postEvent ?event .
		}}
		"""

		results = self.execute_query(query)
		if results:
			return int(results[0].number)
		return 0
	
	def get_post_event_instances(self, event_uri: str, exclude_list: list[str] = []):
		filter_clause = ""
		if len(exclude_list) > 0:
			exclude_uris = ", ".join(f"<{uri}>" for uri in exclude_list)
			filter_clause = f"FILTER(?event NOT IN ({exclude_uris}))"

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?event
		WHERE {{
			<{event_uri}> ont:postEvent ?postEventevent .
			?postEventevent rdf:type ?class .
			?subClass rdfs:subClassOf* ?class .
			?event rdf:type ?subClass .

			{filter_clause}
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.event) for result in results]
		return []
	
	def get_all_event_instances(self):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?event
		WHERE {{
			?event rdf:type ?class .
			?class rdfs:subClassOf* ont:Event .
		}}
		"""

		results = self.execute_query(query)

		if results:
			return [str(result.event) for result in results]
		return []
	
	def get_place_class(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?placeClass
		WHERE {{
			<{event_uri}> ont:hasPlace ?place .
			?place rdf:type ?placeClass .
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)

		if results:
			row = results[0]
			place_uri = str(row.placeClass)
			place_id = place_uri.split('/')[-1]
			return place_id
		return None
	
	def get_object_classes(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?objectClass (COUNT(?object) AS ?objectCount)
		WHERE {{
			<{event_uri}> ont:hasObject ?object .
			?object rdf:type ?objectClass .
		}}
		GROUP BY ?objectClass
		"""

		results = self.execute_query(query)

		if results:
			return [
				{
					"id": str(result.objectClass).split('/')[-1],
					"count": int(result.objectCount)
				}
				for result in results
			]
		return []
	
	def get_role_classes(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?roleClass (COUNT(?role) AS ?roleCount)
		WHERE {{
			<{event_uri}> ont:hasAgent ?agent .
			?agent ont:hasRole ?role .
			?role rdf:type ?roleClass .
		}}
		GROUP BY ?roleClass
		"""

		results = self.execute_query(query)

		if results:
			return [
				{
					"id": str(result.roleClass).split('/')[-1],
					"count": int(result.roleCount)
				}
				for result in results
			]
		return []
	
	def get_genre(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?genre ?genreLabel
		WHERE {{
			?folktale ont:hasEvent <{event_uri}> .
			?folktale ont:hasGenre ?genre .
			?genre rdfs:label ?genreLabel .
		}}
		"""

		results = self.execute_query(query)

		if results:
			row = results[0]
			genre_uri = str(row.genre)
			genre_id = genre_uri.split('/')[-1]
			genre_label = str(row.genreLabel) if row.genreLabel else "Unknown"
			return genre_id, genre_label
		return None, None
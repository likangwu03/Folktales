from generation.ontology.namespaces import ONT,WD
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
	

	def get_role_classes_dict(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?roleClass (COUNT(?role) AS ?roleCount) (GROUP_CONCAT(DISTINCT ?agent; separator=", ") AS ?agents)
		WHERE {{
			<{event_uri}> ont:hasAgent ?agent .
			?agent ont:hasRole ?role .
			?role rdf:type ?roleClass .
		}}
		GROUP BY ?roleClass
		"""

		results = self.execute_query(query)

		if results:
			dict_result = {str(result.roleClass).split('/')[-1]: (int(result.roleCount), str(result.agents).split(',')) for result in results}
			return dict_result
		return {}

	def get_object_classes_dict(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?objectClass (COUNT(?object) AS ?objectCount) (GROUP_CONCAT(DISTINCT ?object; separator=",") AS ?objects)
		WHERE {{
			<{event_uri}> ont:hasObject ?object .
			?object rdf:type ?objectClass .
		}}
		GROUP BY ?objectClass
		"""

		results = self.execute_query(query)

		if results:
			dict_result = {str(result.objectClass).split('/')[-1]: (int(result.objectCount),str(result.objects).split(',') ) for result in results}
			return dict_result

		return {}
	
	def get_place_uri(self, event_uri: str):
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT DISTINCT ?place ?placeClass
		WHERE {{
			<{event_uri}> ont:hasPlace ?place .
			?place rdf:type ?placeClass .
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)

		if results:
			row = results[0]
			place_uri = str(row.place)
			place_id = str(row.placeClass.split('/')[-1])
			return place_id ,place_uri
		return None
	
	def get_roles_by_type_and_genre(self, role_type, genre) -> list[tuple[str, str, str]]:
		"""
		Returns:
			[(role_uri, role_label, folktale_title), ...]
		"""

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX rdfs: <{RDFS}>
		PREFIX ont: <{ONT}>
		PREFIX wd: <{WD}>


		SELECT DISTINCT ?agent ?roleLabel ?folktaleTitle
		WHERE {{
			?folktale a ont:Folktale ;
					ont:hasGenre <{genre}> ;
					ont:title ?folktaleTitle ;
					ont:hasEvent ?event .

			?event ont:hasAgent ?agent .
			?agent ont:hasRole ?role .

			?role rdf:type ont:{role_type} .
			OPTIONAL {{ ?role rdfs:label ?roleLabel }}
		}}
		"""

		results = self.execute_query(query)

		return [
			(str(row.agent), str(row.roleLabel), str(row.folktaleTitle))
			for row in results
		]

	def get_place_by_type_and_genre(self, place_type,genre) -> list[tuple[str, str, str]]:

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX rdfs: <{RDFS}>
		PREFIX ont: <{ONT}>
		PREFIX wd: <{WD}>


		SELECT DISTINCT ?place ?placeLabel ?folktaleTitle
		WHERE {{
			?folktale a ont:Folktale ;
					ont:hasGenre <{genre}> ;
					ont:title ?folktaleTitle ;
					ont:hasEvent ?event .

			?event ont:hasPlace ?place .
			?place rdf:type ont:{place_type} .
			OPTIONAL {{ ?place rdfs:label ?placeLabel }}
		}}
		"""

		results = self.execute_query(query)

		return [
			(str(row.place), str(row.placeLabel), str(row.folktaleTitle))
			for row in results
		]

	def get_objects_by_type_and_genre(self, object_type,genre) -> list[tuple[str, str, str]]:
		

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX rdfs: <{RDFS}>
		PREFIX ont: <{ONT}>
		PREFIX wd: <{WD}>


		SELECT DISTINCT ?object ?objectLabel ?folktaleTitle
		WHERE {{
			?folktale a ont:Folktale ;
					ont:hasGenre <{genre}> ;
					ont:title ?folktaleTitle ;
					ont:hasEvent ?event .

			?event ont:hasObject ?object .
			?object rdf:type ont:{object_type} .
			OPTIONAL {{ ?object rdfs:label ?objectLabel }}
		}}
		"""

		results = self.execute_query(query)

		return [
			(str(row.object), str(row.objectLabel), str(row.folktaleTitle))
			for row in results
		]

	def get_ordered_events_for_agent(self, agent_uri) -> list[tuple[str, str]]:
		query = f"""
		PREFIX rdfs: <{RDFS}>
				PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?event ?label ?eventType (COUNT(?prev) AS ?order)
		WHERE {{
			?event ont:hasAgent <{agent_uri}> ;
				rdf:type ?eventType .
			OPTIONAL {{ ?event rdfs:label ?label }}

			OPTIONAL {{
				?prev ont:postEvent+ ?event .
			}}
		}}
		GROUP BY ?event ?label
		ORDER BY ?order
		"""
		results = self.execute_query(query)

		return [
			(str(r.eventType.split("/")[-1]),str(r.event), str(r.label),str(r.order))
			for r in results
		]

	def get_ordered_events_for_object(self, object_uri) -> list[tuple[str, str, str, str]]:
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?event ?label ?eventType (COUNT(?prev) AS ?order)
		WHERE {{
			?event ont:hasObject <{object_uri}> ;
				rdf:type ?eventType .
			OPTIONAL {{ ?event rdfs:label ?label }}

			OPTIONAL {{
				?prev ont:postEvent+ ?event .
			}}
		}}
		GROUP BY ?event ?label ?eventType
		ORDER BY ?order
		"""
		results = self.execute_query(query)

		return [
			(
				str(r.eventType.split("/")[-1]),
				str(r.event),
				str(r.label),
				str(r.order)
			)
			for r in results
		]

	def get_ordered_events_for_place(self, place_uri) -> list[tuple[str, str, str, str]]:
		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?event ?label ?eventType (COUNT(?prev) AS ?order)
		WHERE {{
			?event ont:hasPlace <{place_uri}> ;
				rdf:type ?eventType .
			OPTIONAL {{ ?event rdfs:label ?label }}

			OPTIONAL {{
				?prev ont:postEvent+ ?event .
			}}
		}}
		GROUP BY ?event ?label ?eventType
		ORDER BY ?order
		"""
		results = self.execute_query(query)

		return [
			(
				str(r.eventType.split("/")[-1]),
				str(r.event),
				str(r.label),
				str(r.order)
			)
			for r in results
		]
	
	def get_type_name(self, uri: str) -> str | None:
		query = f"""
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT ?type
		WHERE {{
			<{uri}> rdf:type ?type .
			FILTER(STRSTARTS(STR(?type), STR(ont:)))
		}}
		LIMIT 1
		"""
		
		results = self.execute_query(query)

		if not results:
			return None

		return str(results[0].type).split("/")[-1]
	
	def get_label(self, resource_uri: str) -> str | None:
		query = f"""
		PREFIX rdfs: <{RDFS}>

		SELECT ?label
		WHERE {{
			<{resource_uri}> rdfs:label ?label .
		}}
		LIMIT 1
		"""
		results = self.execute_query(query)

		if not results:
			return None

		return str(results[0].label)
	
	def get_gender(self, agent_uri: str) -> str | None:
		query = f"""
		PREFIX ont: <{ONT}>

		SELECT ?gender
		WHERE {{
			<{agent_uri}> ont:gender ?gender .
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)

		if not results:
			return None

		return str(results[0].gender)
	
	def get_name(self, agent_uri: str) -> str | None:
		query = f"""
		PREFIX ont: <{ONT}>

		SELECT ?name
		WHERE {{
			<{agent_uri}> ont:name ?name .
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)

		if not results: return None

		return str(results[0].name)
	
	def get_age_category(self, agent_uri: str) -> str | None:
		query = f"""
		PREFIX ont: <{ONT}>

		SELECT ?age
		WHERE {{
			<{agent_uri}> ont:ageCategory ?age .
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)

		if not results: return None

		return str(results[0].age)
	
	def get_personality_traits(self, agent_uri: str) -> list[str]:
		query = f"""
		PREFIX ont: <{ONT}>

		SELECT ?trait
		WHERE {{
			<{agent_uri}> ont:hasPersonality ?trait .
		}}
		"""

		results = self.execute_query(query)

		return [str(row.trait)for row in results]


	def get_role_labels(self, agent_uri: str) -> list[str]:
		query = f"""
		PREFIX ont: <{ONT}>
		PREFIX rdfs: <{RDFS}>

		SELECT ?label
		WHERE {{
			<{agent_uri}> ont:hasRole ?role .
			?role rdfs:label ?label .
		}}
		"""

		results = self.execute_query(query)
		if not results: return None
		return str(results[0].label)



from rdflib import RDFS, RDF, Graph
from generation.ontology.namespaces import ONT
from generation.ontology.graph_retriever import GraphRetriever

class LocalSemanticSimilarityCalculator(GraphRetriever):
	"""
	Calculadora de similitud semántica que trabaja con ontologías locales usando consultas SPARQL sobre el grafo RDF local.

	Similar a SemanticSimilarityCalculator pero ejecuta SPARQL localmente en lugar de consultar endpoints remotos.
	"""

	def __init__(self, graph: Graph):
		super().__init__(graph)

	def get_class(self, instance_uri: str):
		query = f"""
		PREFIX rdf: <{RDF}>
		PREFIX rdfs: <{RDFS}>

		SELECT DISTINCT ?instanceClass ?classLabel WHERE {{
			<{instance_uri}> rdf:type ?instanceClass .

			OPTIONAL {{ ?instanceClass rdfs:label ?classLabel . }}
			
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)
		if results:
			row = results[0]
			uri = str(row.instanceClass)
			id = uri.split('/')[-1]
			label = str(row.classLabel) if row.classLabel else "Unknown"
			return id, label
		return None, None

	def get_least_common_subsumer_class(self, class1_id: str, class2_id: str):
		"""
		Encuentra el Least Common Subsumer (LCS) entre dos clases usando consultas SPARQL sobre el grafo local.
		"""

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>
		

		SELECT ?lcs ?lcsLabel ?sublcs WHERE {{
			# Encontrar ancestros comunes
			ont:{class1_id} rdfs:subClassOf* ?lcs .
			ont:{class2_id} rdfs:subClassOf* ?lcs .

			# Filtrar para obtener el más específico (sin subclases más específicas comunes)
			FILTER NOT EXISTS {{
				?sublcs rdfs:subClassOf+ ?lcs .
				ont:{class1_id} rdfs:subClassOf* ?sublcs .
				ont:{class2_id} rdfs:subClassOf* ?sublcs .
			}}

			OPTIONAL {{ ?lcs rdfs:label ?lcsLabel . }}
		}}
		LIMIT 1
		"""

		results = self.execute_query(query)
		if results:
			row = results[0]
			lcs_uri = str(row.lcs)
			lcs_id = lcs_uri.split('/')[-1]
			lcs_label = str(row.lcsLabel) if row.lcsLabel else "Unknown"
			return lcs_id, lcs_label
		return None, None

	def get_least_common_subsumer_class_instance(self, class_id: str, instance_uri: str):
		"""
		Encuentra el Least Common Subsumer (LCS) entre una clase y una instancia usando consultas SPARQL sobre el grafo local.
		"""

		class2_id, _ = self.get_class(instance_uri)

		return self.get_least_common_subsumer_class(class_id, class2_id)

	def get_class_depth(self, class_id):
		"""
		Calcula la profundidad de una clase en la jerarquía usando consultas SPARQL.
		"""

		query = f"""
		PREFIX rdfs: <{RDFS}>
		PREFIX rdf: <{RDF}>
		PREFIX ont: <{ONT}>

		SELECT (COUNT(DISTINCT ?parent) as ?depth) WHERE {{
			ont:{class_id} rdfs:subClassOf* ?parent .
		}}
		"""

		results = self.execute_query(query)
		if results:
			row = results[0]
			return int(row.depth)
		return 0
	
	def wu_palmer_similarity_class(self, class1_id, class2_id):
		"""
		Similitud Wu & Palmer (1994)
		sim = 2 * depth(lcs) / (depth(c1) + depth(c2))
		"""

		lcs_id, _ = self.get_least_common_subsumer_class(class1_id, class2_id)
		if not lcs_id:
			return 0.0

		depth1 = self.get_class_depth(class1_id)
		depth2 = self.get_class_depth(class2_id)
		depth_lcs = self.get_class_depth(lcs_id)

		if depth1 + depth2 == 0:
			return 0.0

		return (2.0 * depth_lcs) / (depth1 + depth2)

	def wu_palmer_similarity_class_instance(self, class_id: str, instance_uri: str):
		"""
		Similitud Wu & Palmer (1994)
		sim = 2 * depth(lcs) / (depth(c1) + depth(c2))
		"""

		class2_id, _ = self.get_class(instance_uri)

		return self.wu_palmer_similarity_class(class_id, class2_id)
	
	def get_shortest_path_length_class(self, class1_id, class2_id):
		"""
		Calcula la longitud del camino más corto entre dos entidades
		"""
		lcs_id, _ = self.get_least_common_subsumer_class(class1_id, class2_id)
		if not lcs_id:
			return float('inf')		
		
		depth1 = self.get_class_depth(class1_id)
		depth2 = self.get_class_depth(class2_id)
		depth_lcs = self.get_class_depth(lcs_id)
		
		path_length = (depth1 - depth_lcs) + (depth2 - depth_lcs)
		return path_length

	def path_similarity_class(self, class1_id, class2_id):
		"""
		Similitud Path (Rada et al., 1989)
		sim = 1 / (1 + shortest_path)
		"""
		path_length = self.get_shortest_path_length_class(class1_id, class2_id)
		if path_length == float('inf'):
			return 0.0
		return 1.0 / (1.0 + path_length)
	
	def path_similarity_class_instance(self, class_id, instance_uri):
		"""
		Similitud Path (Rada et al., 1989)
		sim = 1 / (1 + shortest_path)
		"""
		class2_id, _ = self.get_class(instance_uri)

		return self.path_similarity_class(class_id, class2_id)
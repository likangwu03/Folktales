from rdflib import Graph, RDF, RDFS, OWL, FOAF, DCTERMS, URIRef, Literal, XSD
import typing
from generation.ontology.namespaces import *
from common.regex_utils import split_camel_case, title_case_to_snake_case, snake_case_to_title_case,  snake_case_to_camel_case
import generation.utils.sbc_tools as sbc
from loguru import logger

class FolktaleOntology(Graph):	
	agent_map = {
		"human_being": ONT.HumanBeing, 
		"anthropomorphic_animal": ONT.AnthropomorphicAnimal, 
		"magical_creature": ONT.MagicalCreature, 
		"groupOfAgents": ONT.GroupOfAgents, 
		"agent": ONT.Agent
	}

	place_map = {
		"mountain": ONT.Mountain, 
		"forest": ONT.Forest, 
		"river": ONT.River, 
		"field": ONT.Field, 
		"castle": ONT.Castle, 
		"palace": ONT.Palace, 
		"house": ONT.House, 
		"hut": ONT.Hut, 
		"farmhouse": ONT.Farmhouse, 
		"tower": ONT.Tower, 
		"shop": ONT.Shop, 
		"school": ONT.School, 
		"tavern": ONT.Tavern, 
		"village": ONT.Village, 
		"town": ONT.Town, 
		"city": ONT.City, 
		"kingdom": ONT.Kingdom
	}

	object_map = {
		"animate_object": ONT.AnimateObject, 
		"non_anthropomorphic_animal": ONT.NonAnthropomorphicAnimal, 
		"inanimate_object": ONT.InanimateObject, 
		"magical_object": ONT.MagicalObject, 
		"natural_object": ONT.NaturalObject, 
		"crafted_object": ONT.CraftedObject
	}

	role_map = {
		"hero": ONT.Hero, 
		"villain": ONT.Villain, 
		"false_hero": ONT.FalseHero, 
		"magical_helper": ONT.MagicalHelper, 
		"prisoner": ONT.Prisoner, 
		"princess": ONT.Princess, 
		"quest_giver": ONT.QuestGiver, 
		"hero_family": ONT.HeroFamily, 
		"primary_character": ONT.PrimaryCharacter, 
		"main_character": ONT.MainCharacter, 
		"antagonist": ONT.Antagonist, 
		"secondary_character": ONT.SecondaryCharacter, 
		"helper": ONT.Helper, 
		"tertiary_character": ONT.TertiaryCharacter
	}

	event_map = {
		"move": ONT.Move, 
			"setup": ONT.Setup, 
				"initial_situation": ONT.InitialSituation, 
				
			"conflict": ONT.Conflict, 
				"hero_interdiction": ONT.HeroInterdiction, 
					"villainy": ONT.Villainy, 
					"false_matrimony": ONT.FalseMatrimony, 
					"expulsion": ONT.Expulsion, 
					"kidnapping": ONT.Kidnapping, 
					"murder": ONT.Murder, 
				"lack": ONT.Lack, 
					"lack_of_bride": ONT.LackOfBride, 
					"lack_of_money": ONT.LackOfMoney, 
				"hero_departure": ONT.HeroDeparture, 
				"struggle": ONT.Struggle, 
					"fight": ONT.Fight, 
				"branding": ONT.Branding, 
					"receive_mark": ONT.ReceiveMark, 
					"receive_injury": ONT.ReceiveInjury, 
				"connective_incident": ONT.ConnectiveIncident, 
					"call_for_help": ONT.CallForHelp, 
					"departure_decision": ONT.DepartureDecision, 
				"villain_gains_information": ONT.VillainGainsInformation, 

			"preparation": ONT.Preparation, 
				"absentation": ONT.Absentation, 
				"breaking_interdiction": ONT.BreakingInterdiction, 
				"acquisition": ONT.Acquisition, 
					"get_present": ONT.GetPresent, 
				"guidance": ONT.Guidance, 
				"return_event": ONT.Return, 
				"make_contact_with_enemy": ONT.MakeContactWithEnemy, 
				"mediation": ONT.Mediation, 
				"trickery": ONT.Trickery, 

			"beginning_of_counteraction": ONT.BeginningOfCounteraction, 

			"helper_move": ONT.HelperMove, 
				"receipt_object": ONT.ReceiptObject, 
				"liquidiation_of_lack": ONT.LiquidiationOfLack, 
					"release_from_captivity": ONT.ReleaseFromCaptivity, 
				"pursuit_and_rescue": ONT.PursuitAndRescue, 
				
			"false_hero_make_unfounded_claim": ONT.FalseHeroMakeUnfoundedClaim, 
			
			"attempt_at_reconnaissance": ONT.AttemptAtReconnaissance, 

		"resolution": ONT.Resolution, 
			"victory": ONT.Victory, 
				"villain_defeated": ONT.VillainDefeated, 

			"arrival": ONT.Arrival, 
				"unrecognised_arrival": ONT.UnrecognisedArrival, 
					"home_arrival": ONT.HomeArrival, 

			"difficult_task_with_solution": ONT.DifficultTaskWithSolution, 
				"difficult_task": ONT.DifficultTask, 
				"solution_difficult_task": ONT.SolutionDifficultTask, 

			"resolution_function": ONT.ResolutionFunction, 
				"recognition": ONT.Recognition, 
				"punishment": ONT.Punishment, 
				"reward": ONT.Reward, 

			"exposure_of_villain": ONT.ExposureOfVillain, 

			"transfiguration": ONT.Transfiguration, 
				"physical_transformation": ONT.PhysicalTransformation, 
				"psychological_transformation": ONT.PsychologicalTransformation, 

			"wedding_or_throne": ONT.WeddingOrThrone, 
				"wedding": ONT.Wedding, 
				"get_throne": ONT.GetThrone
	}

	genre_map = {
		"fable": WD.Q693, 
		"fairy_tale":  WD.Q699, 
		"legend": WD.Q44342, 
		"myth": WD.Q12827256, 
		"tall_tale": WD.Q1951220, 
	}

	age_group_map = {
		"children": PEARL.children, 
		"young": PEARL.young, 
		"adult": PEARL.adult, 
		"senior": PEARL.senior, 
	}

	personality_map = {
		"sociable": PEARL.Sociable, 
		"joyful": PEARL.Joyful, 
		"active": PEARL.Active, 
		"assertive": PEARL.Assertive, 
		"eager": PEARL.Eager, 
		"depressive": PEARL.Depressive, 
		"tense": PEARL.Tense, 
		"aggressive": PEARL.Aggressive, 
		"cold": PEARL.Cold, 
		"egocentric": PEARL.Egocentric, 
		"impersonal": PEARL.Impersonal, 
		"impulsive": PEARL.Impulsive
	}

	relationship_map = {
		"knows": ONT.knows, 
		"friend": ONT.hasFriend, 
		"enemy": ONT.hasEnemy, 
		"family_member": ONT.hasFamilyMember, 
	}

	def _add_namespaces(self):
		self.bind("ont", ONT)
		self.bind("res", RES)

		self.bind("wd", WD)
		self.bind("wdt", WDT)
		self.bind("schema", SCHEMA)
		self.bind("rdf", RDF)
		self.bind("rdfs", RDFS)
		self.bind("owl", OWL)
		self.bind("foaf", FOAF)
		self.bind("dcterms", DCTERMS)

		self.bind("sem", SEM)
		self.bind("rel", REL)
		self.bind("pearl", PEARL)

	def _merge_graph(self, graph: Graph):
		for triple in graph:
			self.add(triple)

	def add_imports(self):
		sem_ontology = "http://semanticweb.cs.vu.nl/2009/11/sem/"
		self.add((ONT[""], OWL.imports, URIRef(sem_ontology)))
		self.add((ONT[""], OWL.imports, URIRef("http://www.gsi.upm.es/ontologies/pearl/ns#")))

		sem_graph = Graph()
		sem_graph.parse(sem_ontology, format='xml')
		self._merge_graph(sem_graph)

		pearl_graph = sbc.load("pearl.ttl")
		self._merge_graph(pearl_graph)

	def _add_class_hierarchy(self, parent_class_name: str, hierarchy: dict):
		for class_name, class_info in hierarchy.items():
			camel_case_name = snake_case_to_camel_case(class_name)
			# print(camel_case_name)

			self.add((getattr(ONT, camel_case_name), RDF.type, OWL.Class))
			self.add((getattr(ONT, camel_case_name), RDFS.subClassOf, getattr(ONT, parent_class_name)))
			self.add((getattr(ONT, camel_case_name), RDFS.label, Literal(snake_case_to_title_case(class_name))))

			children = class_info.get("children")
			if children:
				self._add_class_hierarchy(camel_case_name, children)

	def _add_classes(self, hierarchies: dict):
		# -------------------------------------
		# GENRE
		# -------------------------------------

		self.add((ONT.Genre, RDF.type, OWL.Class))
		self.add((ONT.Genre, RDFS.label, Literal("Genre")))
		self.add((ONT.Genre, OWL.equivalentClass, WD.Q223393))

		# -------------------------------------
		# PLACE
		# -------------------------------------

		self.add((ONT.Place, RDF.type, OWL.Class))
		self.add((ONT.Place, RDFS.label, Literal("Place")))
		self.add((ONT.Place, OWL.equivalentClass, SEM.Place))
		self.add((ONT.Place, OWL.equivalentClass, SCHEMA.Place))
		self.add((ONT.Place, OWL.equivalentClass, DCTERMS.Location))

		# -------------------------------------
		# ROLE
		# -------------------------------------

		self.add((ONT.Role, RDF.type, OWL.Class))
		self.add((ONT.Role, RDFS.label, Literal("Role")))
		self.add((ONT.Role, OWL.equivalentClass, SEM.Role))


		# -------------------------------------
		# ENTITY 
		# -------------------------------------

		self.add((ONT.Entity, RDF.type, OWL.Class))
		self.add((ONT.Entity, RDFS.label, Literal("Entity")))
		self.add((ONT.Entity, OWL.equivalentClass, SEM.Actor))

		# -------------------------------------
		# AGENT 
		# -------------------------------------

		self.add((ONT.Agent, RDF.type, OWL.Class))
		self.add((ONT.Agent, RDFS.label, Literal("Agent")))
		self.add((ONT.Agent, RDFS.subClassOf, ONT.Entity))
		self.add((ONT.Agent, OWL.equivalentClass, SCHEMA.Person))

		self.add((ONT.AgeGroup, RDF.type, OWL.Class))
		self.add((ONT.AgeGroup, RDFS.label, Literal("Age Group")))
		self.add((ONT.AgeGroup, OWL.equivalentClass, PEARL.AgeGroup))

		self.add((ONT.Personality, RDF.type, OWL.Class))
		self.add((ONT.Personality, RDFS.label, Literal("Personality")))
		self.add((ONT.Personality, OWL.equivalentClass, PEARL.Personality))

		# ------- SUBCLASSES OF AGENT -------

		self.add((ONT.IndividualAgent, RDF.type, OWL.Class))
		self.add((ONT.IndividualAgent, RDFS.subClassOf, ONT.Agent))

		self.add((ONT.HumanBeing, RDF.type, OWL.Class))
		self.add((ONT.HumanBeing, RDFS.subClassOf, ONT.IndividualAgent))

		self.add((ONT.AnthropomorphicAnimal, RDF.type, OWL.Class))
		self.add((ONT.AnthropomorphicAnimal, RDFS.subClassOf, ONT.IndividualAgent))

		self.add((ONT.MagicalCreature, RDF.type, OWL.Class))
		self.add((ONT.MagicalCreature, RDFS.subClassOf, ONT.IndividualAgent))

		self.add((ONT.GroupOfAgents, RDF.type, OWL.Class))
		self.add((ONT.GroupOfAgents, RDFS.subClassOf, ONT.Agent))

		# -------------------------------------
		# OBJECT
		# -------------------------------------

		self.add((ONT.Object, RDF.type, OWL.Class))
		self.add((ONT.Object, RDFS.label, Literal("Object")))
		self.add((ONT.Object, RDFS.subClassOf, ONT.Entity))
		self.add((ONT.Object, OWL.equivalentClass, SEM.Object))

		# -------------------------------------
		# EVENT
		# -------------------------------------

		self.add((ONT.Event, RDF.type, OWL.Class))
		self.add((ONT.Event, RDFS.label, Literal("Event")))
		self.add((ONT.Event, RDFS.subClassOf, SEM.Event))
		self.add((ONT.Event, OWL.equivalentClass, SCHEMA.Action))

		# -------------------------------------
		# FOLKTALE
		# -------------------------------------

		self.add((ONT.Folktale, RDF.type, OWL.Class))
		self.add((ONT.Folktale, RDFS.label, Literal("Folktale")))
		self.add((ONT.Folktale, OWL.equivalentClass, WD.Q1221280))
		self.add((ONT.Folktale, RDFS.subClassOf, SCHEMA.CreativeWork))

		for hierarchy in hierarchies.values():
			# print("-"*20)
			for class_name, class_info in hierarchy.items():
				camel_case_name = snake_case_to_camel_case(class_name)
				# print(camel_case_name)
				self._add_class_hierarchy(camel_case_name, class_info.get("children", {}))

	def _add_properties(self):
		# -------------------------------------
		# AGENT 
		# -------------------------------------

		# hasRole
		self.add((ONT.hasRole, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasRole, RDFS.domain, ONT.Agent))
		self.add((ONT.hasRole, RDFS.range, ONT.Role))

		# hasPersonality
		self.add((ONT.hasPersonality, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasPersonality, RDFS.domain, ONT.Agent))
		self.add((ONT.hasPersonality, RDFS.range, ONT.Personality))

		# livesIn
		self.add((ONT.livesIn, RDF.type, OWL.ObjectProperty))
		self.add((ONT.livesIn, RDFS.domain, ONT.Agent))
		self.add((ONT.livesIn, RDFS.range, ONT.Place))

		# knows
		self.add((ONT.knows, RDF.type, OWL.ObjectProperty))
		self.add((ONT.knows, RDFS.domain, ONT.Agent))
		self.add((ONT.knows, RDFS.range, ONT.Agent))
		self.add((ONT.knows, OWL.equivalentProperty, FOAF.knows))
		self.add((ONT.knows, OWL.inverseOf, REL.knowsOf))

		# hasFriend
		self.add((ONT.hasFriend, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasFriend, RDFS.domain, ONT.Agent))
		self.add((ONT.hasFriend, RDFS.range, ONT.Agent))
		self.add((ONT.hasFriend, RDFS.subPropertyOf, ONT.knows))
		self.add((ONT.hasFriend, OWL.inverseOf, REL.friendOf))

		# hasEnemy
		self.add((ONT.hasEnemy, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasEnemy, RDFS.domain, ONT.Agent))
		self.add((ONT.hasEnemy, RDFS.range, ONT.Agent))
		self.add((ONT.hasEnemy, RDFS.subPropertyOf, ONT.knows))
		self.add((ONT.hasEnemy, OWL.inverseOf, REL.enemyOf))

		# hasFamilyMember
		self.add((ONT.hasFamilyMember, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasFamilyMember, RDFS.domain, ONT.Agent))
		self.add((ONT.hasFamilyMember, RDFS.range, ONT.Agent))
		self.add((ONT.hasFamilyMember, RDFS.subPropertyOf, ONT.knows))
		self.add((ONT.hasFamilyMember, OWL.inverseOf, REL.familyMemberOf))

		# gender
		self.add((ONT.gender, RDF.type, OWL.DatatypeProperty))
		self.add((ONT.gender, RDFS.domain, ONT.Agent))
		self.add((ONT.gender, RDFS.range, XSD.string))
		self.add((ONT.gender, OWL.equivalentProperty, SCHEMA.gender))

		# ageCategory
		self.add((ONT.ageCategory, RDF.type, OWL.ObjectProperty))
		self.add((ONT.ageCategory, RDFS.domain, ONT.Agent))
		self.add((ONT.ageCategory, RDFS.range, ONT.AgeGroup))

		# name
		self.add((ONT.name, RDF.type, OWL.DatatypeProperty))
		self.add((ONT.name, RDFS.domain, ONT.Entity))
		self.add((ONT.name, RDFS.range, XSD.string))
		self.add((ONT.name, OWL.equivalentProperty, FOAF.name))

		# -------------------------------------
		# EVENT
		# -------------------------------------

		# hasPlace
		self.add((ONT.hasPlace, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasPlace, RDFS.domain, ONT.Event))
		self.add((ONT.hasPlace, RDFS.range, ONT.Place))
		self.add((ONT.hasPlace, RDFS.subPropertyOf, SEM.hasPlace))
		self.add((ONT.hasPlace, OWL.equivalentProperty, DCTERMS.spatial))

		# preEvent
		self.add((ONT.preEvent, RDF.type, OWL.ObjectProperty))
		self.add((ONT.preEvent, RDFS.domain, ONT.Event))
		self.add((ONT.preEvent, RDFS.range, ONT.Event))
		self.add((ONT.preEvent, OWL.inverseOf, ONT.postEvent))

		# postEvent
		self.add((ONT.postEvent, RDF.type, OWL.ObjectProperty))
		self.add((ONT.postEvent, RDFS.domain, ONT.Event))
		self.add((ONT.postEvent, RDFS.range, ONT.Event))
		self.add((ONT.postEvent, OWL.inverseOf, ONT.preEvent))

		# hasAgent
		self.add((ONT.hasAgent, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasAgent, RDFS.domain, ONT.Event))
		self.add((ONT.hasAgent, RDFS.range, ONT.Agent))
		self.add((ONT.hasAgent, RDFS.subPropertyOf, SEM.hasActor))

		# hasObject
		self.add((ONT.hasObject, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasObject, RDFS.domain, ONT.Event))
		self.add((ONT.hasObject, RDFS.range, ONT.Object))
		self.add((ONT.hasObject, RDFS.subPropertyOf, SEM.hasActor))

		# -------------------------------------
		# FOLKTALE
		# -------------------------------------

		# title
		self.add((ONT.title, RDF.type, OWL.DatatypeProperty))
		self.add((ONT.title, RDFS.domain, ONT.Folktale))
		self.add((ONT.title, RDFS.range, XSD.string))
		self.add((ONT.title, OWL.equivalentProperty, WDT.P1476))
		self.add((ONT.title, OWL.equivalentProperty, DCTERMS.title))

		# nation
		self.add((ONT.nation , RDF.type, OWL.DatatypeProperty))
		self.add((ONT.nation , RDFS.domain, ONT.Folktale))
		self.add((ONT.nation , RDFS.range, XSD.string))

		# hasGenre
		self.add((ONT.hasGenre, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasGenre, RDFS.domain, ONT.Folktale))
		self.add((ONT.hasGenre, RDFS.range, ONT.Genre))
		self.add((ONT.hasGenre, OWL.equivalentProperty, SCHEMA.genre))

		# hasEvent
		self.add((ONT.hasEvent, RDF.type, OWL.ObjectProperty))
		self.add((ONT.hasEvent, RDFS.domain, ONT.Folktale))
		self.add((ONT.hasEvent, RDFS.range, ONT.Event))

	def _add_instances(self):
		# -------------------------------------
		# GENRE
		# -------------------------------------

		fable = self.genre_map["fable"]
		self.add((fable, RDF.type, ONT.Genre))
		self.add((fable, RDFS.label, Literal("Fable")))

		fairy_tale = self.genre_map["fairy_tale"]
		self.add((fairy_tale, RDF.type, ONT.Genre))
		self.add((fairy_tale, RDFS.label, Literal("Fairy Tale")))

		legend = self.genre_map["legend"]
		self.add((legend, RDF.type, ONT.Genre))
		self.add((legend, RDFS.label, Literal("Legend")))

		myth = self.genre_map["myth"]
		self.add((myth, RDF.type, ONT.Genre))
		self.add((myth, RDFS.label, Literal("Myth")))

		tall_tale = self.genre_map["tall_tale"]
		self.add((tall_tale, RDF.type, ONT.Genre))
		self.add((tall_tale, RDFS.label, Literal("Tall Tale")))

	def build(self, hierarchies: dict):
		self._add_namespaces()
		self._add_classes(hierarchies)
		self._add_properties()
		self._add_instances()

	def save(self, filename="folktales.ttl"):
		sbc.save(self, filename, format="turtle")

	def render_html(self, mode: typing.Literal["full", "simplified", "instances"]="full", filename="folktales.html"):
		if mode=="full":
			sbc.show_graph(self, output_file=filename)
		elif mode=="simplified":
			sbc.show_graph_without_owl(self, output_file=filename)
		elif mode=="instances":
			sbc.show_instance_graph(self, output_file=filename)

	def load(self, filename="folktales.ttl"):
		graph = sbc.load(filename)
		self._merge_graph(graph)

	def _try_add_text(self, subject, predicate, text):
		if text:
			self.add((subject, predicate, Literal(text, datatype = XSD.string)))
			return True
		logger.info(f"Invalid text: {text}")
		return False

	def _try_add_existing_instance(self, subject, predicate, key, mapping_map):
		if key in mapping_map:
			self.add((subject, predicate, mapping_map[key]))
			return True
		logger.info(f"Invalid key: {key}")
		return False

	def _try_add_existing_instances(self, subject, predicate, lst, mapping_map):
		if isinstance(lst, list):
			for elem in lst:
				self.add((subject, predicate, mapping_map[elem]))
			return True
		logger.info(f"Invalid list: {lst}")
		return False
	
	def add_folktale(self, data: dict):
		title = data["title"]

		slugify_title = title_case_to_snake_case(title)

		folktale_uri = RES[f"folktale/{slugify_title}"]
		self.add((folktale_uri, RDF.type, ONT.Folktale))
		self.add((folktale_uri, ONT.title, Literal(title, datatype = XSD.string)))
		self.add((folktale_uri, RDFS.label, Literal(title, datatype = XSD.string)))
		self.add((folktale_uri, OWL.sameAs, URIRef(data["uri"])))

		self._try_add_text(folktale_uri, ONT.nation, data.get("nation"))

		self._try_add_existing_instance(folktale_uri, ONT.hasGenre, data.get("has_genre"), self.genre_map)

		# -----------------------------
		# Crear lugares
		# -----------------------------
		places = data.get("places")
		place_uris = {}
		if places and isinstance(places, list):
			for i, place in enumerate(places):
				# Se crea el lugar y se añade al grafo
				instance_name = place["instance_name"]

				place_uri = RES[f"place/{slugify_title}/{title_case_to_snake_case(instance_name)}"]

				self.add((place_uri, RDF.type, self.place_map[place["class_name"]]))
				self.add((place_uri, RDFS.label, Literal(snake_case_to_title_case(instance_name), datatype = XSD.string)))
				place_uris[i] = place_uri

		# -----------------------------
		# Crear objetos
		# -----------------------------
		objects = data.get("objects")
		object_uris = {}
		if objects and isinstance(objects, list):
			for i, object in enumerate(objects):
				# Se crea el lugar y se añade al grafo
				instance_name = object["instance_name"]

				object_uri = RES[f"object/{slugify_title}/{title_case_to_snake_case(instance_name)}"]

				self.add((object_uri, RDF.type, self.object_map[object["class_name"]]))
				self.add((object_uri, RDFS.label, Literal(snake_case_to_title_case(instance_name), datatype = XSD.string)))            
				object_uris[i] = object_uri

		# -----------------------------
		# Crear agentes
		# -----------------------------
		agents = data.get("agents")
		agent_uri_map = {}  # mapear índices de JSON a URIs
		if agents and isinstance(agents, list):
			for i, agent in enumerate(agents):
				# Se crea el agente y se añade al grafo
				instance_name = agent["instance_name"]

				agent_uri = RES[f"agent/{slugify_title}/{title_case_to_snake_case(instance_name)}"]

				self.add((agent_uri, RDF.type, self.agent_map[agent["class_name"]]))
				self.add((agent_uri, RDFS.label, Literal(snake_case_to_title_case(instance_name), datatype = XSD.string)))

				self._try_add_text(agent_uri, ONT.name, agent.get("name"))
				self._try_add_existing_instance(agent_uri, RDF.type, agent.get("age_category"), self.age_group_map)
				self._try_add_existing_instances(agent_uri, ONT.hasPersonality, agent.get("has_personality"), self.personality_map)

				lives_in = agent.get("lives_in")
				if lives_in and isinstance(lives_in, int):
					self.add((agent_uri,  ONT.livesIn, place_uris[lives_in]))

				hasRole = agent.get("has_role")
				if hasRole:
					instance_name = hasRole["instance_name"]

					role_uri = RES[f"role/{slugify_title}/{title_case_to_snake_case(instance_name)}"]

					self.add((role_uri, RDF.type, self.role_map[hasRole["class_name"]]))
					self.add((role_uri, RDFS.label, Literal(snake_case_to_title_case(instance_name), datatype = XSD.string)))            
					self.add((agent_uri, ONT.hasRole, role_uri))

				agent_uri_map[i] = agent_uri

		# -----------------------------
		# Crear relaciones
		# -----------------------------
		relationships = data.get("relationships")	
		if relationships and isinstance(relationships, list):
			for relationship in relationships:
				agent_uri = agent_uri_map[relationship["agent"]]
				other_uri = agent_uri_map[relationship["other"]]
				relationship_type = relationship["relationship"]
				self.add((agent_uri, self.relationship_map[relationship_type], other_uri))
				self.add((other_uri, self.relationship_map[relationship_type], agent_uri))

		# -----------------------------
		# Crear eventos
		# -----------------------------
		pre_event_uri = None
		events = data.get("events")
		if events and isinstance(events, list):
			for event in events:
				instance_name = event["instance_name"]

				event_uri = RES[f"event/{slugify_title}/{title_case_to_snake_case(instance_name)}"]

				self.add((event_uri, RDF.type, self.event_map[event["class_name"]]))
				self.add((event_uri, RDFS.label, Literal(snake_case_to_title_case(instance_name), datatype = XSD.string)))
				
				# Se añade el evento al cuento popular
				self.add((folktale_uri, ONT.hasEvent, event_uri))
				
				# Se añaden los agentes que hay en el evento
				self._try_add_existing_instances(event_uri, ONT.hasAgent, event.get("agents"), agent_uri_map)
				
				# Se añaden los lugares que hay en el evento
				self._try_add_existing_instance(event_uri, ONT.hasPlace, event.get("place"), place_uris)

				# Se añaden los objetos que hay en el evento
				self._try_add_existing_instances(event_uri, ONT.hasObject, event.get("objects"), object_uris)

				# Se establece la secuencia de ventos
				if pre_event_uri:
					self.add((pre_event_uri, ONT.postEvent, event_uri))
					self.add((event_uri, ONT.preEvent, pre_event_uri))
					
				pre_event_uri = event_uri	

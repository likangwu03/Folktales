from rdflib import RDF, RDFS, OWL
from generation.ontology.rmq_fcb import RMQ_FCB

class LCA_RDF:
    """
    LCA usando Euler tour + RMQ estilo Farach-Colton-Bender, directamente desde un grafo RDF.
    Construcción: O(n)
    Consultas LCA: O(1)
    """
    def __init__(self, graph):
        self.graph = graph
        self.class_ids = {}      # URI → int
        self.id_to_class = []    # int → URI
        self.euler = []
        self.depth = []
        self.first_occurrence = {}
        self.visited = set()
        self.rmq = None

    def _get_id(self, uri):
        if uri not in self.class_ids:
            idx = len(self.id_to_class)
            self.class_ids[uri] = idx
            self.id_to_class.append(uri)
        return self.class_ids[uri]

    def _dfs(self, node, d=0):
        node_id = self._get_id(node)
        if node_id not in self.first_occurrence:
            self.first_occurrence[node_id] = len(self.euler)
        self.euler.append(node_id)
        self.depth.append(d)

        # Obtener instancias de esta clase
        instances = set(self.graph.subjects(RDF.type, node))
        for inst in instances:
            inst_id = self._get_id(inst)
            # Tratar instancia como hijo directo
            self.euler.append(inst_id)
            self.depth.append(d + 1)
            if inst_id not in self.first_occurrence:
                self.first_occurrence[inst_id] = len(self.euler) - 1

        # DFS sobre subclases
        for child in self.graph.subjects(RDFS.subClassOf, node):
            child_id = self._get_id(child)
            if child_id in self.visited:
                continue
            self.visited.add(child_id)
            self._dfs(child, d + 1)
            # volver al nodo después de visitar hijo
            self.euler.append(node_id)
            self.depth.append(d)


    def build(self):
        # crear raíz artificial
        ROOT = None
        node_id = self._get_id(ROOT)
        if node_id not in self.first_occurrence:
            self.first_occurrence[node_id] = len(self.euler)
        self.euler.append(node_id)
        self.depth.append(-1)

        # detectar raíces (clases sin padre)
        classes = set(self.graph.subjects(RDF.type, OWL.Class))
        roots = []
        for cls in classes:
            parents = list(self.graph.objects(cls, RDFS.subClassOf))
            if not parents or not any(p in classes for p in parents):
                roots.append(cls)
        if not roots:
            roots = list(classes)

        # DFS desde cada raíz
        self.visited = set()
        for root in roots:
            root_id = self._get_id(root)
            self.visited.add(root_id)
            self._dfs(root, 0)
            #ROOT
            self.euler.append(node_id)
            self.depth.append(-1)

        # construir RMQ
        self.rmq = RMQ_FCB(self.depth)

    def lca(self, uri1, uri2):
        if self.rmq is None:
            raise RuntimeError("LCA no construido. Llama a build() primero.")
        u = self.class_ids[uri1]
        v = self.class_ids[uri2]
        L = self.first_occurrence[u]
        R = self.first_occurrence[v]
        idx = self.rmq.query(L, R)
        return self.id_to_class[self.euler[idx]]
    
    def get_depth(self,uri):
        u = self.class_ids[uri]
        L = self.first_occurrence[u]
        return self.depth[L]

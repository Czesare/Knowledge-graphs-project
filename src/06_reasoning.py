from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import RDF
from owlready2 import (
    get_ontology,
    default_world,
    sync_reasoner_pellet,
    OwlReadyInconsistentOntologyError,
)

ROOT = Path(__file__).resolve().parents[1]
TTL  = ROOT / "output" / "merged_kg_a2.ttl"
NT   = ROOT / "output" / "merged_kg_a2.nt"

# 1) Convert TTL -> NT (Pellet/Jena-friendly)
g = Graph()
g.parse(str(TTL), format="turtle")
g.serialize(destination=str(NT), format="nt")

# 2) Load NT locally (IMPORTANT: use local path, not http://...)
onto = get_ontology(str(NT)).load()

print("Loaded:", NT)
print("World individuals:", len(list(default_world.individuals())))

# (Optional) show how many ontologies exist in the world
try:
    onts = list(default_world.ontologies)
    print("Ontologies in world:", len(onts))
except Exception:
    pass

# 3) Reason (Pellet)
try:
    sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)
    print("✅ Reasoning finished: ontology is CONSISTENT")
except OwlReadyInconsistentOntologyError:
    print("❌ Ontology is INCONSISTENT")
    raise

rg = default_world.as_rdflib_graph()
HI = Namespace("https://w3id.org/hi-ontology#")

print("Papers:", len(set(rg.subjects(RDF.type, HI.Paper))))
print("CompetitionUseCases:", len(set(rg.subjects(RDF.type, HI.CompetitionUseCase))))

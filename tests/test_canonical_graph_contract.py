import json
import unittest
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import RDF


ROOT = Path(__file__).resolve().parents[1]
MERGED_KG = ROOT / "output" / "merged_kg.ttl"
INSTANCE_AUDIT_SUMMARY = ROOT / "output" / "audit" / "instance_generation_summary.json"
HI = Namespace("https://w3id.org/hi-ontology#")


class CanonicalGraphContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(str(MERGED_KG), format="turtle")

    def test_query5_explicit_evaluation_path_exists(self):
        found_path = False
        for paper in self.graph.subjects(RDF.type, HI.Paper):
            for use_case in self.graph.objects(paper, HI.describesUseCase):
                for team in self.graph.objects(use_case, HI.hasHITeam):
                    for agent in self.graph.objects(team, HI.hasMember):
                        for exec_uri in self.graph.objects(agent, HI.performsExecution):
                            for eval_uri in self.graph.objects(exec_uri, HI.evaluatedBy):
                                if (eval_uri, RDF.type, HI.Evaluation) in self.graph:
                                    found_path = True
                                    break
                            if found_path:
                                break
                        if found_path:
                            break
                    if found_path:
                        break
                if found_path:
                    break
            if found_path:
                break

        self.assertTrue(
            found_path,
            "Merged KG should support Query 5 through explicit Paper→UseCase→Team→Agent→Execution→Evaluation traversal.",
        )

    def test_shacl_critical_relations_and_audit_summary(self):
        for task in self.graph.subjects(RDF.type, HI.Task):
            self.assertTrue(
                list(self.graph.objects(task, HI.requiresCapability)),
                f"Task {task} is missing hi:requiresCapability.",
            )

        for exec_uri in self.graph.subjects(RDF.type, HI.TaskExecution):
            self.assertTrue(
                list(self.graph.objects(exec_uri, HI.realizesTask)),
                f"TaskExecution {exec_uri} is missing hi:realizesTask.",
            )

        self.assertTrue(
            INSTANCE_AUDIT_SUMMARY.exists(),
            "Instance-generation audit summary should exist after rerunning Step 3.",
        )
        data = json.loads(INSTANCE_AUDIT_SUMMARY.read_text(encoding="utf-8"))
        self.assertIn("totals", data)
        self.assertIn("repair_link_counts", data["totals"])
        self.assertIn("unresolved_counts", data["totals"])


if __name__ == "__main__":
    unittest.main()

"""The docs assistant's graph: the org chart in Neo4j (chapters 10 and 11 of Tokens to Agents).

Needs a Neo4j to talk to. A throwaway one:

    docker run -d --rm --name tta-neo4j -p 127.0.0.1:7688:7687 -e NEO4J_AUTH=neo4j/tokens-to-agents-local neo4j:5.26.32

    uv run python app/graph.py                 # load org.csv and run the example queries
    uv run python app/graph.py "I'm Maria Lind. Who has to approve my expense claim of 800 euros?"
                                                           # GraphRAG: handbook + graph facts (needs NVIDIA_API_KEY)
"""

import csv
import sys
from pathlib import Path

import assistant
from neo4j import GraphDatabase

ORG_CHART = Path(__file__).parent / "org.csv"
driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "tokens-to-agents-local"))


def load_org_chart() -> None:
    """Rebuild the graph from org.csv: people, teams, and who reports to whom."""
    with ORG_CHART.open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        # MERGE = create if missing. $rows is a parameter: values never go into the query text.
        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Person {name: row.name}) SET p.title = row.title
            MERGE (t:Team {name: row.team})
            MERGE (p)-[:MEMBER_OF]->(t)
            """,
            rows=rows,
        )
        session.run(
            """
            UNWIND $rows AS row
            MATCH (p:Person {name: row.name}), (m:Person {name: row.reports_to})
            MERGE (p)-[:REPORTS_TO]->(m)
            """,
            rows=[row for row in rows if row["reports_to"]],
        )


def query(cypher: str, **parameters: str) -> list[dict]:
    with driver.session() as session:
        return [record.data() for record in session.run(cypher, **parameters)]  # pyright: ignore[reportArgumentType]


CHAIN = """
    MATCH path = (:Person {name: $name})-[:REPORTS_TO*]->(boss:Person)
    RETURN boss.name AS name, boss.title AS title, length(path) AS levels_up
    ORDER BY levels_up
"""
MANAGER = "MATCH (:Person {name: $name})-[:REPORTS_TO]->(boss) RETURN boss.name AS name, boss.title AS title"
NEAREST_DIRECTOR = """
    MATCH path = (:Person {name: $name})-[:REPORTS_TO*]->(boss:Person)
    WHERE boss.title STARTS WITH 'Director'
    RETURN boss.name AS name, boss.title AS title ORDER BY length(path) LIMIT 1
"""


def people_in(question: str) -> list[dict]:
    """The employees a question mentions by name."""
    people = query("MATCH (p:Person) RETURN p.name AS name, p.title AS title")
    return [person for person in people if person["name"].lower() in question.lower()]


def chain_facts(question: str) -> list[str]:
    """First attempt: hand the model the whole management chain and let it work out the rest."""
    facts = []
    for person in people_in(question):
        facts.append(f"{person['name']} is {person['title']}.")
        for boss in query(CHAIN, name=person["name"]):
            level = "Their manager" if boss["levels_up"] == 1 else f"{boss['levels_up']} levels above them"
            facts.append(f"{level} is {boss['name']}, {boss['title']}.")
    return facts


def graph_facts(question: str) -> list[str]:
    """Better: the database answers the structural question, and the fact is phrased in the policy's own words."""
    facts = []
    for person in people_in(question):
        name = person["name"]
        for boss in query(MANAGER, name=name):
            facts.append(f'For {name}, "their manager" means {boss["name"]} ({boss["title"]}).')
        for boss in query(NEAREST_DIRECTOR, name=name):
            facts.append(f'For {name}, "a director" means {boss["name"]} ({boss["title"]}).')
    return facts


def answer(question: str, facts: list[str]) -> str:
    """RAG as in assistant.py, plus graph facts as one more kind of passage."""
    from langchain_nvidia_ai_endpoints import ChatNVIDIA

    passages = [f"[{chunk['doc']}] {chunk['text']}" for chunk in assistant.retrieve(question)]
    passages += [f"[Org chart] {fact}" for fact in facts]
    llm = ChatNVIDIA(
        model="nvidia/nemotron-3.5-lightning-30b-a3b",
        temperature=0,
        max_completion_tokens=200,
        model_kwargs={"chat_template_kwargs": {"enable_thinking": False}},
        rate_limiter=assistant.RATE_LIMITER,
    )
    human = (
        "Passages:\n" + "\n".join(passages) + f"\n\nQuestion: {question}\n\n"
        "Answer in one or two sentences, then the sources."
    )
    return str(llm.invoke([("system", assistant.SYSTEM), ("human", human)]).content)


EXAMPLES = {
    "Who does Maria Lind report to?": MANAGER,
    "Everyone above Maria Lind": CHAIN,
    "The nearest director above Maria Lind": NEAREST_DIRECTOR,
    "Who shares a team with Maria Lind?": (
        "MATCH (:Person {name: $name})-[:MEMBER_OF]->(team)<-[:MEMBER_OF]-(colleague) "
        "RETURN team.name AS team, colleague.name AS name"
    ),
}

if __name__ == "__main__":
    load_org_chart()
    if len(sys.argv) == 2:
        question = sys.argv[1]
        print("no graph            :", answer(question, []))
        print("whole chain, facts  :", chain_facts(question))
        print("whole chain, answer :", answer(question, chain_facts(question)))
        print("resolved, facts     :", graph_facts(question))
        print("resolved, answer    :", answer(question, graph_facts(question)))
    else:
        for title, cypher in EXAMPLES.items():
            print(title, "->", query(cypher, name="Maria Lind"))
        print(
            "How many people are under Sara Holm? ->",
            query(
                "MATCH (p:Person)-[:REPORTS_TO*]->(:Person {name: $name}) RETURN count(p) AS people", name="Sara Holm"
            ),
        )
    driver.close()

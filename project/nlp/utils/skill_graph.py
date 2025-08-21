SKILL_RELATIONS = {
    "react": ["javascript", "frontend"], "node.js": ["javascript", "backend"],
    "express": ["node.js", "backend"], "mongodb": ["database", "nosql"],
    "python": ["programming", "backend"], "flask": ["python", "backend"],
    "django": ["python", "backend"], "java": ["programming", "backend"],
    "spring boot": ["java", "backend"], "sql": ["database"],
    "mysql": ["sql", "database"], "aws": ["cloud", "devops"],
    "docker": ["devops"], "git": ["version control"],
    "javascript": ["programming", "frontend"], "php": ["programming", "backend"]
}

def build_skill_network(skills):
    """Builds a nodes and edges list for graph visualization."""
    nodes = []
    edges = []
    node_ids = {}

    # Create a central "Candidate Skills" node
    candidate_node_id = 0
    nodes.append({"id": candidate_node_id, "label": "Candidate Skills", "group": "center"})
    node_ids["Candidate Skills"] = candidate_node_id
    
    id_counter = 1

    for skill in skills:
        skill = skill.lower()
        # Add the skill as a node
        if skill not in node_ids:
            nodes.append({"id": id_counter, "label": skill.title(), "group": "skill"})
            node_ids[skill] = id_counter
            edges.append({"from": candidate_node_id, "to": id_counter})
            id_counter += 1
        
        # Add related category nodes
        if skill in SKILL_RELATIONS:
            for related in SKILL_RELATIONS[skill]:
                if related not in node_ids:
                    nodes.append({"id": id_counter, "label": related.title(), "group": "category"})
                    node_ids[related] = id_counter
                    id_counter += 1
                # Create an edge from the skill to its category
                edges.append({"from": node_ids[skill], "to": node_ids[related]})

    return {"nodes": nodes, "edges": edges}
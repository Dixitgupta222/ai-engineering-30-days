def search_knowledge(keyword: str) -> bool:
    with open("app/knowledge/company_knowledge.md", "r") as file:
        content = file.read()

    return keyword.lower() in content.lower()

def find_knowledge_section(keyword: str) -> str:
    with open("app/knowledge/company_knowledge.md", "r") as file:
        content = file.read()

    sections = content.split("\n## ")

    for section in sections:
        if keyword.lower() in section.lower():
            return section

    return "No matching section found"
import re
import os
from langchain_core.documents import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

semantic_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile"
)

EXPORT_ROOT = "WyrdWiki\Wyrd Media Labs™ Company Wiki"

SECTION_MAPPING = {
    "The Core Stuff": [
        "What is Wyrd.md",
        "Why Wyrd.md"
    ],
    "The Journey": [
        "Act 1 Our Past.md",
        "Act 2 The Wyrd Dawn.md",
        "Act 3 The Future.md"
    ],
    "Business Stuff": [
        "What we stand for.md",
        "Who we’re for.md"
    ],
    "Brand Guidelines": [
        "How we speak.md",
        "How we roll.md",
        "How we're built.md"
    ],
    "Market Analysis": [
        "The Inconvenient Truth About Creative Industry.md",
        "Who are we fighting against.md"
    ]
}

def clean_text(text):

    # Remove <aside> and </aside> tags
    text = re.sub(r'</?aside>', '', text)

    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # Remove emojis / non-ascii
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    return text.strip()


def parse_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    page_title = None
    current_section = None
    current_subsection = None
    buffer = []
    sections = []

    structure_depth = 0  # 0=page,1=section,2=subsection
    last_heading_level = 1
    last_bullet_level = 0

    def flush():
        nonlocal buffer
        if buffer:
            sections.append({
                "section": current_section or "Intro",
                "subsection": current_subsection,
                "content": "\n".join(buffer).strip()
            })
            buffer = []

    for raw in lines:
        line = raw.rstrip("\n")


        stripped = clean_text(line.strip())

        if not stripped:
            continue

        
        # PAGE TITLE
        
        if stripped.startswith("# "):
            page_title = stripped[2:].strip()
            structure_depth = 0
            current_section = None
            current_subsection = None
            last_heading_level = 1
            continue

       
        # HEADING LOGIC
    
        heading_match = re.match(r'^(#{2,6})\s+(.*)', stripped)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip().replace("**", "")
    
            flush()

            # LEVEL 2 → Always Section
            if level == 2:
                current_section = title
                current_subsection = None
                structure_depth = 1

            # LEVEL 3 → Context dependent
            elif level == 3:

                # If previous heading was level 1 → section
                if last_heading_level == 1 and structure_depth == 0:
                    current_section = title
                    structure_depth = 1

                # If previous heading was level 2 → subsection
                elif last_heading_level == 2 and structure_depth == 1:
                    current_subsection = title
                    structure_depth = 2

                #If previous heading was level 3 and we are in subsection → new subsection
                elif last_heading_level == 3 and structure_depth == 2:
                    current_subsection = title
                    structure_depth = 2
                    
                else:
                    current_section = title
                    current_subsection = None
                    structure_depth = 1

            # LEVEL >= 4 → Content only
            else:
                buffer.append(title)

            last_heading_level = level
            continue

        
        # BULLET LOGIC
        
        if line.lstrip().startswith("- ") and ("**" in stripped):
            indent = len(line) - len(line.lstrip(" "))
            bullet_level = indent // 4
            bullet_text = stripped[2:].replace("**", "").strip()
            
            # Top-level bullet
            if bullet_level == 0:

                #last bullet level = 0 and structure depth = 0 → new section - first time
                if last_bullet_level == 0 and structure_depth == 0:
                    flush()
                    current_section = bullet_text
                    current_subsection = None
                    structure_depth = 1

                #last bullet level = 0 and structure depth = 1 and last heading was level >=2 → new subsection after ## or ### heading
                elif last_bullet_level == 0 and structure_depth >= 1 and last_heading_level == 2:
                    flush()
                    current_subsection = bullet_text
                    structure_depth = 2

                #last bullet level = 0 and structure depth = 1 → new section - section after first section
                elif last_bullet_level == 0 and structure_depth == 1:
                    flush()
                    current_section = bullet_text
                    current_subsection = None
                    structure_depth = 1

                #last bullet level = 1 and structure depth = 2 → new section - came from subsection
                elif last_bullet_level == 1 and structure_depth == 2:
                    flush()
                    current_section = bullet_text
                    current_subsection = None
                    structure_depth = 1

                #last bullet level = 2 and structure depth = 2 → new section - came from content
                elif last_bullet_level == 2 and structure_depth == 2:
                    flush()
                    current_section = bullet_text
                    current_subsection = None
                    structure_depth = 1

                #structure depth = 1 → new subsection
                elif structure_depth == 1:
                    flush()
                    current_subsection = bullet_text
                    structure_depth = 2

                #structure depth > 1 → content
                else:
                    buffer.append(bullet_text)

                last_bullet_level = 0
                continue

            # Indented bullet
            elif bullet_level == 1:
                
                #last bullet level = 0 and structure depth = 1 → new subsection first time
                if last_bullet_level == 0 and structure_depth == 1:
                        flush()
                        current_subsection = bullet_text
                        structure_depth = 2

                #last bullet level = 0 and structure depth = 2 and last heading was level >=2 → new subsection not after ## or ### heading
                elif last_bullet_level == 1 and structure_depth == 2 and not last_heading_level >= 2:
                        flush()
                        current_subsection = bullet_text
                        structure_depth = 2

                #last bullet level = 1 and structure depth = 2 → new subsection - subsection after first subsection
                elif last_bullet_level == 2 and structure_depth == 2:
                        flush()
                        current_subsection = bullet_text
                        structure_depth = 2
                    
                else:
                    buffer.append(bullet_text)

                last_bullet_level = 1
                continue

            else:
                buffer.append(bullet_text)
                last_bullet_level = bullet_level
                continue

        
        # NORMAL CONTENT
       
        buffer.append(stripped)
        

    flush()

    return sections

def split_long_sections(sections):

    split_sections = []

    for sec in sections:

        text = sec["content"]

        if not text:
            continue

        docs = semantic_splitter.create_documents([text])

        for d in docs:
            split_sections.append({
                "section": sec["section"],
                "subsection": sec["subsection"],
                "content": d.page_content
            })

    return split_sections

def load_all_documents():
    documents = []

    for section_title, subpages in SECTION_MAPPING.items():

        for subpage_file in subpages:

            subpage_path = os.path.join(EXPORT_ROOT, subpage_file)

            if not os.path.exists(subpage_path):
                print(f"⚠ Missing file: {subpage_path}")
                continue

            
            # Parse markdown and split long sections
            parsed_sections = parse_markdown(subpage_path)

            split_sections = split_long_sections(parsed_sections)

            page_name = subpage_file.replace(".md", "")

            for sec in split_sections:

                context_path = f"{section_title} > {page_name} > {sec['section']}"

                if sec["subsection"]:
                    context_path += f" > {sec['subsection']}"

                text = f"{context_path}\n\n{sec['content']}"

                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "title": section_title,
                            "subpage": page_name,
                            "section": sec["section"],
                            "subsection": sec["subsection"],
                            "source": subpage_file
                        }
                    )
                )

            
            # Handle nested subpages for "Who are we fighting against"
            if subpage_file == "Who are we fighting against.md":

                nested_folder = os.path.join(
                    EXPORT_ROOT,
                    "Who are we fighting against"
                )

                if os.path.isdir(nested_folder):

                    for nested_file in os.listdir(nested_folder):

                        if not nested_file.endswith(".md"):
                            continue

                        nested_path = os.path.join(nested_folder, nested_file)

                        nested_sections = parse_markdown(nested_path)

                        split_nested = split_long_sections(nested_sections)

                        nested_page = nested_file.replace(".md", "")

                        for sec in split_nested:

                            context_path = f"{section_title} > {page_name} > {nested_page} > {sec['section']}"

                            if sec["subsection"]:
                                context_path += f" > {sec['subsection']}"

                            text = f"{context_path}\n\n{sec['content']}"

                            documents.append(
                                Document(
                                    page_content=text,
                                    metadata={
                                        "title": section_title,
                                        "subpage": "Who are we fighting against",
                                        "nested_page": nested_page,
                                        "section": sec["section"],
                                        "subsection": sec["subsection"],
                                        "source": nested_file
                                    }
                                )
                            )

    return documents


if __name__ == "__main__":
    docs = load_all_documents()
    with open("parsed_docs.txt", "w", encoding="utf-8") as f:
        f.write(f"Total Documents: {len(docs)}\n\n")
        for doc in docs:
            f.write(f"---\n{doc.page_content}\n\n")
from src.schemas import ChunkRecord
from typing import List, Dict, Any
import uuid

def create_semantic_chunks(normalized_layout: List[Dict[str, Any]], document_id: str, chapter: str = "14") -> List[ChunkRecord]:
    """
    Creates semantic chunks based on layout features.
    Rules:
    - Preserve heading hierarchy
    - Keep tables atomic
    - Keep figure captions attached to nearby explanatory text
    - Keep definitions/examples/theorems intact
    - Avoid splitting code/pseudocode blocks blindly
    - Split oversized content only at paragraph boundaries
    """
    chunks = []
    current_chunk_text = []
    current_section_path = ["Root"]
    current_page_start = None
    current_page_end = None
    
    MAX_CHUNK_LENGTH = 1500
    
    def flush_chunk():
        nonlocal current_chunk_text, current_page_start, current_page_end
        if not current_chunk_text:
            return
            
        text = "\n\n".join(current_chunk_text)
        
        chunk = ChunkRecord(
            document_id=document_id,
            parser_strategy="semantic",
            chunk_id=str(uuid.uuid4()),
            chapter=chapter,
            section_path=" > ".join(current_section_path),
            page_start=current_page_start,
            page_end=current_page_end,
            content_type="text", 
            citation_label=f"{chapter} - {' > '.join(current_section_path)}",
            text=text
        )
        chunks.append(chunk)
        current_chunk_text = []
        current_page_start = None
        current_page_end = None

    for block in normalized_layout:
        block_text = block["text"]
        block_type = block["block_type"]
        page_num = block["page_num"]
        
        if current_page_start is None:
            current_page_start = page_num
        current_page_end = page_num
        
        if block_type == "heading":
            # Flush existing chunk before starting a new section
            flush_chunk()
            
            level = block.get("level", 1)
            # Update section path hierarchy
            if level <= len(current_section_path):
                current_section_path = current_section_path[:level]
            else:
                current_section_path.append(block_text)
                
            current_section_path[-1] = block_text
            
            current_chunk_text.append(block_text)
            current_page_start = page_num
            
        elif block_type in ["table", "code", "figure_caption"]:
            # These should not be split. If current chunk is getting big, flush first.
            current_length = sum(len(t) for t in current_chunk_text)
            if current_length + len(block_text) > MAX_CHUNK_LENGTH and current_length > 0:
                flush_chunk()
                current_page_start = page_num
                
            current_chunk_text.append(block_text)
            
            # Flush immediately after tables to keep them atomic and isolated
            if block_type == "table":
                flush_chunk()
                
        else:
            # Standard Paragraphs
            current_length = sum(len(t) for t in current_chunk_text)
            # Split oversized content only at paragraph boundaries
            if current_length + len(block_text) > MAX_CHUNK_LENGTH:
                flush_chunk()
                current_page_start = page_num
                
            current_chunk_text.append(block_text)

    # Flush any remaining text at the end of the document
    flush_chunk()
    
    return chunks

from typing import List, Dict, Any

def normalize_document_layout(documents: List[Any]) -> List[Dict[str, Any]]:
    """
    Normalizes Document AI output into a standard format.
    Extracts headings, paragraphs, tables, and their layout information.
    Handles DocumentLayout from the LAYOUT_PARSER_PROCESSOR.
    """
    normalized_blocks = []
    
    def process_block(block):
        # Base case: block has a text_block
        if hasattr(block, "text_block") and block.text_block:
            text = block.text_block.text.strip()
            type_ = block.text_block.type_.lower()
            page_num = getattr(block.page_span, "page_start", 1) if hasattr(block, "page_span") else 1
            
            if not text:
                pass
            else:
                block_type = "paragraph"
                level = 0
                
                if "heading" in type_ or "header" in type_:
                    block_type = "heading"
                    level = 1
                    if "-" in type_:
                        try:
                            level = int(type_.split("-")[-1])
                        except:
                            pass
                elif "table" in type_:
                    block_type = "table"
                elif "code" in type_ or "math" in type_ or "formula" in type_:
                    block_type = "code"
                else:
                    if text.startswith("Table "):
                        block_type = "table"
                    elif text.startswith("Figure "):
                        block_type = "figure_caption"
                        
                normalized_blocks.append({
                    "text": text,
                    "block_type": block_type,
                    "page_num": page_num,
                    "level": level
                })
        
        # Also process table_block if present
        elif hasattr(block, "table_block") and block.table_block:
            # Layout Parser might return table_block
            page_num = getattr(block.page_span, "page_start", 1) if hasattr(block, "page_span") else 1
            # Just add a placeholder if no text is extracted easily, 
            # but usually tables have text inside table_rows or similar.
            # For simplicity, if we get here we can try to extract nested blocks.
            pass
            
        # Recursive step: process child blocks
        if hasattr(block, "text_block") and hasattr(block.text_block, "blocks") and block.text_block.blocks:
            for child in block.text_block.blocks:
                process_block(child)

    for document in documents:
        if hasattr(document, "document_layout") and document.document_layout.blocks:
            for block in document.document_layout.blocks:
                process_block(block)
        else:
            # Fallback for standard Document AI OCR parser
            text = document.text
            for page in document.pages:
                page_num = page.page_number
                for block in page.blocks:
                    segments = block.layout.text_anchor.text_segments
                    block_text = "".join([text[segment.start_index:segment.end_index] for segment in segments]).strip()
                    if block_text:
                        normalized_blocks.append({
                            "text": block_text,
                            "block_type": "paragraph",
                            "page_num": page_num,
                            "level": 0
                        })

    return normalized_blocks

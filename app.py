#!/usr/bin/env python3
import sys
import re
import os
from pypdf import PdfReader, PdfWriter
import pdfplumber


def evaluate_chapter_start(page, page_num, pdf_path):
    """
    Evaluate if a page is likely a chapter start.
    Returns a score (higher = more likely to be chapter start).
    """
    score = 0
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            plumber_page = pdf.pages[page_num]
            text = plumber_page.extract_text() or ""
            
            # Get first 500 characters for analysis
            first_text = text[:500].strip()
            
            if not first_text:
                return 0
            
            # Check for chapter keywords at start of page
            chapter_patterns = [
                r'^CHAPTER\s+[IVX\d]+',
                r'^Chapter\s+[IVX\d]+',
                r'^PART\s+[IVX\d]+',
                r'^Part\s+[IVX\d]+',
                r'^SECTION\s+[IVX\d]+',
                r'^Section\s+[IVX\d]+',
            ]
            
            for pattern in chapter_patterns:
                if re.search(pattern, first_text, re.MULTILINE | re.IGNORECASE):
                    score += 100
                    break
            
            # Check for chapter title patterns
            lines = first_text.split('\n')
            if lines:
                first_line = lines[0].strip()
                
                # All caps title (common for chapters)
                if first_line and first_line.isupper() and len(first_line) > 5:
                    score += 30
                
                # Numeric or Roman numeral start
                if re.match(r'^[IVX\d]+[\.\s]', first_line):
                    score += 20
            
            # Check for substantial whitespace at top (typical for chapter starts)
            if len(lines) > 0 and not lines[0].strip():
                score += 10
            
            # Penalize very short pages (likely not chapter starts)
            if len(text) < 200:
                score -= 20
            
            # Bonus for pages that are multiples of common chapter lengths
            if page_num > 0 and page_num % 10 == 0:
                score += 5
            
    except Exception as e:
        print(f"Error evaluating page {page_num}: {e}", file=sys.stderr)
    
    return score


def find_chapter_boundaries(pdf_path, min_score=50):
    """
    Find chapter boundaries using evaluation function.
    Returns list of (page_number, score) tuples.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    boundaries = []
    
    print(f"Analyzing {total_pages} pages...", file=sys.stderr)
    
    for i in range(total_pages):
        score = evaluate_chapter_start(reader.pages[i], i, pdf_path)
        
        if score >= min_score:
            boundaries.append((i, score))
            print(f"Page {i+1}: score={score}", file=sys.stderr)
    
    return boundaries


def split_pdf_by_chapters(pdf_path, output_dir="chapters", min_score=50):
    """
    Split PDF into chapters based on evaluation scores.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    # Find chapter boundaries
    boundaries = find_chapter_boundaries(pdf_path, min_score)
    
    if not boundaries:
        print("No chapter boundaries found with current threshold.", file=sys.stderr)
        print(f"Try lowering min_score (current: {min_score})", file=sys.stderr)
        return
    
    # Add first page if not already included
    if not boundaries or boundaries[0][0] != 0:
        boundaries.insert(0, (0, 0))
    
    # Add end boundary
    boundaries.append((total_pages, 0))
    
    # Sort by page number
    boundaries.sort(key=lambda x: x[0])
    
    print(f"\nFound {len(boundaries)-1} chapters", file=sys.stderr)
    
    # Split into chapters
    for i in range(len(boundaries) - 1):
        start_page = boundaries[i][0]
        end_page = boundaries[i + 1][0]
        
        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        output_path = os.path.join(output_dir, f"chapter_{i+1:02d}_pages_{start_page+1}-{end_page}.pdf")
        
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        print(f"Created: {output_path}", file=sys.stderr)
    
    print(f"\nChapters saved to: {output_dir}/", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <pdf_file> [output_dir] [min_score]")
        print("  pdf_file: Path to input PDF")
        print("  output_dir: Directory for output chapters (default: chapters)")
        print("  min_score: Minimum score for chapter detection (default: 50)")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "chapters"
    min_score = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    split_pdf_by_chapters(pdf_path, output_dir, min_score)


if __name__ == "__main__":
    main()

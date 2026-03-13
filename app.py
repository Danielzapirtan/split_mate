import re
from pathlib import Path
import sys


def detect_chapters(file_path):
    """Detect chapter markers in text file."""
    chapters = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        
        # Pattern: "CHAPTER X" or "CHAPTER X Title"
        match = re.match(r'^CHAPTER\s+(\d+)(?:\s+(.*))?$', line, re.IGNORECASE)
        if match:
            chapter_num = int(match.group(1))
            title = match.group(2) if match.group(2) else ""
            
            # Skip if this is just a table of contents entry (has page number at end)
            if re.search(r'\d+\s*$', title):
                continue
                
            chapters.append({
                'number': chapter_num,
                'line': line_num,
                'title': title.strip(),
                'full_text': line
            })
    
    return chapters, lines


def split_text_by_chapters(file_path, output_dir=None):
    """Split text file into separate files for each chapter."""
    file_path = Path(file_path)
    
    if output_dir is None:
        output_dir = file_path.parent / f"{file_path.stem}_chapters"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    chapters, lines = detect_chapters(file_path)
    
    if not chapters:
        print("No chapters detected.")
        return
    
    print(f"Found {len(chapters)} chapters:\n")
    for ch in chapters:
        title_text = f" - {ch['title']}" if ch['title'] else ""
        print(f"  Chapter {ch['number']}{title_text} (line {ch['line'] + 1})")
    
    print(f"\nSplitting into separate files...\n")
    
    # Write front matter (before first chapter)
    if chapters[0]['line'] > 0:
        front_matter = ''.join(lines[:chapters[0]['line']])
        output_path = output_dir / "00_front_matter.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(front_matter)
        print(f"Front matter: Lines 1-{chapters[0]['line']} -> {output_path.name}")
    
    # Write each chapter
    for i, chapter in enumerate(chapters):
        start_line = chapter['line']
        end_line = chapters[i + 1]['line'] if i + 1 < len(chapters) else len(lines)
        
        chapter_text = ''.join(lines[start_line:end_line])
        
        # Create filename
        safe_title = re.sub(r'[^\w\s-]', '', chapter['title'])[:50].strip()
        safe_title = safe_title.replace(' ', '_') if safe_title else ''
        filename = f"chapter_{chapter['number']:02d}"
        if safe_title:
            filename += f"_{safe_title}"
        filename += ".txt"
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(chapter_text)
        
        print(f"Chapter {chapter['number']}: Lines {start_line + 1}-{end_line} -> {output_path.name}")
    
    print(f"\nSplit complete. Output directory: {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python app.py <text_file> [output_directory]")
        print("\nOptimized for DBT therapy books and similar text files with CHAPTER markers.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    
    split_text_by_chapters(input_file, output_directory)

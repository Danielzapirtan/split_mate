#!/usr/bin/env python3
"""
PDF Chapter Splitter for "Chain Analysis in Dialectical Behavior Therapy"
Splits the PDF into individual chapter files based on predefined page ranges.
"""

import os
import argparse
from pathlib import Path
import PyPDF2
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFChapterSplitter:
    """
    Splits a PDF file into chapters based on predefined page ranges.
    """
    
    # Chapter definitions with page ranges (1-indexed as in the PDF)
    # Format: (start_page, end_page, title)
    CHAPTERS = [
        (2, 25, "00_Title_and_Front_Matter"),
        (26, 47, "01_Chapter_1_The_Basics"),
        (48, 66, "02_Chapter_2_Orientation_and_Collaboration"),
        (67, 98, "03_Chapter_3_Getting_to_Know_Target_Behavior"),
        (99, 120, "04_Chapter_4_Keeping_Client_Engaged"),
        (121, 144, "05_Chapter_5_Incorporating_Solutions"),
        (145, 161, "06_Chapter_6_When_Behavior_Not_Changing"),
        (162, 183, "07_Chapter_7_Thoughts_Urges_Missing_Behaviors"),
        (183, 203, "08_Chapter_8_Consultation_Teams_Skills_Phone"),
        (204, 212, "09_References_and_Index"),
    ]
    
    def __init__(self, input_pdf_path: str, output_dir: str):
        """
        Initialize the PDF splitter.
        
        Args:
            input_pdf_path: Path to the input PDF file
            output_dir: Directory where chapter PDFs will be saved
        """
        self.input_pdf_path = Path(input_pdf_path)
        self.output_dir = Path(output_dir)
        
        # Validate input file
        if not self.input_pdf_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {self.input_pdf_path}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_pdf_info(self) -> Tuple[int, List[str]]:
        """
        Get information about the PDF file.
        
        Returns:
            Tuple of (total_pages, list of existing chapter files)
        """
        try:
            with open(self.input_pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Check for existing chapter files
                existing_chapters = []
                for _, _, title in self.CHAPTERS:
                    chapter_file = self.output_dir / f"{title}.pdf"
                    if chapter_file.exists():
                        existing_chapters.append(str(chapter_file))
                
                return total_pages, existing_chapters
                
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
    
    def validate_page_ranges(self, total_pages: int) -> bool:
        """
        Validate that chapter page ranges are within the PDF.
        
        Args:
            total_pages: Total number of pages in the PDF
            
        Returns:
            True if all ranges are valid, False otherwise
        """
        valid = True
        for start, end, title in self.CHAPTERS:
            if start < 1 or end > total_pages + 2:
                logger.warning(f"Chapter '{title}' range ({start}-{end}) exceeds PDF pages (1-{total_pages})")
                valid = False
            elif start > end:
                logger.warning(f"Chapter '{title}' has invalid range: start ({start}) > end ({end})")
                valid = False
        return valid
    
    def split_chapter(self, start_page: int, end_page: int, chapter_title: str) -> Path:
        """
        Extract a single chapter from the PDF.
        
        Args:
            start_page: First page number (1-indexed)
            end_page: Last page number (1-indexed)
            chapter_title: Title for the output file
            
        Returns:
            Path to the created chapter PDF
        """
        output_file = self.output_dir / f"{chapter_title}.pdf"
        
        try:
            with open(self.input_pdf_path, 'rb') as infile:
                pdf_reader = PyPDF2.PdfReader(infile)
                pdf_writer = PyPDF2.PdfWriter()
                
                # PyPDF2 uses 0-indexed pages
                for page_num in range(start_page - 2, end_page - 1):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                with open(output_file, 'wb') as outfile:
                    pdf_writer.write(outfile)
                    
            logger.info(f"Created: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error creating chapter '{chapter_title}': {e}")
            raise
    
    def split_all_chapters(self, force: bool = False) -> List[Path]:
        """
        Split all chapters from the PDF.
        
        Args:
            force: If True, overwrite existing chapter files
            
        Returns:
            List of paths to created chapter files
        """
        # Get PDF info
        total_pages, existing_chapters = self.get_pdf_info()
        logger.info(f"PDF has {total_pages} pages")
        
        # Check for existing files
        if existing_chapters and not force:
            logger.warning("Some chapter files already exist. Use --force to overwrite:")
            for chapter in existing_chapters:
                logger.warning(f"  {chapter}")
            return []
        
        # Validate page ranges
        if not self.validate_page_ranges(total_pages):
            logger.error("Invalid page ranges detected. Please check chapter definitions.")
            return []
        
        # Split each chapter
        created_files = []
        for start, end, title in self.CHAPTERS:
            try:
                output_file = self.split_chapter(start, end, title)
                created_files.append(output_file)
            except Exception as e:
                logger.error(f"Failed to split chapter '{title}': {e}")
                
        logger.info(f"Successfully created {len(created_files)} chapter files")
        return created_files
    
    def create_metadata_file(self) -> Path:
        """
        Create a metadata file with chapter information.
        
        Returns:
            Path to the created metadata file
        """
        metadata_file = self.output_dir / "chapter_metadata.txt"
        
        try:
            with open(metadata_file, 'w') as f:
                f.write("Chapter Metadata for 'Chain Analysis in Dialectical Behavior Therapy'\n")
                f.write("=" * 60 + "\n\n")
                f.write("Generated by PDF Chapter Splitter\n\n")
                
                for i, (start, end, title) in enumerate(self.CHAPTERS):
                    # Extract clean chapter name without prefix
                    if i == 0:
                        chapter_name = "Title and Front Matter"
                    else:
                        chapter_name = title.replace(f"{i:02d}_", "").replace("_", " ")
                    
                    f.write(f"Chapter {i}: {chapter_name}\n")
                    f.write(f"  File: {title}.pdf\n")
                    f.write(f"  Pages: {start} - {end}\n\n")
                    
            logger.info(f"Created metadata file: {metadata_file}")
            return metadata_file
            
        except Exception as e:
            logger.error(f"Error creating metadata file: {e}")
            raise


def main():
    """Main function to run the PDF chapter splitter."""
    parser = argparse.ArgumentParser(
        description="Split 'Chain Analysis in Dialectical Behavior Therapy' PDF into chapters"
    )
    parser.add_argument(
        "--input", "-i",
        default="/content/drive/MyDrive/boox/Chain.pdf",
        help="Path to input PDF file (default: /content/drive/MyDrive/boox/Chain.pdf)"
    )
    parser.add_argument(
        "--output", "-o",
        default="/content/drive/MyDrive/output_dir",
        help="Output directory for chapter PDFs (default: /content/drive/MyDrive/output_dir)"
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force overwrite of existing chapter files"
    )
    parser.add_argument(
        "--info", "-n",
        action="store_true",
        help="Only show PDF information without splitting"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize splitter
        splitter = PDFChapterSplitter(args.input, args.output)
        
        # Get PDF info
        total_pages, existing_chapters = splitter.get_pdf_info()
        logger.info(f"PDF: {args.input}")
        logger.info(f"Total pages: {total_pages}")
        
        if args.info:
            logger.info("\nChapter definitions:")
            for start, end, title in splitter.CHAPTERS:
                logger.info(f"  {title}: pages {start}-{end}")
            return
        
        # Split chapters
        logger.info(f"Output directory: {args.output}")
        created_files = splitter.split_all_chapters(force=args.force)
        
        if created_files:
            # Create metadata file
            splitter.create_metadata_file()
            logger.info(f"\nSuccessfully created {len(created_files)} chapter files in: {args.output}")
        else:
            logger.info("No files were created. Use --force to overwrite existing files.")
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.info("\nMake sure your Google Drive is mounted and the file exists at:")
        logger.info("  /content/drive/MyDrive/boox/Chain.pdf")
        logger.info("\nTo mount Google Drive in Colab, run:")
        logger.info("  from google.colab import drive")
        logger.info("  drive.mount('/content/drive')")
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
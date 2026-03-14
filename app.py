import os
import tarfile
from PyPDF2 import PdfReader, PdfWriter
from google.colab import drive

# 1. Mount your Google Drive
drive.mount('/content/drive')

# 2. Configuration
input_pdf_path = "/content/drive/MyDrive/boox/DSD.pdf" # Ensure this matches your filename
output_folder = "Dont_Shoot_The_Dog_Chapters"
archive_name = "Dont_Shoot_The_Dog_Split.tar.gz"
drive_destination = "/content/drive/MyDrive/"

chapters = [
    ("0_Intro_and_Foreword", 1, 11),
    ("1_Reinforcement", 12, 41),
    ("2_Shaping", 42, 70),
    ("3_Stimulus_Control", 71, 96),
    ("4_Untraining", 97, 138),
    ("5_Real_World_Applications", 139, 152),
    ("6_Clicker_Training", 153, 168),
    ("7_Resources_and_Author", 169, 173)
]

# 3. Create temp folder and split PDF
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

reader = PdfReader(input_pdf_path)

for title, start, end in chapters:
    writer = PdfWriter()
    # Subtract 1 because list indices start at 0
    for page_num in range(start - 1, end):
        writer.add_page(reader.pages[page_num])
    
    file_path = os.path.join(output_folder, f"{title}.pdf")
    with open(file_path, "wb") as f:
        writer.write(f)
    print(f"Created: {title}.pdf")

# 4. Create .tar.gz archive
with tarfile.open(archive_name, "w:gz") as tar:
    tar.add(output_folder, arcname=os.path.basename(output_folder))

# 5. Move to Google Drive
final_path = os.path.join(drive_destination, archive_name)
os.rename(archive_name, final_path)

print(f"\nSuccess! Your file has been saved to your Google Drive at: {final_path}")
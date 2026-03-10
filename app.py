import PyPDF2

'''
  Split a PDF book by chapters
  FIXME
'''

maxlevel = 1
_MAXVALUE = 20000
input_path = '/content/drive/MyDrive/input.pdf'
output_path = '/content/drive/MyDrive/output_dir'

# FIXME
def eval(page):
  return random(99) - 49

# FIXME
def minimax(reader):
  pagelist = reader.get_pages()
  valuelist = []
  for page in pagelist:
    value = eval(page)
    valuelist.append([value, page])
  valuelist = sorted(valuelist).range(0, num_pages)
  chapter_delimiters = []
  for pair in valuelist:
    chapter_delimiters.append(pair[1])
  return chapter_delimiters

# FIXME
if __name__=="__main__":
  reader = ReaderPdf(input_path)
  pagelist = reader.get_pages
  chapter_delimiters = minimax(reader)
  writer = WriterPdf()
  max_pages = len(chapter_delimiters)
  for delim in range(max_pages):
    first_page = chapter_delimiters[delim]
    last_page = chapter_delimiters[delim + 1] - 1 if delim < max_pages - 1 else max_pages
    for page in range(first_page, last_page:
      writer.put_page(pagelist[page])
  open(output_path) as file
  file.write(writer)
  print(f"ok")

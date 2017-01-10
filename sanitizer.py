import os,sys
import re
import string

#Alison says hi too!


def get_input_file():

  if(len(sys.argv) != 2):
    print 'Usage: python sanitizer_new.py <filename.pdf>'
    return
  pdf_input_string = sys.argv[1]
  return pdf_input_string[:-4]


def get_txt_filename(input_string):
  os.system("./pdftotext %s.pdf -enc UTF-8 -layout" % str(input_string))
  txt_filename = input_string + ".txt"
  return txt_filename


def concatenate_string_list(resume_lines):
  resume_str = ''
  for line in resume_lines:
    line = line.strip().replace('\t', ' ') + ' '
    resume_str = resume_str + line + ','
  return resume_str


def call_NLP(resume_lines):
  resume_str = concatenate_string_list(resume_lines)
  resume_str = "\"" + resume_str + "\""
  os.system("python analyze.py entities %s > entities.txt" % str(resume_str))

def get_entities(resume_lines, entity_file):
  entities = ['LOCATION', 'ORGANIZATION', 'PERSON']
  pii = []
  for entity_line in entity_file:
    if 'COMMON' in entity_line:
      next(entity_file)
      next(entity_file)
      next(entity_file)
      next(entity_file)
      next(entity_file)
    else:
      for word in entities:
        if word in entity_line:
          next_line = next(entity_file)
          next_line = next_line.replace('"name": "', '')
          next_line = next_line.replace('",', '')
          next_line = next_line.strip()
          if len(next_line) > 1:
            if word != 'PERSON' or next_line[0].isupper():
              print 'adding pii: ' + next_line
              pii.append(next_line + '\\' + word)
  pii.sort(lambda x,y: cmp(len(y), len(x)))
  return pii


def get_regex_phone():
  regular_expression = re.compile(r"\(?"
                                  r"(\d{3})?"
                                  r"\)?"
                                  r"[\t\s\.-]{0,5}?"
                                  r"(\d{3})"
                                  r"[\s\.-]{0,3}"
                                  r"(\d{4})"
                                  , re.IGNORECASE)
  return regular_expression

def get_regex_zip():
  regular_expression = re.compile(r'.*(\d{5}(\-\d{4})?)$')
  return regular_expression

def remove_phone_and_web(line, tags, regex_phone, regex_zip):
  for word in line.split():
    for tag in tags:
      if tag in word.lower():
        line = line.replace(word, '<WEB-ADDRESS>')
    try:
      result = re.search(regex_phone, word)
      if result:
        line = line.replace(word, '<PHONE-NUMBER>')
      result = re.search(regex_zip, word)
      if result:
        line = line.replace(word, '<ZIP>')
    except:
      pass
  return line

def remove_pii(resume_lines, pii):
  tags = ['@', '.com', '.edu', 'http', 'https', '.org', '.net', 'www.']
  regex_phone = get_regex_phone()
  regex_zip = get_regex_zip()
  for i,line in enumerate(resume_lines):
    line = remove_phone_and_web(line, tags, regex_phone, regex_zip)
    for pairs in pii:
      pair = pairs.split('\\')
      line = line.replace(pair[0] + ' ', '<' + pair[1] + '> ')
      line = line.replace(' ' + pair[0], ' <' + pair[1] + '>')
    resume_lines[i] = line
  return resume_lines



if __name__ == '__main__':
  input_string = get_input_file() #ex. clavelli_resume

  txt_filename = get_txt_filename(input_string) #ex. clavelli_resume.pdf
  with open(txt_filename) as resume_txt_file:
    resume_lines = resume_txt_file.readlines()

  copy_lines = list(resume_lines)
  call_NLP(copy_lines)
  entity_file = open('entities.txt', 'r')
  pii = get_entities(resume_lines, entity_file)
  entity_file.close()

  edited_lines = remove_pii(resume_lines, pii)

  output = open(input_string + '_sanitized.txt', 'w')
  for line in edited_lines:
    output.write(line)
  output.close()

import os,sys
import re
import string

#Sydney says hello!

def getRegex():
  regular_expression = re.compile(r"\(?"  # open parenthesis
                                  r"(\d{3})?"  # area code
                                  r"\)?"  # close parenthesis
                                  r"[\t\s\.-]{0,5}?"  # area code, phone separator
                                  r"(\d{3})"  # 3 digit local
                                  r"[\s\.-]{0,3}"  # 3 digit local, 4 digit local separator
                                  r"(\d{4})"  # 4 digit local
                                  , re.IGNORECASE)
  return regular_expression


def removePhoneAndWeb(line, tags, regex):
  for word in line.split():
      #remove web#
    for tag in tags:
      if tag in word.lower():
        line = line.replace(word, '<WEB-ADDRESS>')
        break
      #end#

    try:
      result = re.search(regex, word)
      if result:
        line = line.replace(word, '<PHONE-NUMBER>')
    except:
      pass
  return line


def removePII(resumeLines, pii):
  tags =  ['.com', '.edu', 'http', 'https', '.org', '.net', 'www.']
  regex = getRegex()
  #removePhoneAndWeb(resumeLines)
  i = 0 #ratchet -thomas
  for line in resumeLines:
    line = removePhoneAndWeb(line, tags, regex)
    for pairs in pii:
      pair = pairs.split('\\')
      line = line.replace(pair[0], '<' + pair[1] + '>')
    resumeLines[i] = line
    i = i + 1
  return resumeLines



def getEntities(resumeLines, entityFile):
  entities = ['LOCATION', 'ORGANIZATION', 'PERSON']
  pii = []
  for entityLine in entityFile:
    for word in entities: #possible bug if the user has token 'LOCATION' or 'ORGANIZATION' or 'PERSON' in resume
      if word in entityLine:
        next_line = next(entityFile)
        next_line = next_line.replace('"name": "', '')
        next_line = next_line.replace('",', '')
        next_line = next_line.strip()

        if len(next_line) > 1:
          if word != 'PERSON' or next_line[0].isupper():
            #print word + " : " + next_line
            pii.append(next_line + '\\' + word)
       #break out of for loop
  pii.sort(lambda x,y: cmp(len(y), len(x)))
  return pii


def concatenateStringList(resumeLines):
  resumeStr = ''
  for line in resumeLines:
    line = line.strip().replace("\t", " ") + ' '
    resumeStr = resumeStr + line + "," #PLUS NEWLINE SEPARATOR XXX
  return resumeStr


def callNLP(resumeLines):
  resumeStr = concatenateStringList(resumeLines)
  resumeStr = "\"" + resumeStr + "\""
  os.system("python analyze.py entities %s > entities.txt" % str(resumeStr))
  return 'entities.txt' #this is if we want a custom entity file TODO: remove
  


def getResumeTxtFilename(inputString):
  os.system("./pdftotext %s.pdf -enc UTF-8 -layout" % str(inputString))
  txtFilename = inputString + ".txt"
  return txtFilename

def getInputFile():
  if(len(sys.argv) != 2):
    print 'Usage: python sanitizer.py <filename.pdf>'
    return
  pdfInputString = sys.argv[1]
  return pdfInputString[:-4]


if __name__ == '__main__':

  '''outline of steps in this process'''
  # 1. get desired pdf file
  # 2. run that file through pdf2text
  # 3. take the output of pdf2text and run that through google NLP, getting a pii list from that
  # 4. go through the pdf2text output again, this time removing pii from pii list and saving them into line list
  # 5. read lines from line list into a new file
  '''end'''

    #step 1
inputString = getInputFile()
#inputString = 'resumehutton_pdf' #temporary

    #step 2
resumeTxtFilename = getResumeTxtFilename(inputString)
#resumeTxtFilename =  'resumehutton_pdf.txt' #temporary
with open(resumeTxtFilename) as resumeTxtFile:
  resumeLines = resumeTxtFile.readlines()

    #step 3
entityFilename = callNLP(resumeLines)
#entityFilename = 'huttonEntities.txt' #temporary
entityFile = open(entityFilename, 'r')
pii = getEntities(resumeLines, entityFile)
entityFile.close()
  
    #step 4
editedLines = removePII(resumeLines, pii)

    #step 5
output = open(inputString + '_sanitized.txt', 'w')
for line in editedLines:
  output.write(line)
output.close()


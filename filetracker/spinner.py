import sys

def Spinner(update_intervall=100):
     counter = 0
     while True:
          if counter%update_intervall==0:
              if   counter%5 == 1: marker = '\\'
              elif counter%5 == 2: marker = '|'
              elif counter%5 == 3: marker = '/'
              elif counter%5 == 0: marker = '-'
              sys.stderr.write('Processed: {0} {1} files/dirs \r'.format(marker,counter))
          counter += 1
          yield counter

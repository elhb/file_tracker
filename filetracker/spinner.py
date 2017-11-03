import sys

def Spinner():
     counter = 0
     while True:
          if   counter%5 == 1: marker = '\\'
          elif counter%5 == 2: marker = '|'
          elif counter%5 == 3: marker = '/'
          elif counter%5 == 0: marker = '-'
          sys.stderr.write('Processed: {0} {1} files/dirs \r'.format(marker,counter))
          counter += 1
          yield counter
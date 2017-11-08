import sys
import psutil

def Spinner(update_intervall=100, with_memory=True, mem_intervall=100000):
     counter = 0
     while True:
          if counter%update_intervall==0:
              if   counter%5 == 1: marker = '\\'
              elif counter%5 == 2: marker = '|'
              elif counter%5 == 3: marker = '/'
              elif counter%5 == 0: marker = '-'
              sys.stderr.write('Processed: {0} {1} files/dirs \r'.format(marker,counter))
              if with_memory and counter%mem_intervall==0:   sys.stderr.write('Processed: {0} {1} files/dirs {2}% of system memory used \r'.format(marker,counter,psutil.virtual_memory().percent))
          counter += 1
          yield counter
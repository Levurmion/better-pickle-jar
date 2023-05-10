import os
import sys
import subprocess as sub
import pickle as p
from typing import Callable
import inspect

class PickleShelf:
   '''
   Configure `betterpicklejar` with a `pickle_shelf` directory in the root of your project. This is where you will keep all of your `PickleJars` for each individual file. Your project's directory should be configured as a `PYTHONPATH` environment variable from your virtual environment's `activate.sh` file (typically in `venv/bin`). This will be seen as your `PickleShelf's` root directory.
   '''
   
   # class attributes
   _PickleShelf_instance = None
   _PickleShelf_dir = None
   _instantiated = False
   
   def __new__(cls, *args, **kwargs):
      if cls._PickleShelf_instance is None:
         cls._PickleShelf_instance = super().__new__(cls) # super() refers to the <object> Python base class
      return cls._PickleShelf_instance
   
   def __init__(self, shelf_dir: str):
      if PickleShelf._instantiated is False:
         PickleShelf._PickleShelf_dir = self.__build_shelf(shelf_dir)
         PickleShelf._instantiated = True
      elif PickleShelf._instantiated is True:
         PROJECT_PATH = os.environ.get('PYTHONPATH')
         print(f"WARNING: Your PickleShelf is already configured in the directory:\n{os.path.join(PROJECT_PATH, PickleShelf._PickleShelf_dir)}")
         
   def __build_shelf(self, shelf_dir: str):
      PROJECT_PATH = os.environ.get('PYTHONPATH')
      SCRIPT_PATH = os.path.join(os.path.dirname(__file__),'build_shelf.sh')
      SHELF_DIR = os.path.join(PROJECT_PATH, shelf_dir)
      # make sure it is executable
      sub.call(f'chmod +x {SCRIPT_PATH}', shell=True)
      sub.run([SCRIPT_PATH, SHELF_DIR])
      print(f'Your PickleShelf is configured in the directory:\n{SHELF_DIR}')
      return SHELF_DIR


class PickleJar:
   
   def __init__(self):
      current_frame = inspect.currentframe()
      # Get the outer frame (caller's frame)
      caller_frame = current_frame.f_back
      # Get the caller's code object
      caller_code = caller_frame.f_code
      # Get the caller's file name
      caller_filename = inspect.getfile(caller_code)

      self.uniqueFilename = os.path.relpath(os.path.abspath(caller_filename), start=os.environ.get('PYTHONPATH')).replace('/','_')
      self.PATH_TO_JAR = os.path.join(PickleShelf._PickleShelf_dir, self.uniqueFilename + '_JAR')
      self.pickleTracker = {}

      if os.path.exists(self.PATH_TO_JAR) and os.path.isdir(self.PATH_TO_JAR):
         print(f'Your current PickleJar is in the directory: {self.PATH_TO_JAR}')
      else:
         self.__build_jar()
         
   
   def __build_jar(self):
      SHELF_DIR = PickleShelf._PickleShelf_dir
      PROJECT_PATH = os.environ.get('PYTHONPATH')
      SCRIPT_PATH = SCRIPT_PATH = os.path.join(os.path.dirname(__file__),'build_jar.sh')
      JAR_DIR = os.path.join(SHELF_DIR, self.uniqueFilename + '_JAR')
      # make sure it is executable
      sub.call(f'chmod +x {SCRIPT_PATH}', shell=True)
      sub.run([SCRIPT_PATH, JAR_DIR])
      print(f'Your PickleJar is configured in the directory:\n{JAR_DIR}')
   
   
   def __str__(self):
      pickleList = list(self.pickleTracker.keys())
      file = os.path.relpath(__file__, start=os.environ.get('PYTHONPATH'))
      return f'Current pickles in {file}:\n- ' + '\n- '.join(pickleList)
   
   
   # method to use pickles
   def pickle(self, callback: Callable, pickle_name: str):
      
      # check if pickle_name has been used before
      try:
         pickleExists = self.pickleTracker[pickle_name]
         if pickleExists:
            raise Exception(f'\n`{pickle_name}` has already been used. If you are trying to access the same pickle, refer to the variable where `{pickle_name}` was bound to. Otherwise, use a different name.\n\nCall `self.my_pickles()` or print(self) to get the list of currently available pickles.')
      except KeyError:
         self.pickleTracker[pickle_name] = True
      
      picklePath = os.path.join(self.PATH_TO_JAR, pickle_name + '.pkl')

      # dump or load pickle
      if os.path.exists(picklePath) and os.path.isfile(picklePath):
         with open(picklePath, 'rb') as pickleFile:
            return p.load(pickleFile)
      
      else:
         value = callback()
         
         with open(picklePath, 'wb') as pickleFile:
            p.dump(value, pickleFile)
         
         return value
      
   
   def my_pickles(self):
      return list(self.pickleTracker.keys())


def usePickleJar():
   instance = PickleJar()
   return instance, instance.pickle



if __name__ == '__main__':
   
   shelf = PickleShelf('PICKLE_SHELF')

   jar, pickle = usePickleJar()
   
   def load_string():
      return 'string'
   
   string = pickle(load_string, 'my_string')

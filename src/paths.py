import os
import re

class Paths():

    def __init__(self, path=None, root=None):

        if root is None: 
            self.root = self.get_root_path()
        else:
            self.root = root

        if path is None:
            self.path = self.root    
        else:
            self.path = path

        subdirs = [directory for directory in os.listdir(self.path) if os.path.isdir(self.join_to_path(directory))]
        self.subdirs = subdirs
        self.set_subdirs(subdirs)        
        
        self.files = [file for file in os.listdir(self.path) if os.path.isfile(self.join_to_path(file))]
        self.filepaths = [self.join_to_path(file) for file in self.files]

    def __repr__(self):
        """Represent object as class name and path"""

        return f"<{str(self.__class__).strip('<>')}: {self.path}>"

    def set_subdirs(self, subdirs):
        """Create Paths objects for each subdir"""

        for subdir in subdirs:
            setattr(self, subdir, Paths(self.join_to_path(subdir), self.root))

    def join_to_path(self, path):
        """Join path to objects internal path"""

        return os.path.join(self.path, path)
    
    def get_root_path(self):
        """Find walk up directories until `.root` file is found
        Set that to root directory of the project"""

        current_dir = os.path.dirname(__file__)
        path = current_dir

        while path != os.environ['HOME']:
            for file in os.listdir(path):
                if file == '.root':
                    return path
                
            path = os.path.dirname(path)



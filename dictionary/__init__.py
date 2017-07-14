from cassandra.cluster import Cluster
from dictionary.constants import *
from dictionary.phrase import Phrase
from dictionary.dictionary import Dictionary
from dictionary.interface import *

init_fail = False

cluster = Cluster()

# Find something better!
if not (Dictionary.ConnectToDatabase(cluster) and 
        Dictionary.BuildPreparedStatements()):
    init_fail = True

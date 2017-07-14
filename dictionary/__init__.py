from cassandra.cluster import Cluster
from dictionary.phrase import Phrase
from dictionary.dictionary import Dictionary
from dictionary.constants import *
from dictionary.interface import *

cluster = Cluster()
Dictionary.ConnectToDatabase(cluster)
Dictionary.BuildPreparedStatements()

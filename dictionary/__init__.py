from cassandra.cluster import Cluster
from dictionary.dictionary import Dictionary
from dictionary.constants import *
from dictionary.interface import *

import sys

cluster = Cluster()
Dictionary.ConnectToDatabase(cluster)
Dictionary.BuildPreparedStatements()

from cassandra.cluster import Cluster
from dictionary.dictionary import Dictionary
from dictionary.constants import *
import sys

cluster = Cluster()
Dictionary.ConnectToDatabase(cluster)

from cassandra.cluster import Cluster
from dictionary.constants import *
from dictionary.textprocessor import *
from dictionary.phrase import Phrase
from dictionary.dictionary import Dictionary
from dictionary.offer import Offer
from dictionary.document import Document
from dictionary.interface import *

init_fail = False

cluster = Cluster()

# Find something better!
if not (Dictionary.ConnectToDatabase(cluster) and 
        Dictionary.BuildPreparedStatements() and
        Offer.ConnectToDatabase(cluster)):

    init_fail = True

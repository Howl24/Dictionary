from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
from dictionary.constants import *
from dictionary.textprocessor import *
from dictionary.phrase import Phrase
from dictionary.dictionary import Dictionary
from dictionary.offer import Offer
from dictionary.document import Document
from dictionary.interface import *

cluster = Cluster()

try:
    Dictionary.ConnectToDatabase(cluster)
    Offer.ConnectToDatabase(cluster)
except NoHostAvailable:
    print("Ningun servicio de cassandra esta disponible.")
    print("Inicie un servicio con el comando " +
          "\"sudo cassandra -R\"")
    print()
    raise ImportError

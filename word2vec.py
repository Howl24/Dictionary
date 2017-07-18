import gensim
from main import get_documents

KEYSPACES = ['new_btpucp']
FEATURES = ['Description','Qualifications', 'Software']

def train(documents):
#    model = gensim.models.Word2Vec(documents)
#    print(len(model.wv.vocab))

    all_phrases = []
    for doc in documents:
        phrases = doc.split()
        all_phrases.append(phrases)

    model = gensim.models.Word2Vec(all_phrases)

    for word in model.wv.vocab:
        print(word)

    #print(model.wv.most_similar(positive=['Gestión']))
    return model

def save(model):
    model.save('w2v/model')


def main():
    documents = get_documents(KEYSPACES, FEATURES)
    model = train(documents)
    save(model)

if __name__ == "__main__":
    main()
    print("Fin del entrenamiento!")

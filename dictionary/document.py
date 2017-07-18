from dictionary import remove_whitespaces

class Document:

    def __init__(self, text, source):
        self.source = source
        self.text = text


    @staticmethod
    def text_list(documents):
        texts = []
        for doc in documents:
            texts.append(doc.text)

        return texts

    def process_text(self):
        """ Processing text:
            - Lower case
            - Remove whitespaces
        """

        text = self.text
        text = text.lower()
        text = remove_whitespaces(text)
        self.text = text
        return self.text

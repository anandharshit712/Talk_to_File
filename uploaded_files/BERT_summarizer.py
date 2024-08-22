from summarizer import Summarizer,TransformerSummarizer

def read_text_file(file_path):
    with open(file_path, 'r', encoding = 'utf-8') as file:
        return file.read()

def summarizer(text):
    bert_model = Summarizer()
    bert_summerary = ''.join(bert_model(text))
    return bert_summary

text = read_text_file("Transcript.txt")
summary = summarizer(text)
print(summary)
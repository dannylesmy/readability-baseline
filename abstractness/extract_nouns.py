import pandas as pd
from nltk.corpus import wordnet as wn
from joblib import Parallel, delayed
import spacy 
nlp = spacy.load("en_core_web_md", disable=["tok2vec", "parser", "attribute_ruler", "lemmatizer","ner"])
# https://prrao87.github.io/blog/spacy/nlp/performance/2020/05/02/spacy-multiprocess.html

def remove_short(txt):
    return " ".join(word for word in txt.split() if len(word)>1)

def pos_tag(doc):
    pos_list = [token.text for token in doc if token.pos_=="NOUN"]
    return pos_list

def chunker(iterable, total_length, chunksize):
    return (iterable[pos: pos + chunksize] for pos in range(0, total_length, chunksize))

def flatten(list_of_lists):
    "Flatten a list of lists to a combined list"
    return [item for sublist in list_of_lists for item in sublist]

def process_chunk(texts):
    preproc_pipe = []
    for Doc in nlp.pipe(texts, batch_size=20):
        preproc_pipe.append(pos_tag(Doc))
    return preproc_pipe

def preprocess_parallel(texts, chunksize=100):
    executor = Parallel(n_jobs=7, backend='multiprocessing', prefer="processes")
    do = delayed(process_chunk)
    tasks = (do(chunk) for chunk in chunker(texts, len(df), chunksize=chunksize))
    result = executor(tasks)
    return flatten(result)




if __name__ == '__main__':  
	df = pd.read_feather(r"C:\Users\danny\OneDrive\Desktop\SERVER\lemmatize_item7_from_2002.feather")
	df["lemma"] = df.lemma.apply(lambda x: remove_short(x))
	df["nouns"] = preprocess_parallel(df['lemma'], chunksize=500)
	df.to_feather("item7_lemma_nouns.feather")


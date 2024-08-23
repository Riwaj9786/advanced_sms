# from joblib import Parallel, delayed
import os
import PyPDF2
import docx2txt
# from collections import defaultdict
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
import re
from difflib import SequenceMatcher 

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''.join([page.extract_text() for page in reader.pages])
    return text

def read_docx(file_path):
    return docx2txt.process(file_path)

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_file(file_path):
    print("Reading file ", file_path)
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return read_pdf(file_path)
    elif ext == '.docx':
        return read_docx(file_path)
    elif ext == '.txt':
        return read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def preprocess_text(text):
   
    pattern = re.compile(r'[^a-zA-Z\s]')
    text = pattern.sub('', text).lower()
    return text

def split_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]



def check_plagiarism(file1, file2):
    score = SequenceMatcher(None, file1, file2).ratio() 
    return int(score*100) 


# def calculate_plagiarism_score(texts):
#     vectorizer = TfidfVectorizer().fit_transform(texts)  
#     cosine_matrix = cosine_similarity(vectorizer)  
#     return cosine_matrix

# def check_plagiarism(folder_path, threshold=60.0):
#     files = [f for f in os.listdir(folder_path) if f.endswith(('.pdf', '.docx', '.txt'))]
    
    
#     file_texts = Parallel(n_jobs=-1)(delayed(preprocess_text)(read_file(os.path.join(folder_path, file))) for file in files)
    
#     file_sentences = {file: split_sentences(text) for file, text in zip(files, file_texts)}
#     combined_texts = {file: ' '.join(sentences) for file, sentences in file_sentences.items()}
    
#     plagiarism_scores = calculate_plagiarism_score(list(combined_texts.values()))
    
#     plagiarism_dict = defaultdict(list)
    
#     for i in range(len(files)):
#         for j in range(i + 1, len(files)):
#             score = plagiarism_scores[i, j] * 100  
#             if score > threshold:
#                 plagiarism_dict[files[i]].append((files[j], round(score, 2)))
#                 plagiarism_dict[files[j]].append((files[i], round(score, 2)))
    
#     return dict(plagiarism_dict)

# folder_path = 'Assignment'
# plagiarism_results = check_plagiarism(folder_path)
# print(plagiarism_results)
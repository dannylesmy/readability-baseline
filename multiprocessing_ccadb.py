from zipfile import ZipFile
import glob
import pandas as pd
import csv
from pathlib import Path
from readabilityDanny import Readability
import re
import os
import shutil
import time
from datetime import datetime
import multiprocessing as mp
import pytesseract
from pdf2image import convert_from_path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
poppler_path = r"C:\Program Files\poppler-0.68.0\bin"
# https://catalog.data.gov/dataset/credit-card-agreements-database 
# download all credit cards agreement from the data gov website

def unzip_file(path): # unzip all files and remove the zipped files 
    files = glob.glob(path+"/*.zip")
    for file in files:
        shutil.unpack_archive(file, re.search(r"\d{4}.*?\.",file).group())
        os.remove(file)
        
def create_list(path): # extract all files into one folder
    allfiles = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            allfiles.append(os.path.join(subdir, file))
    allfiles = [file for file in allfiles if file.endswith("pdf")]
    return allfiles
     
def extract_txt(file): # conver each pdf to image to capture the whitespaces and extract text from the ocr image.
    year = int(re.search(r"\d{4}", file).group(0))
    try:
        images = convert_from_path(file,poppler_path=poppler_path)
        ocr_text = ''
        for i in range(len(images)):        
            page_content = pytesseract.image_to_string(images[i])
            page_content = '***PDF Page {}***\n'.format(i+1) + page_content
            ocr_text = ocr_text + ' ' + page_content
        readability = Readability(ocr_text)
        return year, readability.gunning_fog().score
    except: pass
 
if __name__ == '__main__':  
    print(datetime.now().time())
    rootdir = r"D:\Danny\Baseline\Credit Card Agreements"
    #unzip = unzip_file(rootdir)
    pool = mp.Pool(processes=33)
    files = create_list(rootdir)
    results = [pool.apply_async(extract_txt, [f]) for f in files]
    output = [p.get() for p in results]
    pool.close()
    pool.join()
    print(datetime.now().time())   
    df = pd.DataFrame(output, columns=['year', 'fog'])
    df.to_csv("CCADB_FOG.csv", index=False)
    print (df.shape)
    
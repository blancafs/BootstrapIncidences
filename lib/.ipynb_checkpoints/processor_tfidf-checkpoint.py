from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
# Custom import

from .configurator import MODEL_FOLDER_PATH,CATEGORY_COLUMN_NAME,TEXT_COLUMN_NAME,VECTOR_COLUMN_NAME,VECTOR_DATABASE_NAME

class ProcessorTFIDF:
    
    def __init__(self, path_to_csv):
        self.path_to_csv = path_to_csv
        self.df = pd.read_csv(path_to_csv, engine='python')
    
    # Processes text column into tfidf vectors
    def initialize(self, text_col='texto_sap', y_col=CATEGORY_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME, drop_cols=[], test_ratio=0.2, random_state=0, vectors_available=False):
        
        # Check Target Column
        if y_col not in self.df.columns:
            print('Please give a valid target column name (y_col=)')
            print('Returning Null...')
            return None
        
        # Get text list and clean it
        df = self.df
        texts = df[text_col].apply(lambda x: self.clean_text(str(x)))

        # Vectorize the cleaned texts and add them to the df
        self.vectoriser = TfidfVectorizer()
        vec_txts = self.vectoriser.fit_transform(texts)
        
        self.df[vec_col] = list(vec_txts.toarray())
        
        # Splitting
        X = self.df.drop(columns=drop_cols, axis=1)
        X = X.drop(columns=[y_col], axis=1)
        y = self.df[y_col]
        X_train, X_valid, y_train, y_valid = train_test_split(X, y, random_state=random_state, test_size=test_ratio)

        # Save the train/test datasets as private fields
        self.df_train = X_train.copy()
        self.df_train[y_col] = y_train
        self.df_test = X_valid.copy()
        self.df_test[y_col] = y_valid
    
    ## Process and return new datapoints for classifying
    def processFrame(self, data_frame, text_col=TEXT_COLUMN_NAME, drop_Cols=[]):
        # Clean text
        texts = data_frame[text_col].apply(lambda x: self.clean_text(str(x)))
        
        # Vectorise the cleaned texts and add them to the returned df
        results - self.vectoriser.transform(texts)
        df_return = data_frame.copy()
        df_return[VECTOR_COLUMN_NAME] = list(results)
        
        return df_return
    
    # Retrieves private training field
    def getTrainingSet(self):
        return self.df_train.copy()
   
    # Retrieves private testing field
    def getTestingSet(self):
        return self.df_test.copy()
    
    # Retrieves vectoriser
    def getTfidfVectoriser(self):
        return self.vectoriser.copy()
            
    # Method to clean text
    def clean_text(self, text):
        # Define regex
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        BAD_SYMBOLS_RE = re.compile('[.]')
        # Convert input text
        text = text.lower() # lowercase text
        text = REPLACE_BY_SPACE_RE.sub(' ', text)
        text = BAD_SYMBOLS_RE.sub('', text)
        final = ''
        for t in text.split():
            if any(char.isdigit() for char in t)<=0:
                final += t + ' '
        return final            
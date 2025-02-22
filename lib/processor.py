# Native imports
import os
import pandas as pd
import numpy as np
import re

# Third party imports
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow_hub as hub
import tf_sentencepiece

# Custom imports
from .debug import Debug
from .configurator import Utils, MODEL_FOLDER_PATH,CATEGORY_COLUMN_NAME,TEXT_COLUMN_NAME,VECTOR_COLUMN_NAME,VECTOR_DATABASE_NAME


####################################################################################################
### Processor Class used to embed texts and get data ready #########################################
####################################################################################################
class Processor(Debug):
    """"
    The processor class is used to embed the texts using the google multilingual embedder and get the text ready
    for the classification algorithm.

    Args:
        Debug: The abstract super class Debug includes a debug log method which is inherited by all classes in the system to make debugging efficient.
    """
    ## Constructor
    def __init__(self, path_to_csv, model_url=MODEL_FOLDER_PATH):
        """
        The constructor method needs the path to the csv file/database and the path to the pre-trained model.

        Args:
            path_to_csv: The local path to the database
            model_url: Path to the pre-trained model
        """
        self.path_to_csv = path_to_csv
        self.df = pd.read_csv(path_to_csv)
        self.model_url = model_url


    ## Initializes model and embeds training set if necessary
    def initialize(self, y_col=CATEGORY_COLUMN_NAME, text_col=TEXT_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME, drop_cols=[], test_ratio=0.2, random_state=0, vectors_available=False):
        """
        Initializes model and embeds the training set if necessary, aka if model hasn't been downloaded before.

        Args:
            y_col: The name of the column with categories
            text_col: The name of the column holding the text complaints
            vec_col: The name of the column holding the vectorized texts
            drop_cols: The names of any columns we wish to drop from the database
            test_ratio: The ratio of train to test data
            random_state: The seed for the randomization algorithm, keep the same to recreate fair trials
            vectors_available: Set to True if the vectorized database already exists to avoid re-creating the vectorizations

        Returns:
            Sets the self variables of text_input, embedded_text, session, df, train and test sets.
        """

        # Check Target Column
        if y_col not in self.df.columns:
            self.inform('Please give a valid target column name (y_col=)')
            self.inform('Returning Null...')
            return None

        # Set up module and initialiize session
        module_url = self.model_url
        g = tf.Graph()
        with g.as_default():
            self.text_input = tf.placeholder(dtype=tf.string, shape=[None])
            multiling_embed = hub.Module(module_url)
            self.embedded_text = multiling_embed(self.text_input)
            init_op = tf.group([tf.global_variables_initializer(), tf.tables_initializer()])
        g.finalize()
        session = tf.Session(graph=g)
        session.run(init_op)
        self.session = session

        # If the vectors are not available, clean the text and embed them
        if not vectors_available:
            # Get text list and clean it
            df = self.df
            texts = df[text_col].apply(lambda x: self.clean_text(str(x)))

            # Vectorize the cleaned texts and add them to the df
            results = session.run(self.embedded_text, feed_dict={self.text_input: texts})
            self.df[vec_col] = list(results)

            # Save the new vector csv
            path_to_vector_list = self.path_to_csv.split('/')[:-1]
            path_to_vector = '/'.join(path_to_vector_list)
            path_to_vector = path_to_vector + '/' + VECTOR_DATABASE_NAME
            Utils.saveCSV(df, path_to_vector)

        # If the vectors were available and read, then parse them from string into list of floats
        else:
            self.df[vec_col] = self.df[vec_col].apply(lambda x : self.readVector(x))


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


    ## Process the texts and return new dataframe with the vectors column for classifying
    def processFrame(self, data_frame, text_col=TEXT_COLUMN_NAME, drop_cols=[]):
        """
        If vectors are not available, this method is called to process the texts and return a dataframe with a new vectors column for classifying.

        Args:
            data_frame: The name of the column with categories
            text_col: The name of the column holding the text complaints
            drop_cols: The names of any columns we wish to drop from the database
        Returns:
            df: The cleaned dataframe with the vectors column
        """
        # Clean text
        texts = data_frame[text_col].apply(lambda x: self.clean_text(str(x)))

        # Vectorize the cleaned texts and add them to the return df
        results = self.session.run(self.embedded_text, feed_dict={self.text_input: texts})
        df_return = data_frame.copy()
        df_return[VECTOR_COLUMN_NAME] = list(results)

        return df_return


    ## Reads in string of vectors and returns array of floats
    def readVector(self, text_vector):
        """
        Reads a string of vectors, as the model returns them, and returns an array of floats.

        Args:
            text_vector: The string to read
        Returns:
            vec: An array of floats
        """
        text = text_vector.replace('\n','') # Remove \n
        text = text.replace('[','')
        text = text.replace(']','')

        vec = [float(x) for x in text.split(' ') if x]

        return np.array(vec)


    ## Retrieve private training field
    def getTrainingSet(self):
        return self.df_train.copy()

    ## Retrieve private testing field
    def getTestingSet(self):
        return self.df_test.copy()


    ## Method to clean text
    def clean_text(self, text):
        """
        Method used to clean the basic text of commas, punctuation, capital letters and other unwanted symbols.

        Args:
            text: The individual text paragraph to process
        Returns:
            text: The same text but cleaned
        """
        # Define regex
        REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        BAD_SYMBOLS_RE = re.compile('[.]')
        # Convert input text
        text = text.lower() # lowercase text
        text = REPLACE_BY_SPACE_RE.sub(' ', text)
        text = BAD_SYMBOLS_RE.sub('', text)
        return text

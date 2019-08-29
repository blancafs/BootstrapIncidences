# import env variables
import pandas as pd
import numpy as np

# Processing imports
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler

# Model imports
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB as NB
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

# Custom imports
from .configurator import ConfigGetter, CATEGORY_COLUMN_NAME, VECTOR_COLUMN_NAME


####################################################################################################
#### Classifier class used to classify categories of saps ##########################################
####################################################################################################
class Classifier:
    """
    Class used to classify the category and sub-category of a given SAP text.
    """

    ### CONSTRUCTOR ###
    def __init__(self, training_df, y_col=CATEGORY_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME, params={}):
        """
        Establishes the training dataframe, the goal column, and any params necessary
        :param training_df: the dataframe containing all the datapoints that will help train the classifier
        :param y_col: the name of the column the classifier wants to predict, from the training dataframe
        :param vec_col: the name of the vector column in the training dataframe
        :param params: any necessary params, depending on what classifier is wanted
        """
        self.train_df = training_df
        self.vec_col = vec_col
        self.y_col = y_col
        self.params = params


    ## Abstract class to classify input dataframe
    def classify(self, test_df):
        pass


    ## Classifies input dataframe given model and sets
    def giveClassification(self, test_df, model):
        """
        'Classifies input dataframe given the current model.'
        :param test_df:
        :param model:
        :return:
        """
        # Get training set
        X_train, y_train = self.getSplittedVectorsFrame(self.train_df)
        # Preprocess dataframe input
        X_test = self.getSplittedVectorsFrame(test_df, for_training=False)

        # Fit model and make predictions
        model.fit(X_train, y_train)
        categories = model.predict(X_test)

        # Make a new dataframe with the results and return it
        classified_df = test_df.copy()
        classified_df[self.y_col] = categories
        return classified_df


    ### FUNCTIONAL HELPER METHODS ###

    ## Returns accuracy for predictions input
    def getAccuracy(self, predictions_df, actual_df):
        wrong = predictions_df[predictions_df[self.y_col]!=actual_df[self.y_col]].shape[0]
        acc = (1 - (wrong / predictions_df.shape[0])) * 100
        return str(round(acc,2))+'% Accuracy'


    ## Builds X_train, y_train sets for ML models
    def getSplittedVectorsFrame(self, df, for_training=True):
        # Create an X_train dataframe with the right dimensions
        vector_dim = list(df[self.vec_col])[0].shape[0]
        X_train = pd.DataFrame(columns=['dim '+str(x) for x in range(vector_dim)])

        # Populate the dataframe with the text vectors as rows
        for i in range(df.shape[0]):
            X_train.loc[X_train.shape[0]] = df.iloc[i][self.vec_col].tolist()

        # If needed for training, return the y column as y_train
        if for_training:
            y_train = df[self.y_col]
            return X_train, y_train
        else:
            return X_train



####################################################################################################
#### Classifier sublasses ##########################################################################
####################################################################################################

## Classifies with SVM
class ClassifierSVM(Classifier):
    def classify(self, test_df):
        return self.giveClassification(test_df, SVC(**self.params))

## Classifies with Logistic Regression
class ClassifierLogistic(Classifier):
    def classify(self, test_df):
        return self.giveClassification(test_df, LogisticRegression(**self.params))

## Classifies with GaussianNB
class ClassifierGaussian(Classifier):
    def classify(self, test_df):
        return self.giveClassification(test_df, GaussianNB())


## Classifies with XGBoost
class ClassifierXGBoost(Classifier):
    # Override giveClassification
    def giveClassification(self, test_df, model):
        # Get sets
        X_train, y_train = self.getSplittedVectorsFrame(self.train_df)
        X_test = self.getSplittedVectorsFrame(test_df, for_training=False)

        # Fit model and make predictions 
        model.fit(X_train, y_train, verbose=False)
        categories = model.predict(X_test)

        # Make a new dataframe with the results and return it
        classified_df = test_df.copy()
        classified_df[self.y_col] = categories
        return classified_df

    def classify(self, test_df):
        return self.giveClassification(test_df, XGBClassifier(**self.params))



####################################################################################################
#### Classifier Builder ############################################################################
####################################################################################################

class ClassifierBuilder:
    ## This class returns a classifier object depending on the configuration file
    def getClassifier(training_df, y_col=CATEGORY_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME):
        # Get the model name and parameters from config file
        configGetter = ConfigGetter()
        model_name = configGetter.getModelName()
        param_dict = configGetter.getParamDict()

        # Return the right class depending on the config file
        if model_name=='SVM':
            return ClassifierSVM(training_df, y_col=y_col, vec_col=vec_col, params=param_dict)
        elif model_name=='Logistic':
            return ClassifierLogistic(training_df, y_col=y_col, vec_col=vec_col, params=param_dict)
        elif model_name=='Gaussian':
            return ClassifierGaussian(training_df, y_col=y_col, vec_col=vec_col, params=param_dict)
        elif model_name=='XGBoost':
            return ClassifierXGBoost(training_df, y_col=y_col, vec_col=vec_col, params=param_dict)
        else:
            print('No valid model was found in config.txt, returning None')
            return None

        

####################################################################################################
#### Class that returns object based on string #####################################################
#### NOT USED IN THIS VERSION                  #####################################################
####################################################################################################
class ClassifierFactory:
    
    def __init__(self, model_name, training_df, y_col, vec_col, param_dict):
        classifier_dict = {'SVM' : ClassifierSVM,\
                           'Logistic' : ClassifierLogistic,\
                           'Gaussian' : ClassifierGaussian,\
                           'XGBoost' : ClassifierXGBoost}
        classifier = classifier_dict[model_name]()
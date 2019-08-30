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

    Abstract class used to classify the category and sub-category of a given SAP text.

    The constructor method establishes the training dataframe, the goal column, and any params necessary.

    Args:
      training_df: the dataframe containing all the datapoints that will help train the classifier
      y_col: the name of the column the classifier wants to predict, from the training dataframe
      vec_col: the name of the vector column in the training dataframe
      params: any necessary params, depending on what classifier is wanted

    """

    ### CONSTRUCTOR ###
    def __init__(self, training_df, y_col=CATEGORY_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME, params={}):

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
        Classifies input dataframe given the input model. As it is an abstract class, depending on the model a different subclass will be used to classify the dataframe.

        Args:
          test_df: the dataframe containing the dataframe to classify
          model: the model to be used for the classification

        Returns:
          The new classified dataframe
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
    """
    The following are functional helper methods that were used to test the model's accuracies at predicting categories.
    """

    ## Returns accuracy for predictions input
    def getAccuracy(self, predictions_df, actual_df):
        """
        Returns accuracy of predictions vs the real categories. This method was used in the testing period.

        Args:
          predictions_df: the dataframe with the datapoints and their predicted categories
          actual_df: the real categories for the datapoints

        Returns:
          The accuracy of the current model with the given dataframe.
        """
        wrong = predictions_df[predictions_df[self.y_col]!=actual_df[self.y_col]].shape[0]
        acc = (1 - (wrong / predictions_df.shape[0])) * 100
        return str(round(acc,2))+'% Accuracy'


    ## Builds X_train, y_train sets for ML models
    def getSplittedVectorsFrame(self, df, for_training=True):
        """
        This method builds the Xtrain and ytrain sets for the ML models by splitting the given dataframe. This method is more useful than the typical
        train test split python function as it takes into account the size of the vector encodings for each datapoint.

        Args:
          df: the dataframe with datapoints to be split up
          for_training: if for training the category column will be added to the returned dataframe, if its for testing it won't

        Returns:
          The split training sets for training our model.
        """
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
    """
    Creates SVM classifier. This was for the testing period and was not used in the final website.

    Has one method to classify a given test dataframe, using the params set by the super class, and returns the classified dataframe.
    """
    def classify(self, test_df):
        return self.giveClassification(test_df, SVC(**self.params))

## Classifies with Logistic Regression
class ClassifierLogistic(Classifier):
    """
    Creates Logistic Regression classifier. This was for the testing period and was not used in the final website.

    Has one method to classify a given test dataframe, using the params set by the super class, and returns the classified dataframe.
    """
    def classify(self, test_df):
        return self.giveClassification(test_df, LogisticRegression(**self.params))

## Classifies with GaussianNB
class ClassifierGaussian(Classifier):
    """
    Creates Gaussian Naive Bayes classifier. This was for the testing period and was not used in the final website.

    Has one method to classify a given test dataframe, using the params set by the super class, and returns the classified dataframe.
    """
    def classify(self, test_df):
        return self.giveClassification(test_df, GaussianNB())


## Classifies with XGBoost
class ClassifierXGBoost(Classifier):
    """
    Creates XGBoost classifier. This is the final model that was used.

    Has one method to classify a given test dataframe, using the params set by the super class, and returns the classified dataframe.
    """
    # Override giveClassification
    def giveClassification(self, test_df, model):
        """
        This method overrides the giveClassification method in the super class.

        Args:
          test_df: dataframe to classify, given without the category column
          model: the model to use, in this case the XGboost

        Returns:
          The classified dataframe.
        """
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
    """
    Returns the correct classifier depending on the values given by the pre-made configuration class/file (check Configuration class)
    """
    ## This class returns a classifier object depending on the configuration file
    def getClassifier(training_df, y_col=CATEGORY_COLUMN_NAME, vec_col=VECTOR_COLUMN_NAME):
        """
        Given the column that is to be predicted and the column holding the vector encodings, it will return the wanted classifier object with all its parameters done.

        Args:
           y_col: the name of the column to predict, set in configuration
           vec_col: the name of the column holding the vector encodings, set in configuration

        Returns:
          The new classifier with the y col, vec_col, and parameters set.
        """
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
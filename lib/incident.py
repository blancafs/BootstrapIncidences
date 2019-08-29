## Native imports
import os
import pandas as pd
import numpy as np

# Custom imports
from .processor import Processor
from .classifier import ClassifierBuilder
from .configurator import DATABASE_PATH, INDEX_COLUMN_NAME, CODIGO_COLUMN_NAME, MATERIAL_COLUMN_NAME,\
    ANALYSIS_COLUMN_NAME, CAUSA_COLUMN_NAME, CATEGORY_COLUMN_NAME, SUB_CATEGORY_COLUMN_NAME,\
    TEXT_COLUMN_NAME, TEXT_DATABASE_NAME, VECTOR_DATABASE_NAME
from flask import request


####################################################################################################
### Incidents Class used to wrap functionality of other classes ####################################
### -> Classifies category and sub-category                     ####################################
####################################################################################################
class IncidentWrapper:
    """
    Incidents Class used to wrap functionality of other classes. Adds the classification of category and sub-category.
    """
    ## Constructor
    def __init__(self, path_to_database=DATABASE_PATH, DEBUG=False):
        self.DEBUG = DEBUG
        self.data_folder = path_to_database
        self.data_processor = self.getProcessor()


    ## Returns predicted incident entry
    def getPredictedIncidentEntry(self, incident_df):
        """"
        Given incidence dataframe, returns the processed incidence along with its predicted category and sub category.
        :parameter: incident_df
        """

        # Get dataframe of incident and vectorize it
        processed_incident_df = self.processIncident(incident_df)
        self.inform('[getPredictedIncidentEntry]: Incident was parsed and preprocessed successfully.')

        # Predict the category of the processed incident
        predicted_category = self.predictCategory(processed_incident_df)
        self.inform('[getPredictedIncidentEntry]: Predicted category is ' + predicted_category)

        # Based on the predicted category, predict sub-category
        predicted_sub_category = self.predictSubCategory(processed_incident_df, predicted_category)
        self.inform('[getPredictedIncidentEntry]: Predicted sub-category is ' + predicted_sub_category)

        # Add the category and subcategory to the dataframe
        processed_incident_df[CATEGORY_COLUMN_NAME] = [predicted_category]
        processed_incident_df[SUB_CATEGORY_COLUMN_NAME] = [predicted_sub_category]
        return processed_incident_df


    ## Parses excel file and returns dataframe with useful data
    def parseIncidentFromFile(self, path_to_file):
        """
        Given a path to a file, will parse it obtaining the wanted sections and return a panda dataframe for that data file
        :param path_to_file:
        :return:
        """
        _, _, df = IncidentParser().parseFiles([path_to_file])
        return df


    ## Parses the form
    def parseIncidentFromWebForm(self, form):
        df = IncidentParser().parseWebForm(form)
        return df


    ## Returns given df with columns necessary for training
    def keepTrainingCols(self, entry_df):
        return entry_df[[INDEX_COLUMN_NAME, TEXT_COLUMN_NAME, CATEGORY_COLUMN_NAME, SUB_CATEGORY_COLUMN_NAME]].copy()


    ##Returns given df with columns necessary for general database
    def keepGeneralCols(self, entry_df):
        return entry_df[[INDEX_COLUMN_NAME, CODIGO_COLUMN_NAME, MATERIAL_COLUMN_NAME, TEXT_COLUMN_NAME,\
                         ANALYSIS_COLUMN_NAME, CAUSA_COLUMN_NAME, CATEGORY_COLUMN_NAME, SUB_CATEGORY_COLUMN_NAME]].copy()


    ### FUNCTIONAL HELPER METHODS ###

    ## Returns the best possible initialized Processor object
    def getProcessor(self):
        available_databases = os.listdir(self.data_folder)

        # Check if pre-calculated vectors are available
        if VECTOR_DATABASE_NAME in available_databases:
            processor = Processor(self.data_folder + VECTOR_DATABASE_NAME)
            processor.initialize(test_ratio=0.00000000001, vectors_available=True)
            self.inform('Vector database was found and loaded.')
        elif TEXT_DATABASE_NAME in available_databases:
            processor = Processor(self.data_folder + TEXT_DATABASE_NAME)
            self.inform('Vector database was not found. Text database was loaded instead. Making embeddings now...')
            processor.initialize(test_ratio=0.00000000001, vectors_available=False)
            self.inform('Vectors were made and loaded.')
        else:
            self.inform('The following files were searched: ' + str(available_databases))
            self.inform('No valid database was found. Aborting process.')
            return None

        return processor

    ## Vectorizes the incident entry
    def processIncident(self, incident_df):
        return self.data_processor.processFrame(incident_df)

    ## Predicts category of processed incident
    def predictCategory(self, processed_incident_df):
        classifier_category = ClassifierBuilder.getClassifier(self.data_processor.getTrainingSet())
        categorized_df = classifier_category.classify(processed_incident_df)
        return categorized_df[CATEGORY_COLUMN_NAME][0]

    ## Predicts sub-category
    def predictSubCategory(self, processed_incident_df, predicted_category):
        training_set = self.data_processor.getTrainingSet()
        training_set = training_set[training_set[CATEGORY_COLUMN_NAME] == predicted_category]
        classifier_subcategory = ClassifierBuilder.getClassifier(training_set, y_col=SUB_CATEGORY_COLUMN_NAME)
        sub_categorized_df = classifier_subcategory.classify(processed_incident_df)
        return sub_categorized_df[SUB_CATEGORY_COLUMN_NAME][0]

    ## DEBUG message method
    def inform(self, *text):
        if self.DEBUG:
            print('[DEBUG]: inform():', *text)


####################################################################################################
### Incidents Parser class used to parse excel files ###############################################
####################################################################################################
class IncidentParser:

    ## Returns df from parsed form
    def parseWebForm(self, form):
        aviso_calidad = request.values.get("aviso_calidad")
        codigo_cliente = request.values.get("codigo_cliente")
        material_afectado = request.values.get("material_afectado")
        textoSAP = request.values.get("textoSAP")
        analysis_causa = request.values.get("analysis_causa")
        causa_raiz = request.values.get("causa_raiz")

        # Making entry with all parameters into dataframe
        entry = [aviso_calidad, codigo_cliente, material_afectado, textoSAP, analysis_causa, causa_raiz]
        column_names = ['aviso_de_calidad', 'codigo_cliente', 'material', 'texto_sap', 'analysis_de_causas', 'causa_raiz']
        df = pd.DataFrame(columns=column_names)
        df.rename(columns={"aviso_de_calidad": INDEX_COLUMN_NAME}, inplace=True)
        df.loc[0] = entry
        return df

    ## Returns dataframe with the parsed data of the given file list
    def parseFiles(self, list_of_files):
        names = ['aviso_de_calidad', 'codigo_cliente', 'material', 'texto_sap', 'analysis_de_causas', 'causa_raiz']
        docs = []
        entries = []
        for name in list_of_files:
            d = pd.read_excel(name, header=None)
            for elem in names:
                e = self.getInfo(elem, d)
                entries.append(e)
            df = pd.DataFrame(columns=names)
            df.loc[0] = list(entries)
            # filename = name.split('/')[-1]
            # df['filename'] = filename
            docs.append(df)
        THE_DATAFRAME = pd.concat(docs).reset_index(drop=True)
        THE_DATAFRAME.rename(columns={"aviso_de_calidad": INDEX_COLUMN_NAME}, inplace=True)
        return docs, entries, THE_DATAFRAME

    ## Input string with name of field desired to find methods to use
    def lookUp(self, string):
        methods = {}
        methods.update({'aviso_de_calidad': ('R', 0, 'Aviso de calidad', None)})
        methods.update({'codigo_cliente': ('R', 0, 'Cód cliente', None)})
        methods.update({'clientes': ('B', 1, 'Clientes', 'Responsable')})
        methods.update({'material': ('R', 1, 'Material', None)})
        methods.update({'lote': ('B', 1, 'Lote', 'Texto SAP')})
        methods.update({'texto_sap': ('B', 0, 'Texto SAP', None)})
        methods.update({'investigacion': ('B', 1, 'Investigación', 'Imputable CIP')})
        methods.update({'imputable_cip': ('R', 0, 'Imputable CIP', None)})
        methods.update({'analysis_de_causas': ('B', 1, 'Análisis de causas', 'Acciones')})
        methods.update({'acciones': ('B', 1, 'Acciones', 'Fecha finalización')})

        # If not in dictionary, it means the field is not in the original excels and we return 0
        if string in list(methods.keys()):
            return methods.get(string)
        else:
            return 0,0,0,0

    ## Returns x and y coordinates of first encounter of string entered or -1,-1 if it doesn't!
    # REMEMBER TO SEARCH FOR MATERIAL WITH CAPITAL M or wont find it
    def find(self, string, df):
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                cell = df.iloc[i, j]
                if string in str(cell):
                    return (i, j)
                else:
                    pass
        return (-1, -1)

    ## GET ENTRY FOR STRING GIVEN WITHIN DATAFRAME - LOOKS UP METHOD AND FINDS IT
    def getInfo(self, string, df):
        u, h, s, n = self.lookUp(string)
        # If lookup method returned all 0s, field is not in excel and gets value -1
        if u==0 and h==0 and s==0 and n==0:
            return -1
        i, j = self.find(s, df)
        if h == 0:
            if u == 'R':
                element = (df[df.columns[j + 1]].iloc[i])
            else:
                element = (df[df.columns[j]].iloc[i + 1])
            return element
        if h == 1:
            if u == 'R':
                elements = []
                vals = list(((df.iloc[i])[j + 1:]).dropna())
                if len(vals) < 1:
                    vals = np.nan
            else:
                ni, nj = self.find(n, df)
                vals = list(((df.iloc[i + 1:ni, j]).dropna()))
                if len(vals) < 1:
                    vals = np.nan
            return vals

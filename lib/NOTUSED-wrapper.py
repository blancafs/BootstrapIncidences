## Native imports
import os
import pandas as pd
import numpy as np

# Custom imports
from processor import Processor
from classifier import ClassifierBuilder
from configurator import CATEGORY_COLUMN_NAME,SUB_CATEGORY_COLUMN_NAME,TEXT_COLUMN_NAME,VECTOR_COLUMN_NAME,TEXT_DATABASE_NAME,VECTOR_DATABASE_NAME

####################################################################################################
### Incidents Class used to wrap functionality of other classes ####################################
### -> Takes excel incident as an input                         ####################################
### -> Classifies category and sub-category                     ####################################
####################################################################################################

class IncidentWrapper:
    ## Constructor
    def __init__(self, path_to_database, DEBUG=False):
        self.DEBUG = DEBUG
        self.data_folder = path_to_database
        self.data_processor = self.getProcessor()
    
    
    ## Returns category and sub-category of input incident file
    def categorizeFile(self, path_to_file):
        # Get dataframe of incident and vectorize it
        incident_df = self.parseIncident(path_to_file)
        processed_incident_df = self.data_processor.processFrame(incident_df)
        self.inform('[categorizeFile]: Incident was parsed and preprocessed successfully.')
        
        # Predict the category of the processed incident
        classifier_category = ClassifierBuilder.getClassifier(self.data_processor.getTrainingSet())
        categorized_df = classifier_category.classify(processed_incident_df)
        predicted_category = categorized_df[CATEGORY_COLUMN_NAME][0]
        self.inform('[categorizeFile]: Predicted category is '+predicted_category)
        
        # Based on the predicted category, predict sub-category
        training_set = self.data_processor.getTrainingSet()
        training_set = training_set[training_set[CATEGORY_COLUMN_NAME]==predicted_category]
        classifier_subcategory = ClassifierBuilder.getClassifier(training_set, y_col=SUB_CATEGORY_COLUMN_NAME)
        sub_categorized_df = classifier_subcategory.classify(processed_incident_df)
        predicted_sub_category = sub_categorized_df[SUB_CATEGORY_COLUMN_NAME][0]
        self.inform('[categorizeFile]: Predicted sub-category is '+predicted_sub_category)
        
        return predicted_category, predicted_sub_category
    
    
    ## Parses excel file and returns dataframe with useful data
    def parseIncident(self, path_to_file):
        _,_,df = self.parseFiles([path_to_file])
        return df
    
    
    
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
            self.inform('The following files were searched: '+str(available_databases))
            self.inform('No valid database was found. Aborting process.')
            return None
        
        return processor
    
    
    ## Input string with name of field desired to find methods to use
    def lookUp(self, string):
        methods = {}
        methods.update({'aviso_de_calidad': ('R', 0, 'Aviso de calidad', None)})
        methods.update({'codigo_cliente': ('R', 0, 'Cód cliente', None)})
        methods.update({'clientes': ('B',1,'Clientes','Responsable')})
        methods.update({'material': ('R', 1, 'Material', None)})
        methods.update({'lote': ('B', 1, 'Lote', 'Texto SAP')})
        methods.update({'texto_sap': ('B', 0, 'Texto SAP', None)})
        methods.update({'investigacion': ('B', 1, 'Investigación', 'Imputable CIP')})
        methods.update({'imputable_cip': ('R', 0, 'Imputable CIP', None)})
        methods.update({'analysis_de_causas': ('B', 1, 'Análisis de causas','Acciones')})
        methods.update({'acciones': ('B', 1, 'Acciones','Fecha finalización')})
        return methods.get(string)

    ## Returns x and y coordinates of first encounter of string entered or -1,-1 if it doesn't!
    # REMEMBER TO SEARCH FOR MATERIAL WITH CAPITAL M or wont find it
    def find(self, string, df):
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                cell = df.iloc[i,j]
                if string in str(cell):
                    return (i,j)
                else:
                    pass
        return (-1,-1)

    ## GET ENTRY FOR STRING GIVEN WITHIN DATAFRAME - LOOKS UP METHOD AND FINDS IT
    def getInfo(self, string,df):
        u,h,s,n = self.lookUp(string)
        i,j = self.find(s,df)
        if h == 0:
            if u == 'R':
                element = (df[df.columns[j+1]].iloc[i])
            else:
                element = (df[df.columns[j]].iloc[i+1])
            return element
        if h == 1:
            if u == 'R':
                elements = []
                vals = list(((df.iloc[i])[j+1:]).dropna())
                if len(vals)<1:
                    vals = np.nan
            else:
                ni, nj = self.find(n, df)
                vals = list(((df.iloc[i+1:ni, j]).dropna()))
                if len(vals)<1:
                    vals = np.nan
            return vals

        
    ## Returns dataframe with the parsed data of the given file list
    def parseFiles(self, list_of_files):
        names = ['aviso_de_calidad','codigo_cliente', 'clientes', 'material', 'lote', 'texto_sap', 'investigacion', 'imputable_cip', 'analysis_de_causas', 'acciones']
        docs = []
        for name in list_of_files:
            d = pd.read_excel(name, header=None)
            entries = []
            for elem in names:
                e = self.getInfo(elem, d)
                entries.append(e)
            df = pd.DataFrame(columns=names)
            df.loc[0] = list(entries)
            filename = name.split('/')[-1]
            df['filename'] = filename
            docs.append(df)
        THE_DATAFRAME = pd.concat(docs).reset_index(drop=True)

        return docs, entries, THE_DATAFRAME
    
    
    ## DEBUG message method
    def inform(self, text):
        if self.DEBUG:
            print(text)
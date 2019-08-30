import pandas as pd

from .debug import Debug
from .configurator import Utils, INDEX_COLUMN_NAME, CATEGORY_COLUMN_NAME, SUB_CATEGORY_COLUMN_NAME

"""
COPYRIGHT none
This module abstracts the updating and pulling from the
csv database files in the database folder
"""

class IncidentBase(Debug):
    def __init__(self, incident_wrapper, path_to_training, path_to_vectors, path_to_incidents):
        self.incidentWrapper = incident_wrapper
        self.path_to_training = path_to_training
        self.path_to_vectors = path_to_vectors
        self.path_to_incidents = path_to_incidents

    ## Updates the training databases (both vector and non-vector), by adding or replacing the given incident
    def updateTrainingData(self, df_entry):
        # Construct dataframe, get id and see if there are any previous entries for id
        train_df = pd.read_csv(self.path_to_training).reset_index(drop=True)
        vector_df = pd.read_csv(self.path_to_vectors).reset_index(drop=True)
        ind = self.getRelavantIndex(df_entry, train_df, log='[incidentBase]: updateTrainingData():')

        if ind == -1:
            return False
        else:
            # Replace the entry at the correct index
            train_df.loc[ind] = list(df_entry.loc[0])

            # Get the new entry as a one-row dataframe and process it for vectors
            df_to_process = train_df.loc[[ind]].copy()
            processed_df = self.incidentWrapper.processIncident(df_to_process).reset_index()
            processed_entry = processed_df.loc[0]

            # Replace the corresponding index of the vector database
            vector_df.loc[ind] = processed_entry

            # Save the new dfs back as csv files
            Utils.saveCSV(train_df, self.path_to_training)
            Utils.saveCSV(vector_df, self.path_to_vectors)
            return True


    ## Updates the incident database with the given incident, replacing or adding it at the end
    def updateIncidentData(self, df_entry):
        # Retrieve database and index
        incident_df = pd.read_csv(self.path_to_incidents).reset_index(drop=True)
        ind = self.getRelavantIndex(df_entry, incident_df, log='[incidentBase]: updateIncidentData():')

        # Replace the entry at the correct index and save it back to csv
        if ind == -1:
            return False
        else:
            incident_df.loc[ind] = list(df_entry.loc[0])
            Utils.saveCSV(incident_df, self.path_to_incidents)
            return True


    ## Returns the required entry from its id int(aviso_de_calidad) as a dataframe
    def getEntry(self, incidence_id):
        df = pd.read_csv(self.path_to_incidents).reset_index(drop=True)
        occurances = df[df[INDEX_COLUMN_NAME] == incidence_id].shape[0]
        # Find the right index for the entry
        if occurances == 0:
            self.inform('[incidentBase]: getEntry(): Found NO occurance of', incidence_id)
            ind = -1
        elif occurances == 1:
            self.inform('[incidentBase]: getEntry(): Found one occurance of' ,incidence_id)
            ind = df.loc[df[INDEX_COLUMN_NAME] == incidence_id].index[0]
        else:
            self.inform('[incidentBase]: getEntry(): Database has multiple occurances of id:', incidence_id)
            ind = -1

        # If no entry found return an empty df, otherwise return df with single entry
        if ind == -1:
            entry = df.loc[df[INDEX_COLUMN_NAME] == -1]
        else:
            entry = df.loc[[ind]]

        entry.reset_index(inplace=True, drop=True)
        return entry


    ## Changes the classification of the incident id
    def changeIncidentClass(self, id, category, sub_category):
            entry = self.getEntry(id)
            # Check its not empty
            if entry.shape[0] != 1:
                self.inform('[incidentBase]: changeIncidentClass(): No occurances of :',id,'found. Aborting the configuration')
            else:
                p_cat = entry.loc[0][CATEGORY_COLUMN_NAME]
                p_sub_cat = entry.loc[0][SUB_CATEGORY_COLUMN_NAME]
                self.inform('[incidentBase]: changeIncidentClass():',id,'category was:',p_cat,p_sub_cat)
                entry.loc[0, CATEGORY_COLUMN_NAME] = category
                entry.loc[0, SUB_CATEGORY_COLUMN_NAME] = sub_category
                n_cat = entry.loc[0, CATEGORY_COLUMN_NAME]
                n_sub_cat = entry.loc[0, SUB_CATEGORY_COLUMN_NAME]


                # Update the database
                incident_df = self.incidentWrapper.keepGeneralCols(entry)
                training_df = self.incidentWrapper.keepTrainingCols(entry)
                self.updateIncidentData(incident_df)
                self.updateTrainingData(training_df)
                self.inform('[incidentBase]: changeIncidentClass(): Change of :',id,'to',n_cat,n_sub_cat,'was successful!')



    ## Common functionality
    def getRelavantIndex(self, df_entry, df_database, log=''):
        # Check it has one entry
        if df_entry.shape[0] != 1:
            self.inform(log, 'The incoming dataframe had more/less than 1 entry, Aborting.')
            return -1

        # Get number of occurances of id in the database
        incidence_id = str(df_entry.loc[0][INDEX_COLUMN_NAME])
        incidence_id = incidence_id.replace(' ', '')
        self.inform(log, 'Incoming incidence_id is:',incidence_id)
        occurances = df_database.loc[df_database[INDEX_COLUMN_NAME].astype(str) == incidence_id].shape[0]

        # Find the right index for the new entry
        if occurances == 0:
            self.inform(log, 'Found NO occurance adding it at the end')
            ind = df_database.shape[0]
        elif occurances == 1:
            self.inform(log, 'Found one occurance, replacing it')
            ind = df_database.loc[df_database[INDEX_COLUMN_NAME].astype(str) == incidence_id].index[0]
        else:
            self.inform(log, 'Database has multiple occurances of id:', incidence_id)
            ind = -1

        return ind

import pandas as pd

from .configurator import INDEX_COLUMN_NAME

"""
COPYRIGHT none
This module abstracts the updating and pulling from the
csv database files in the database folder
"""

class IncidentBase:
    def __init__(self, incident_wrapper, path_to_training, path_to_vectors, path_to_incidents):
        self.incidentWrapper = incident_wrapper
        self.path_to_training = path_to_training
        self.path_to_vectors = path_to_vectors
        self.path_to_incidents = path_to_incidents

    def updateTrainingData(self, entry_list):
        # Construct dataframe, get id and see if there are any previous entries for id
        train_df = pd.read_csv(self.path_to_training).reset_index(drop=True)
        vector_df = pd.read_csv(self.path_to_vectors).reset_index(drop=True)
        incidence_id = entry_list[0]
        occurances = train_df[train_df[INDEX_COLUMN_NAME] == incidence_id].shape[0]

        # Find the right index for the new entry
        if occurances == 0:
            print('Found NO occurance adding it at the end')
            ind = train_df.shape[0]
        elif occurances == 1:
            print('Found one occurance, replacing it')
            ind = train_df.loc[train_df[INDEX_COLUMN_NAME] == incidence_id].index[0]
        else:
            print('Database has multiple occurances of id:', incidence_id)
            return False

        # Replace the entry at the correct index
        train_df.loc[ind] = entry_list

        # Get the new entry as a one-row dataframe and process it for vectors
        df_to_process = train_df.loc[[ind]].copy()
        processed_df = self.incidentWrapper.processIncident(df_to_process).reset_index()
        processed_entry = processed_df.loc[0]

        # Replace the corresponding index of the vector database
        vector_df.loc[ind] = processed_entry

        # Save the new dfs back as csv files
        train_df.to_csv(self.path_to_training, index=False)
        vector_df.to_csv(self.path_to_vectors, index=False)
        return True

    def updateIncidentData(self, entry_list):
        pass

    def getEntry(self, id):
        pass
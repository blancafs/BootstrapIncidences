import pandas as pd

from .configurator import Utils, INDEX_COLUMN_NAME

"""
COPYRIGHT none
This module abstracts the updating and pulling from the
csv database files in the database folder
"""

class IncidentBase:
    """

    """
    def __init__(self, incident_wrapper, path_to_training, path_to_vectors, path_to_incidents):
        self.incidentWrapper = incident_wrapper
        self.path_to_training = path_to_training
        self.path_to_vectors = path_to_vectors
        self.path_to_incidents = path_to_incidents

    ## Updates the training databases (both vector and non-vector), by adding or replacing the given incident
    def updateTrainingData(self, entry_list):
        """Connects to the next available port.

        Args:
          minimum: A port value greater or equal to 1024.
        Raises:
          ValueError: If the minimum port specified is less than 1024.
          ConnectionError: If no available port is found.
        Returns:
          The new minimum port.
        """
        # Construct dataframe, get id and see if there are any previous entries for id
        train_df = pd.read_csv(self.path_to_training).reset_index(drop=True)
        vector_df = pd.read_csv(self.path_to_vectors).reset_index(drop=True)
        incidence_id = entry_list[0]
        occurances = train_df[train_df[INDEX_COLUMN_NAME] == incidence_id].shape[0]

        # Find the right index for the new entry
        if occurances == 0:
            print('[incidentBase]: updateTrainingData(): Found NO occurance adding it at the end')
            ind = train_df.shape[0]
        elif occurances == 1:
            print('[incidentBase]: updateTrainingData(): Found one occurance, replacing it')
            ind = train_df.loc[train_df[INDEX_COLUMN_NAME] == incidence_id].index[0]
        else:
            print('[incidentBase]: updateTrainingData(): Database has multiple occurances of id:', incidence_id)
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
        Utils.saveCSV(train_df, self.path_to_training)
        Utils.saveCSV(vector_df, self.path_to_vectors)
        return True

    ## Updates the incident database with the given incident, replacing or adding it at the end
    def updateIncidentData(self, entry_list):
        incident_df = pd.read_csv(self.path_to_incidents).reset_index(drop=True)
        incidence_id = entry_list[0]
        occurances = incident_df[incident_df[INDEX_COLUMN_NAME] == incidence_id].shape[0]

        # Find the right index for the new entry
        if occurances == 0:
            print('[incidentBase]: updateIncidentData(): Found NO occurance adding it at the end')
            ind = incident_df.shape[0]
        elif occurances == 1:
            print('[incidentBase]: updateIncidentData(): Found one occurance, replacing it')
            ind = incident_df.loc[incident_df[INDEX_COLUMN_NAME] == incidence_id].index[0]
        else:
            print('[incidentBase]: updateIncidentData(): Database has multiple occurances of id:', incidence_id)
            return False

        # Replace the entry at the correct index and save it back to csv
        incident_df.loc[ind] = entry_list
        Utils.saveCSV(incident_df, self.path_to_incidents)
        return True

    ## Returns the required entry from its id (aviso_de_calidad) as a dataframe
    def getEntry(self, incidence_id):
        df = pd.read_csv(self.path_to_incidents).reset_index(drop=True)
        occurances = df[df[INDEX_COLUMN_NAME] == incidence_id].shape[0]
        # Find the right index for the entry
        if occurances == 0:
            print('[incidentBase]: getEntry(): Found NO occurance of', incidence_id)
            ind = -1
        elif occurances == 1:
            print('[incidentBase]: getEntry(): Found one occurance of' ,incidence_id)
            ind = df.loc[df[INDEX_COLUMN_NAME] == incidence_id].index[0]
        else:
            print('[incidentBase]: getEntry(): Database has multiple occurances of id:', incidence_id)
            ind = -1

        # If no entry found return an empty df, otherwise return df with single entry
        if ind == -1:
            entry = df.loc[df[INDEX_COLUMN_NAME] == -1]
        else:
            entry = df.loc[[ind]]

        entry.reset_index(inplace=True, drop=True)
        return entry
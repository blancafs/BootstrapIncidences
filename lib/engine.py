import os

from .incident import IncidentWrapper
from .incidentBase import IncidentBase
from .configurator import TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH

'''
Copyrights(R) Blancanator and Vanginous LTD

This is the interface class for communication between
the website and the backend
'''


class Engine:
    def __init__(self):
        self.incidentWrapper = IncidentWrapper(DEBUG=True)
        self.incidentBase = IncidentBase(self.incidentWrapper, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, None)
        self.incidentWrapper.inform('The web engine was initialized!')

    # Processes the incoming form
    def dealWithWebForm(self, form):
        incident_entry_df = self.incidentWrapper.parseIncidentFromWebForm(form)
        info = self.deal(incident_entry_df)
        return info

    ## Process the file, retrieve required information and delete it
    def dealWithFile(self, file_path):
        # Extract file info
        incident_entry_df = self.incidentWrapper.parseIncidentFromFile(file_path)
        info = self.deal(incident_entry_df)
        return info


    ## Deals with the incoming dataframe entry
    def deal(self, incident_entry_df):
        # Deal with data
        predicted_incident_entry_df = self.incidentWrapper.getPredictedIncidentEntry(incident_entry_df)
        training_entry_df = self.incidentWrapper.keepTrainingCols(predicted_incident_entry_df)

        # Update general database
        '''
        Here update the csv file with all info parsed from excel file
        '''
        # Update vector and training database
        entry_list = list(training_entry_df.loc[0])
        self.incidentBase.updateTrainingData(entry_list)

        # Delete the file
        os.remove(file_path)

        # Return relevant info
        info = list(predicted_incident_entry_df.loc[0])
        return str(info)


    ## Return all data for this incident id
    def retrieveId(self, incident_id):
        results = self.incidentBase.getEntry(incident_id)
        pass

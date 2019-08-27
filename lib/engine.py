import os

from .incident import IncidentWrapper
from .incidentBase import IncidentBase
from .configurator import Utils, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH
from .forms import FormBuilder

'''
Copyrights(R) Blancanator and Vanginous LTD

This is the interface class for communication between
the website and the backend
'''


class Engine:
    def __init__(self):
        self.incidentWrapper = IncidentWrapper(DEBUG=True)
        self.incidentBase = IncidentBase(self.incidentWrapper, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH)
        self.incidentWrapper.inform('The web engine was initialized!')

    # Processes the incoming form
    def dealWithWebForm(self, form):
        incident_entry_df = self.incidentWrapper.parseIncidentFromWebForm(form)
        print(incident_entry_df)
        info = self.deal(incident_entry_df)
        self.incidentWrapper.inform('Form was dealt-with!')
        return info

    ## Process the file, retrieve required information and delete it
    def dealWithFile(self, file_path):
        self.incidentWrapper.inform('Dealing with file')
        incident_entry_df = self.incidentWrapper.parseIncidentFromFile(file_path)
        self.incidentWrapper.inform('File was parsed to the following entry:')
        print(incident_entry_df)
        info = self.deal(incident_entry_df)
        os.remove(file_path)
        self.incidentWrapper.inform('File was dealt-with and deleted!')
        return info


    ## Deals with the incoming dataframe entry
    def deal(self, incident_entry_df):
        # Deal with data
        predicted_incident_entry_df = self.incidentWrapper.getPredictedIncidentEntry(incident_entry_df)
        training_entry_df = self.incidentWrapper.keepTrainingCols(predicted_incident_entry_df)
        general_entry_df = self.incidentWrapper.keepGeneralCols(predicted_incident_entry_df)

        # Update general database
        entry_list = list(general_entry_df.loc[0])
        self.incidentBase.updateIncidentData(entry_list)

        # Update vector and training database
        training_entry_list = list(training_entry_df.loc[0])
        self.incidentBase.updateTrainingData(training_entry_list)

        # Return relevant info
        info = list(predicted_incident_entry_df.loc[0])
        return str(info)


    ## Return all data for this incident id (UNSAFE ID INPUT)
    def retrieveFormFromId(self, id):
        # Check if None
        if id is None:
            return FormBuilder.buildEmptyForm()

        # Check that id does not contain any illegal characters
        if Utils.isInteger(id):
            entry_df = self.incidentBase.getEntry(int(id))
            form = FormBuilder.buildFromEntry(entry_df)

        # If id is not a number then return an empty result with the same input
        else:
            form = FormBuilder.buildEmptyForm()

        form.id = id
        return form



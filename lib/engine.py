import os

from .debug import Debug
from .incident import IncidentWrapper
from .incidentBase import IncidentBase
from .configurator import Utils, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH
from .forms import FormBuilder

'''
Copyrights(R) Blancanator and Vanginous LTD

This is the interface class for communication between
the website and the backend
'''


class Engine(Debug):
    def __init__(self):
        self.performInitCheck()
        self.incidentWrapper = IncidentWrapper()
        self.incidentBase = IncidentBase(self.incidentWrapper, TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH)
        self.inform('[main]: init(): The web engine was initialized!')

    # Processes the incoming form
    def dealWithWebForm(self, form):
        # Parse form
        incident_entry_df = self.incidentWrapper.parseIncidentFromWebForm(form)
        print(incident_entry_df)

        # Deal with form
        info = self.deal(incident_entry_df)
        self.inform('[main]: dealWithWebForm(): Form was dealt-with!')
        return info

    ## Process the file, retrieve required information and delete it
    def dealWithFile(self, file_path):
        # Parse file
        incident_entry_df = self.incidentWrapper.parseIncidentFromFile(file_path)
        print(incident_entry_df)

        # Deal with file
        info = self.deal(incident_entry_df)
        os.remove(file_path)
        self.inform('[main]: dealWithFile(): File was dealt-with and deleted!')
        return info


    ## Return all data for this incident id
    def retrieveFormFromId(self, id):
        # Check that id does not contain any illegal characters, otherwise return empty form
        if Utils.isInteger(id):
            entry_df = self.incidentBase.getEntry(int(id))
            form = FormBuilder.buildFromEntry(entry_df)
        else:
            form = FormBuilder.buildEmptyForm()

        # Set the form id
        form.id = id
        return form


    ## Deals with the incoming dataframe entry
    def deal(self, incident_entry_df):
        # Deal with data
        predicted_incident_entry_df = self.incidentWrapper.getPredictedIncidentEntry(incident_entry_df)
        training_entry_df = self.incidentWrapper.keepTrainingCols(predicted_incident_entry_df)
        general_entry_df = self.incidentWrapper.keepGeneralCols(predicted_incident_entry_df)

        # Update general database and training databases
        self.incidentBase.updateIncidentData(general_entry_df)
        self.incidentBase.updateTrainingData(training_entry_df)

        return True

    ## Performs initialization checks
    def performInitCheck(self):
        Utils.performSystemCheck()

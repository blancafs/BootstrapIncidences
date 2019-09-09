# Get application parent dir
import os
path = os.path.dirname(os.path.realpath(__file__))
path += '/../'

from flask import url_for


########################
### GLOBAL VARIABLES ###
########################
DEBUG = True
PORT = 5000

# Column name variables
INDEX_COLUMN_NAME = 'id'
CODIGO_COLUMN_NAME = 'codigo_cliente'
MATERIAL_COLUMN_NAME = 'material'
TEXT_COLUMN_NAME = 'texto_sap'
ANALYSIS_COLUMN_NAME = 'analysis_de_causas'
CAUSA_COLUMN_NAME = 'causa_raiz'
SIMILARITY_COLUMN_NAME = 'similarity'
CUTE_NAMES =  ['Aviso de Calidad:', 'Codigo Cliente: ', 'Material Afectado: ','Texto SAP: ', 'Analysis de Causas: ','Causa Raiz: ', 'Category: ', 'Sub-Category: ',\
                'Similar Incidents: ']

CATEGORY_COLUMN_NAME = 'category'
SUB_CATEGORY_COLUMN_NAME = 'sub_category'
VECTOR_COLUMN_NAME = 'vectorized_texts'

# Paths
DATABASE_PATH = 'data/'
MODELS_PATH = 'models/'
UPLOADS_PATH = 'uploads/'

# File names
TEXT_DATABASE_NAME = 'training_data.csv'
VECTOR_DATABASE_NAME = 'training_data_vectors.csv'
CONFIG_FILE_NAME = 'config.txt'
GENERAL_DATABASE_NAME = 'general_data.csv'
MULTILINGUAL_MODEL_NAME = 'multilingual-large'
USER_DATABASE_NAME = 'user_table.csv'

# Final variables
TEXT_DATABASE_PATH = path + DATABASE_PATH + TEXT_DATABASE_NAME
VECTOR_DATABASE_PATH = path + DATABASE_PATH + VECTOR_DATABASE_NAME
GENERAL_DATABASE_PATH = path + DATABASE_PATH + GENERAL_DATABASE_NAME
MODEL_FOLDER_PATH = path + MODELS_PATH + MULTILINGUAL_MODEL_NAME
CONFIG_FILE_PATH = path + CONFIG_FILE_NAME

#####################################################################
### Class to read and parse the config ##############################
#####################################################################
class ConfigParser:
    """

    This class reads and parses the config file to set important variables such as paths to models.
    """

    def __init__(self, path_to_config):
        """
        Takes the path to the configuration file in the constructor.

        Args:
            path_to_config: Path to config file
        """
        self.info = self.parseFile(path_to_config)
        self.model_name, self.param_dict = self.extractInfo()

    ## Parses file and returns only usefull lines
    def parseFile(self, path_to_config):
        """
        Strips the file of spaces and commas.

        Args:
            path_to_config: Passed in the constructor
        Returns:
            string: The clean text from the file
        """
        ## Read lines with no comment
        f = open(path_to_config)
        no_comms = [x.rstrip('\n') for x in f.readlines() if ('#' not in x)]

        # Return non-empty lines
        return [x.replace(' ','') for x in no_comms if x]


    ## Exctracts model and dict from info
    def extractInfo(self):
        """
        Given the clean file, this method extracts the model and dictionary information.

        Returns:
          string: The name of the model to use
          dictionary: The dictionary of parameters to use for the session.
        """
        lines = self.info.copy()
        model_name = ''
        param_dict = {}

        # Get info from each line
        for line in lines:
            key = line.split('=')[0]
            val = line.split('=')[1]
            if key=='model':
                model_name = val
            else:
                # Check if it is a number
                try:
                    new_val = float(val)
                    param_dict.update({key:new_val})
                except ValueError:
                    param_dict.update({key:val})

        return model_name, param_dict


    ## Getters ##
    def getModelName(self):
        return self.model_name

    def getParamDict(self):
        return self.param_dict



######################################################################
### Class to return the model string, and the parameter dictionary ###
######################################################################
class ConfigGetter:
    """
    This class returns the model string and parameter dictionary, the getter method for the class above.
    """

    def __init__(self):
        """
        The constructor creates a ConfigParser object by giving it the established config file path, any getter method thereafter returns the model and parameter dictionary
        using methods from the class ConfigParser.
        """
        self.parser = ConfigParser(CONFIG_FILE_PATH)

    ## Returns model string from config file
    def getModelName(self):
        return self.parser.getModelName()

    ## Returns parameter dict from config
    def getParamDict(self):
        return self.parser.getParamDict()



############################################
################## UTILS ###################
############################################
class Utils:
    """
    A class with useful methods used when python-provided ones did not suffice.
    """
    @staticmethod
    def performSystemCheck():
        # Check static directories
        directories_to_check = [path+DATABASE_PATH, path+UPLOADS_PATH]
        for dir in directories_to_check:
            if not os.path.exists(dir):
                os.mkdir(dir)
                print('[configurator]: performSystemCheck():',dir,'not found and was created')

        # Check model directory
        if not os.path.exists(path+MODELS_PATH):
            from .. import check_model

    # Checks if input variable is integer
    @staticmethod
    def isInteger(var):
        if var is None:
            return False

        try:
            num = int(var)
            return True
        except ValueError:
            return False

    @staticmethod
    def saveCSV(df, file_path, index=False):
        """
        This method was created for compatibility - you can set a specific encoding for the spanish language, or any other encoding/os necessary.

        Args:
            df: Pandas dataframe to save to the file
            file_path: Where the file should be saved
            index: If an index column is wanted in the dataframe saved in the csv file, set to true

        Returns:
            Automatically saves the file, does not return anything.
        """
        df.to_csv(file_path, index=index, encoding='utf-8-sig')


    @staticmethod
    def buildLinksString(sim_list):
        links_string = ""
        for sim in sim_list:
            temp_str = Utils.__buildInfoLink(sim) + " "
            links_string += temp_str

        return links_string

    @staticmethod
    def __buildInfoLink(id):
        id = str(id)
        return '<a href="'+ url_for('get_info', id=id) +'" >'+id+'</a>'

# Get application parent dir
import os
path = os.path.dirname(os.path.realpath(__file__))
path += '/../'


########################
### GLOBAL VARIABLES ###
########################

# Column name variables
INDEX_COLUMN_NAME = 'id'
CATEGORY_COLUMN_NAME = 'category'
SUB_CATEGORY_COLUMN_NAME = 'sub_category'
TEXT_COLUMN_NAME = 'texto_sap'
VECTOR_COLUMN_NAME = 'vectorized_texts'

# Paths
DATABASE_PATH = 'data/'
MODELS_PATH = 'models/'
U_DATABASE_PATH = 'users/'

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
USER_DATABASE_PATH = path + U_DATABASE_PATH + USER_DATABASE_NAME


#####################################################################
### Class to read and parse the config ##############################
#####################################################################
class ConfigParser:
    def __init__(self, path_to_config):
        self.info = self.parseFile(path_to_config)
        self.model_name, self.param_dict = self.extractInfo()

    ## Parses file and returns only usefull lines
    def parseFile(self, path_to_config):
        ## Read lines with no comment
        f = open(path_to_config)
        no_comms = [x.rstrip('\n') for x in f.readlines() if ('#' not in x)]

        # Return non-empty lines
        return [x.replace(' ','') for x in no_comms if x]


    ## Exctracts model and dict from info
    def extractInfo(self):
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

    def __init__(self):
        self.parser = ConfigParser(CONFIG_FILE_PATH)

    ## Returns model string from config file
    def getModelName(self):
        return self.parser.getModelName()

    ## Returns parameter dict from config
    def getParamDict(self):
        return self.parser.getParamDict()

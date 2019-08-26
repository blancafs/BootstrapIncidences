import os
from lib.configurator import USER_DATABASE_PATH
import pandas as pd

# Creates User object
class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def getUsername(self):
        return self.username

    def getEmail(self):
        return self.email


class UserDB:

    def __init__(self, path=USER_DATABASE_PATH):

        self.user_dataframe = pd.DataFrame()

        if not os.path.exists(path):
            str = 'touch ' + USER_DATABASE_PATH
            os.system(str)
            print('[USER DATABASE]: init: file did not exist')
        self.user_dataframe = pd.read_csv(path)
        if self.user_dataframe.empty:
            self.next_id = 1
            print('[USER DATABASE]: init: dataframe found empty')
        else:
            last_id = len(self.user_dataframe.index)
            self.next_id = last_id + 1
            print('[USER DATABASE]: init: next id is', self.next_id)

    # if user object doesnt exist in user database yet, create one and add to database
    def addUser(self, user):
        name = user.username
        email = user.email
        id = self.next_id
        user = [name, email, id]
        if name and email not in self.user_dataframe['username']:
            self.user_dataframe.loc[len(self.user_dataframe)] = {'username':name, 'email':email, 'id':id}
            self.user_dataframe.to_csv(USER_DATABASE_PATH)
            return 1
        # If failed to add because data already present, return -1
        print('[USER DATABASE]: addUser: user orname or email already in database')
        return -1

    # returns id based on username or email, identifier_type=email or username
    def getId(self,identifier, identifier_type='username'):
        if identifier in self.user_dataframe[identifier_type]:
            id = self.user_dataframe.loc[self.user_dataframe[identifier_type] == identifier, 'id'].iloc[0]
            return id
        else:
            # If failed to find id, return -1
            print('[USER DATABASE]: get id: given identifier not found in identifier field')
            return -1

    # changes username or email - prevalue is old username/value and postvalue is the one to change to
    def changeUser(self, pre_identifier, post_identifier, change_field):
        if pre_identifier in self.user_dataframe[change_field]:
            self.user_dataframe.loc[self.user_dataframe[change_field] == pre_identifier, change_field] = post_identifier
            self.user_dataframe.to_csv(USER_DATABASE_PATH)
            return 1
        else:
            # if identifier given does not exist in given field, return -1 to indicate failure
            print('[USER DATABASE]: changeUser: identifier did not exist in given field')
            return -1

    def checkUser(self, email, password):
        if email in self.user_dataframe['email']:
            pw = self.user_dataframe.loc[self.user_dataframe['email']==email]['password']
            if password == pw:
                return 1
        # if user password does not match, return -1
        print('[USER DATABASE]: checkUser: password given did not match saved password')
        return -1









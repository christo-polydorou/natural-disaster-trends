import psycopg2
import psqlConfig as config

class DataSource:
    '''
    DataSource executes all of the queries on the database.
    It also formats the data to send back to the frontend, typically in a list
    or some other collection or object.
    '''

    class UserInput:
        '''
        UserInput is an object that contains all of the inputs
        so that we aren't passing a bunch of parameters around.
        '''
        def __init__(self, inputStartYear, inputEndYear, inputStateList, inputDisasterTypeList, inputDisasterDeclarationTypeList):
            '''
            Holds all the parameters from a user input for searching the disasters database.

            Parameters:
                inputStartYear - the first year of the disasters the user wants, stored as an integer
                inputEndYear - the last year of the disasters the user wants, stored as an integer
                inputStateList - a list of all the two-character state identifiers the user wants to find natural disasters in
                inputDisasterTypeList - a list of all the disaster types the user wants to find natural disasters in
                inputDisasterDeclarationTypeList - a list of all the two-character disaster declaration types the user wants to find natural disasters in

            Returns:
                None
            '''
            self.startYear = inputStartYear
            self.endYear = inputEndYear
            self.states = inputStateList
            self.disasterTypes = inputDisasterTypeList
            self.disasterDeclarationTypes = inputDisasterDeclarationTypeList


    def __init__(self):
        self.connection = self.connect()

    def setUserInput(self, inputStartYear, inputEndYear, inputStateList, inputDisasterTypeList, inputDisasterDeclarationTypeList):
        '''
        Initializes the UserInput class

        Parameters:
            inputStartYear - the first year of the disasters the user wants, stored as an integer
            inputEndYear - the last year of the disasters the user wants, stored as an integer
            inputStateList - a list of all the two-character state identifiers the user wants to find natural disasters in
            inputDisasterTypeList - a list of all the disaster types the user wants to find natural disasters in
            inputDisasterDeclarationTypeList - a list of all the two-character disaster declaration types the user wants to find natural disasters in

        Return:
            The UserInput object that will contain the users data
        '''

        userInputObject = self.UserInput(inputStartYear, inputEndYear, inputStateList, inputDisasterTypeList, inputDisasterDeclarationTypeList)
        return userInputObject

    def connect(self):
        '''
        Establishes a connection to the database with the following credentials:
            user - username, which is also the name of the database
            password - the password for this database on perlman

        Returns:
            a database connection.

        Note: exits if a connection cannot be established.
        '''
        try:
            connection = psycopg2.connect(database=config.database, user=config.user, password=config.password, host="localhost")
        except Exception as e:
            print("Connection error: ", e)
            exit()
        return connection

    def queryDatabase(self, userInput):
        '''
        Returns a list of all the natural disaster entries that fit the userInput variables (search parameters).

        Parameters:
            connection - the connection to the database
            userInput - a UserInput object containing the search parameters of the query

        Return:
            a list of tuples of all of the natural disasters that occured within the specified parameters

        Note:
            Returns an empty list if any parameter is None or is an empty list
            (don't try to query without parameters it wouldn't return anything anyways)
        '''

        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM disasters WHERE (declaration_year BETWEEN %s AND %s) AND (state = ANY(%s)) AND (incident_type = ANY(%s)) AND (declaration_type = ANY(%s))"
            data = (userInput.startYear, userInput.endYear, userInput.states, userInput.disasterTypes, userInput.disasterDeclarationTypes,)
            cursor.execute(query, data)
            datasetWithoutDuplicates = self.removeDuplicateDisasters(cursor.fetchall())
            return datasetWithoutDuplicates
        except Exception as e:
            print("Something went wrong when executing the query: ", e)
            return []

    def getDisastersByYear(self, years):
        '''
        Returns a list of all the natural disasters that have occured in the specified years.

        Parameters:
            connection - the connection to the database
            years - a list of years to get natural disasters from

        Return:
            a list of tuples of all of the natural disasters that occured in the specified years
        '''
        dataList = []
        try:
            cursor = self.connection.cursor()
            for year in years:
                query = "SELECT * FROM disasters WHERE declaration_year = " + str(year)
                cursor.execute(query, (year,))
                dataList.append(cursor.fetchall())
            return dataList

        except Exception as e:
            print("Something went wrong when executing the query: ", e)
            return None

    def getDisastersByState(self, states):
        '''
        Returns a list of all the natural disasters that have occurred in the specified states.

        Parameters:
            connection - the connection to the database
            years - a list of years to get natural disasters from

        Return:
            a list of tuples of all of the natural disasters that occured in the specified years
        '''
        dataList = []
        try:
            cursor = self.connection.cursor()
            for inputState in states:
                query = "SELECT * FROM disasters WHERE state = \'" + inputState + "\';"
                cursor.execute(query, (inputState,))
                dataList.append(cursor.fetchall())
            return dataList

        except Exception as e:
            print("Something went wrong when executing the query: ", e)
            return None

    def removeDuplicateDisasters(self, naturalDisasterList):
        '''
        Removes all but the first entry of each disaster ID number in the provided list

        Parameters:
            naturalDisasterList - a list of disasters to remove duplicates from

        Return:
            a list containing only the first disaster entry of each ID number
            or False if there was an error parsing the data.
        '''

        newDataList = []
        idList  = []
        try:
            for entry in naturalDisasterList:
                if int(entry[1]) not in idList:
                    newDataList.append(entry)
                    idList.append(int(entry[1]))
            return newDataList
        except Exception as e:
            print("Something went wrong when parsing the data: ", e)
            return False

    def countResultOccurances(self, resultList, searchParameter, sortOrder):
        '''
        Counts the amount of occurances of the search parameter in the result list

        Parameters:
            resultsList: the list that is being counted
            searchParameter: the search parameter that is searched in resultsList

        Return:
            The resulting occurances that were found in resultsList
        '''

        resultsDictionary = {}
        index = self.parameterToIndex(searchParameter)
        if index == -1:
            print("Invalid Parameter!")
            return None
        for result in resultList:
            if result[index] in resultsDictionary:
                resultsDictionary[result[index]] += 1
            else:
                resultsDictionary[result[index]] = 1

        occuranceResultsList = self.sortResultOccurances(resultsDictionary, sortOrder)

        return occuranceResultsList

    def sortResultOccurances(self, resultsDictionary, sortOrder):
        '''
        Takes in a dictionary and turns the keys into a list and the values in a list. They are both then added to a list that is returned.
        The key-value pairs are sorted as indicated by the user. The keys and values correspond to each other in the output lists.

        Parameters:
            resultsDictionary: the dictionary that is being used to create the returned list
            sortOrder: the order in which to sort the data

        Return: The list containing the dictionaries keys and values.
        '''



        keyList = []
        valueList = []
        resultsDictLength = len(resultsDictionary)

        if (sortOrder == "defaultSort"): # doesn't sort it, just converts the dictionary to two lists
            for dictKey in resultsDictionary:
                keyList.append(dictKey)
                valueList.append(resultsDictionary.get(dictKey))
        else:
            while len(keyList) != resultsDictLength: # sorts it in ascending/descending order then converts
                num = 0
                key = ""
                for dictKey in resultsDictionary:
                    if resultsDictionary.get(dictKey) >= num:
                        key = dictKey
                        num = resultsDictionary.get(dictKey)
                keyList.append(key)
                valueList.append(resultsDictionary.get(key))
                del resultsDictionary[key]
            if (sortOrder == "ascendingSort"): # flips the list order
                keyList.reverse()
                valueList.reverse()

        resultsList = []
        resultsList.append(keyList)
        resultsList.append(valueList)

        return resultsList


    def parameterToIndex(self, searchParameter):
        '''
        Converts a string sort parameter to the corresponding results tuple index.

        Parameters:
            searchParameter: what parameter to convert

        Return:
            the integer position of that parameter in the results tuples. or -1 if its given an invalid parameter
        '''
        switcher = {
            "declarationString": 0,
            "idNumber": 1,
            "state": 2,
            "declarationType": 3,
            "declarationDate": 4,
            "declarationYear": 5,
            "incidentType": 6,
            "declarationTitle": 7,
            "ihProgramDeclared": 8,
            "iaProgramDeclared": 9,
            "paProgramDeclared": 10,
            "hmProgramDeclared": 11,
            "incidentBeginDate": 12,
            "incidentEndDate": 13,
            "fipsNumber": 14,
            "designatedArea": 15,
            "idHash": 16,
        }
        print(switcher.get(searchParameter, -1))
        return(switcher.get(searchParameter, -1))

def main():

    dataSourceInstance = DataSource()
    dataSourceInstance.connection.close()

main()

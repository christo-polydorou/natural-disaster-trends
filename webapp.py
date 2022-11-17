import flask
from flask import render_template, request
import sys
from datasource import DataSource
app = flask.Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def renderHomePage():
    '''
    This method renders the home page
    '''
    return render_template('homePage.html')

@app.route('/aboutdata')
def renderAboutDataPage():
    '''
    This method renders the about data page
    '''
    return render_template('aboutDataPage.html')

@app.route('/results', methods=['POST', 'GET'])
def getDisasterData():
    '''
    This method is called when the form request is submitted. The user's input is pulled from the HTML file, cleaned up a bit,
    sent to datasource to pull the disasters that fit the user's input, and then sent to the template disasterResults.html
    '''
    if request.method == 'POST':
        result = request.form

    checkedStates = getStates(result)
    checkedDisasterTypes = getDisasterType(result)
    checkedDeclarationTypes = getDeclarationType(result)
    horizontalAxis = getHorizontalAxis(result)
    startYear = getStartYear(result)
    endYear = getEndYear(result)
    graphSort = getGraphSort(result)
    checkedALLCheckboxes = getALLCheckboxes(result)
    checkedViewCheckboxes = getViewCheckboxes(result)

    datasourceObject = DataSource()
    inputedDataObject = datasourceObject.setUserInput(int(result.get('startYear')), int(result.get('endYear')), checkedStates, checkedDisasterTypes, checkedDeclarationTypes)
    disastersFromDatabase = datasourceObject.queryDatabase(inputedDataObject)
    sortedDisastersByParameter = datasourceObject.countResultOccurances(disastersFromDatabase, horizontalAxis, graphSort)

    userInputtedCheckboxes = []
    userInputtedCheckboxes.append([checkedStates,checkedDisasterTypes,checkedDeclarationTypes,checkedALLCheckboxes, checkedViewCheckboxes])

    dropdownValues = [horizontalAxis, startYear, endYear, graphSort]
    return render_template('disasterResults.html', allDisasters=disastersFromDatabase, dropdownValues=dropdownValues, checkedStates=checkedStates, checkedDisasterTypes=checkedDisasterTypes, checkedDeclarationTypes=checkedDeclarationTypes, sortedDisastersByParameter=sortedDisastersByParameter, userInputtedCheckboxes=userInputtedCheckboxes)


def getStates(results):
    '''
    Finds all the states in results and returns them in a list

    Parameters:
        results: The request.form from homePage.html. This is an immutable dictionary.
    return:
        The list of all the states in results
    '''

    states = ["AK","AL","AR","AS","AZ","CA","CO","CT","DC","DE","FL","GA","GU","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD","ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VA","VI","VT","WA","WI","WV","WY"]
    checkedStates =[]
    if "allStates" in results:
        checkedStates = states
    else:
        for state in states:
            if state in results:
                checkedStates.append(state)
    return checkedStates


def getDisasterType(results):
    '''
    Finds all the disaster types in results and returns them in a list

    Parameters:
        results: The request.form from homePage.html. This is an immutable dictionary.
    return:
        The list of all the disaster types in results
    '''

    disasterTypes = ['Biological','Chemical','Coastal Storm','Dam/Levee Break','Drought','Earthquake','Fire','Fishing Losses','Flood','Freezing','Human Cause','Hurricane','Mud/Landslide','Other','Severe Ice Storm','Severe Storm(s)','Snow','Terrorist','Tornado','Toxic Substances','Tsunami','Typhoon','Volcano']
    checkedDisasterTypes = []
    if "allDisasters" in results:
        checkedDisasterTypes = disasterTypes
    else:
        for disasterType in disasterTypes:
            if disasterType in results:
                checkedDisasterTypes.append(disasterType)
    return checkedDisasterTypes

def getDeclarationType(results):
    '''
    Finds all the declaration types in results and returns them in a list

    Parameters:
        results: The request.form from homePage.html. This is an immutable dictionary.
    return:
        The list of all the declaration types in results
    '''

    declarationTypes = ['DR','EM','FM']
    checkedDeclarationTypes = []
    if "allDeclarations" in results:
        checkedDeclarationTypes = declarationTypes
    else:
        for declarationType in declarationTypes:
            if declarationType in results:
                checkedDeclarationTypes.append(declarationType)
    return checkedDeclarationTypes

def getALLCheckboxes(results):
    '''
    Finds all the "ALL" checkboxes in results and returns them in a list

    Parameters:
        results: The request.form from homePage.html. This is an immutable dictionary.
    return:
        The list of all the ALL checkboxes that have been selected.
    '''

    ALLCheckboxes = ['allStates','allDisasters','allDeclarations']
    checkedALLCheckboxes = []
    for checkbox in ALLCheckboxes:
        if checkbox in results:
            checkedALLCheckboxes.append(checkbox)
    return checkedALLCheckboxes

def getViewCheckboxes(results):
    '''
    Finds all the view style checkboxs in results and returns them in a list

    Parameters:
        results: The request.form from homePage.html. This is an immutable dictionary.
    return:
        The list containing the checked style checkbox(es)
    '''

    tableViewCheckboxes = ['advancedSettingsView', 'tableView']
    checkedViewCheckboxes = []
    for checkbox in tableViewCheckboxes:
        if checkbox in results:
            checkedViewCheckboxes.append(checkbox)
    return checkedViewCheckboxes

def getHorizontalAxis(results):
    '''
    Finds the horizontal axis variable in the list results

    Parameter:
        results: The request.form from homePage.html. This is an immutable dictionary.

    Return:
         A string that is the variable for the horizontal axis
    '''

    return results.get("horizontalAxis")

def getStartYear(results):
    '''
    Finds the startYear variable in the list results

    Parameter:
        results: The request.form from homePage.html. This is an immutable dictionary.

    Return:
         A string that is the variable for the start year
    '''

    return results.get("startYear")

def getEndYear(results):
    '''
    Finds the endYear variable in the list results

    Parameter:
        results: The request.form from homePage.html. This is an immutable dictionary.

    Return:
         A string that is the variable for the end year
    '''

    return results.get("endYear")

def getGraphSort(results):
    '''
    Finds the graphSort variable in the list results

    Parameter:
        results: The request.form from homePage.html. This is an immutable dictionary.

    Return:
         A string that is the variable for the graphSort order
    '''

    return results.get("graphSort")



'''
Run the program by typing 'python3 localhost [port]'
'''

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
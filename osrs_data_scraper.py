import requests
import lxml.html as lh

# Global Variables
url = 'https://oldschool.runescape.wiki/w/Trailblazer_League/Guide/Quests'
areaDict = {1:'Misthalin', 2: 'Karamja', 3:'Asgarnia', 4:'Desert', 5:'Fremennik', 6:'Kandarin', 7:'Morytania', 8:'Tirannwn', 9:'Wilderness'}
reqDict = {'Chompy bird hat|Chompy Bird Hunting':{'areasRequired':['Kandarin'],'autoAreas':[]}, 'Natural history quiz':{'areasRequired':['Misthalin'],'autoAreas':[]}}


# Populates requirement dictionary given a list of rows
def fillReqDict(tr_elements):
    for row, tr in enumerate(tr_elements):
        # Skipping header info, table starts on 11
        if row < 11:
            continue
        questName = ""
        areasRequired = []
        autoAreas = []
        for col, te in enumerate(tr):
            # Check for text content, store info if so
            if te.text_content() != "":
                info = te.text_content()
                if col == 0:
                    questName = info
                elif info == "Auto":
                    autoAreas.append(areaDict[col])
            else:
                # Check for children. Use their column number to get area required.
                children = te.getchildren()
                if len(children) > 0:
                    areasRequired.append(areaDict[col])
        # Update dictionary
        reqDict[questName] = {"areasRequired":areasRequired, "autoAreas":autoAreas}


# Fills last two columns on each quest table
# inputName: name of source file
# outputName: name of output file for result
def populateColumns(inputName, outputName):
    # Read/store contents from input file
    myFile = open(inputName)
    content = myFile.read()
    myFile.close()

    
    pos = 0
    while True:
        # Loop through input file finding the end of the column headers for each table
        pos = content.find("!Trailblazer auto", pos)
        
        # Loop condition. Stop when at EOF
        if pos == -1 or pos >= len(content):
            break
        pos += 41 # Move pointer len('!Trailblazer auto unlock (no experience)') spaces

        # Last quest is above !Total
        endpos = content.find("!Total", pos)

        # Loop condition. Stop when at EOF
        if endpos == -1 or endpos >= len(content):
            break

        # Save info using pointers found
        questInfo = content[pos:endpos]
        # Split info by quest
        questLines = questInfo.split("|-\n|[[")
        # Loop over quests, skip first empty value
        for i, line in enumerate(questLines[1:len(questLines)], 1):
            # edge case: last quest has an extra |-\n due to split
            if i == len(questLines)-1:
                line = line[:-3] #remove extra |-\n before adding
            a = 0
            b = line.find("]]")
            questName = line[a:b]

            # Recipe for Disaster edge case
            if questName == "Recipe for Disaster":
                phrase = "Recipe for Disaster/"
                newpos = line.find(phrase)
                name = line[newpos+len(phrase):]
                newpos = name.find("|")
                name = name[:newpos]
                questName = name
            # Camelot Training Room edge case
            if questName == "Camelot training room":
                questName = "King's Ransom"

            # Reattach split string characters with separator
            questLines[i] = "|-\n|[[" + line + "||"
            # Modify page values based on values in dictionary
            if questName in reqDict:
                areasRequired = reqDict[questName]["areasRequired"]
                autoAreas = reqDict[questName]["autoAreas"]
                if len(areasRequired) == 0 and len(autoAreas) == 0:
                    questLines[i] += "N/A||N/A"
                else:
                    for area in areasRequired:
                        questLines[i] += "{{TB|"+ area +"}} "
                    questLines[i] += "||"
                    for area in autoAreas:
                        questLines[i] += "{{TB|"+ area +"}} "
            else:
                if questName != '':
                    questLines[i] += "N/A||N/A"
        # Edge case. Add final separator
        questLines[i] += "\n|-\n"
        # Join all quest lines, skip first blank value
        newQuestInfo = "\n".join(questLines[1:len(questLines)])
        # Place quest info in proper place in main content
        content = content[:pos] + newQuestInfo + content[endpos:]
    # Write content to output file
    myFile = open(outputName, "w")
    myFile.write(content)
    myFile.close()        


# Adds two new columns to the table in source file
def addNewColumns(inputName, outputName):
    # Read/Store input file content
    myFile = open(inputName)
    content = myFile.read()
    myFile.close()

    pos = 0
    while True:
        # Loop through input file finding the end of the column headers for each table
        pos = content.find("!Enemy to defeat", pos)
        # Loop condition: end when at EOF
        if pos == -1 or pos >= len(content):
            break
        # Place two new columns in place
        content = content[:pos+17] + "!Trailblazer area requirements\n!Trailblazer auto unlock (no experience)\n" + content[pos+17:]
        pos += 88 # len("!Enemy to defeat") + len("!Trailblazer area requirements...")
    # Write/Save changes to output file
    myFile = open(outputName, "w")
    myFile.write(content)
    myFile.close()


# Get page info from web request
page = requests.get(url)

# Store contents from website in a doc
doc = lh.fromstring(page.content)

# Parse data into rows
tr_elements = doc.xpath('//tr')

# Fill requirement dictionary based on row data
fillReqDict(tr_elements)

# Add two new columns to source file
addNewColumns("source.txt", "intermediateResult.txt")

# Populate two new columns 
populateColumns("intermediateResult.txt", "finalResult.txt")

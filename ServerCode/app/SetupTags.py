"""This is a file to set up tags in the DB, it will run when the db is run, but it is callable from the module"""

def readTags(filename):
    Taglist = []
    with open(filename, 'r') as file:
        for line in file:
            Taglist.append(line.strip())
    Taglist.sort()
    return Taglist
        

def createTags():
    Taglist = readTags("app/Tags.txt")
    return Taglist


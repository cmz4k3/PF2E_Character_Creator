from tkinter import *
import tkinter.messagebox
from PIL import Image,ImageTk #had to install  "pip install pillow"
import xlrd #had to install "pip install xlrd"
import math
import random

#Access levelup charts dynamically
class_levelup_workbook = xlrd.open_workbook("Class levelup charts.xlsx")
class_list = class_levelup_workbook.sheet_names() #you can use this list to populate the list of classes
#you can also access it by using class_levelup_workbook.sheet_by_name(<class name>) if it is stored as a string, or
#sheet_by_index(<id>) if everything is stored in the same order
if "Template" in class_list:
    class_list.remove("Template") #Ignore the template

#Access sublcass features dynamically, like Sorcerer bloodlines
#These are to be picked like feats, but are only chosen once, at level 1
subclass_features = xlrd.open_workbook("subfeatures.xlsx")
subfeatures = subclass_features.sheet_names() #Contains a list of stuff like Bloodline, Arcane School, Muse, etc.

#This method takes in a Sorcerer bloodline name and retruns what spell list the sorcerer can cast from
def getSorcSpellList(Bloodline):
    bloodline_sheet = subclass_features.sheet_by_name("Bloodline")
    for index in range(1, bloodline_sheet.nrows):
        if bloodline_sheet.cell(index, 0).value == Bloodline:
            return bloodline_sheet.cell(index, 4).value

#feat_sheets = wb.sheet_names() #will contain entries like "Fighter_Attack", "Fighter_Utility", etc.
#use these to access by xlrd.sheet_by_name(<desired_sheet>) for easier indexing

#Section for variables to store the charcter's information
class_subfeatures = [] #Append to this list to assign things like a Sorcerer' Bloodline, a Bard's Muse, etc. Use the name of the choice made.
spell_list = "" #Change this by class selected, and for Sorcerers, by Bloodline (it appears as a 5th column for Bloodlines).
FeatChoices = [] #I moved this from your Submit function, since we now need to reference it outside the function
#Dictionaries can be accessed by key values, e.g. Skills["Stealth"] will get the value for Stealth, or AbilityScores["Charisma"] for Charisma
Skills = {
        "Acrobatics": 0,
        "Arcana": 0,
        "Athletics": 0,
        "Crafting": 0,
        "Deception": 0,
        "Diplomacy": 0,
        "Intimidation": 0,
        "Lore": 0,
        "Medicine": 0,
        "Nature": 0,
        "Occultism": 0,
        "Performance": 0,
        "Religion": 0,
        "Society": 0,
        "Stealth": 0,
        "Survival": 0,
        "Theivery": 0
        }
#Use to convert proficiency bonuses from string to int or from int to string.
#Untrained in 0, Trained is 2, Expert is 4, Master is 6, and Legendary is 8.
Proficiency = {
        0: "Untrained",
        2: "Trained",
        4: "Expert",
        6: "Master",
        8: "Legendary",
        "Untrained": 0,
        "Trained": 2,
        "Expert": 4,
        "Master": 6,
        "Legendary": 8
        }

AbilityScores = {
        "Strength": 10,
        "Dexterity": 10,
        "Constitution": 10,
        "Intelligence": 10,
        "Wisdom": 10,
        "Charisma": 10
        }
#End section for character information variables

#For use with feat prerequisites
#Returns true if the character has the prereq selected already, false if not.
#<Type> is which column the prereq is from. Pass in "Feat", "Skill", or "Other", depending on which column from the database you pull the prereq from.
#<Prereq> is the actual contents of the cell. Pass in everything, this function will split by semicolon and parse it.
#You'll have to check weapon type matching elsewhere, I'm not sure where you store what weapon the character will use.
def hasPrereq(Type, Prereq):
    Reqs = []
    if ";" in Prereq:
        Reqs = Prereq.split(";")
    else:
        Reqs.append(Prereq)
    if Type == "Feat":
        for feat in Reqs:
            if feat not in FeatChoices:
                return False #Feat not found, prereq not met
        return True #Proof by lack of contradictions
    if Type == "Skill":
        for skill in Reqs:
            parseReq = skill.split(":")
            if(int(Skills[parseReq[0]])) < int(Proficiency(int(parseReq[1]))):
                return False #Skill proficiency rank too low, prereq not met
        return True #Proof by lack of contradictions
    if Type == "Other":
        for other in Reqs:
            parseReq = other.split(":")
            #Check class subfeature choice
            if parseReq[0] == "Subfeature":
                if parseReq[1] not in class_subfeatures:
                    return False #Missing feature, prereq not met
            #Check ability score
            if parseReq[0] in AbilityScores:
                if AbilityScores[parseReq[0]] < int(parseReq[1]):
                    return False #Ability Score too low, prereq not met
            #Check spell list
            if parseReq[0] == "Spell List":
                if parseReq[1] != spell_list:
                    return False #Spell list didn't match, prereq not met
        return True #Proof by lack of contradictions
    #End of input parsing. Error and failsafe past this point.
    print("Error in hasPrereq, either the Type was not incorrect or it was Other and it could not be parsed.")
    return False #Failsafe, just in case we somehow got a type we couldn't handle

root = Tk()
root.geometry('600x650')
root.title("Character Creator")
root.config(background="white")

def DeleteListElement(List):
	Index = List.curselection()
	if Index:
		List.delete(int(Index[0]))


def AddListElement(List, TotalFeats, FeatChoices, LastFeatIndex):
	if(LastFeatIndex[0] != (len(FeatChoices) - 1) and List.size() < TotalFeats):
		LastFeatIndex[0] += 1
		List.insert(END, FeatChoices[LastFeatIndex[0]])
	else:
		print("Full or no feats left")

def FinalDisplay(Race, Class, Background, Level, Weapon, RaceFeatChoices, ClassFeatChoices, GeneralFeatChoices, SkillFeatChoices, Focus, RaceInfo, ClassInfo, StatBonuses):
	GeneralFeatChoices = [i for i in GeneralFeatChoices if i not in SkillFeatChoices]
	CLastFeatIndex = [0]
	RLastFeatIndex = [0]
	GLastFeatIndex = [0]
	SLastFeatIndex = [0]
	HP = int(ClassInfo[0]) + int(RaceInfo[4])
	if(Race == "Dwarf"):
		HP += 2
	Armor = 16
	if(Focus[1] == 1 and Focus[2] == 1):
		Armor = 14 #to do
	elif(Focus[1] == 1 and Focus[2] == 0):
		Armor = 16
	elif(Focus[1] == 0 and Focus[2] == 1):
		Armor = 11
	else:
		Armor = 12
	Final = Tk()
	Final.geometry('600x800')
	Final.title("Final Character")
	Title=Label(Final,text="Meet Your Character!",font=("Times", 12,"bold")).place(x=200,y=20)

	#Size = RaceInfo[5]
	Speed = int(RaceInfo[6])
	Strength = 10 + StatBonuses[0]
	Constitution = 10 + StatBonuses[1]
	Wisdom = 10 + StatBonuses[2]
	Intelligence = 10 + StatBonuses[3]
	Dexterity = 10 + StatBonuses[4]
	Charisma = 10 + StatBonuses[5]

	String1 = "Character Ancestry: " + str(Race)
	String2 = "Character Class: " + str(Class)
	String3 = "Character Level: " + str(Level)
	String4 = "Character Weapon: " + str(Weapon)
	String5 = "Character HP: " + str(HP)
	String6 = "Character AC: " + str(Armor)
	String7 = "Character Background: " + str(Background)
	String8 = "Character Speed: " + str(Speed)
	String9 = "Character Strength: " + str(Strength)
	String10 = "Character Constitution: " + str(Constitution)
	String11 = "Character Wisdom: " + str(Wisdom)
	String12 = "Character Intelligence: " + str(Intelligence)
	String13 = "Character Dexterity: " + str(Dexterity)
	String14 = "Character Charisma: " + str(Charisma)

	TotalStrings1 = String1 + "\n\n" + String2 + "\n\n" + String3 + "\n\n" + String4 + "\n\n" + String5 + "\n\n" + String6 + "\n\n" + String7
	CharacterInfo1 = Label(Final, text=TotalStrings1,width=30,font=("bold", 10), justify=LEFT)
	CharacterInfo1.place(x=50,y=60)

	TotalStrings1 = String8 + "\n\n" + String9 + "\n\n" + String10 + "\n\n" + String11 + "\n\n" + String12 + "\n\n" + String13 + "\n\n" + String14
	CharacterInfo1 = Label(Final, text=TotalStrings1,width=30,font=("bold", 10), justify=LEFT)
	CharacterInfo1.place(x=280,y=60)

	ShiftX1 = 250
	ShiftY1 = 220

	label_C = Label(Final, text="Class Feats:",width=30,font=("bold", 10), justify=LEFT)
	label_C.place(x=0,y=280)
	
	TotalClassFeats = ClassInfo[3]
	if(len(ClassFeatChoices) < TotalClassFeats):
		TotalClassFeats = len(ClassFeatChoices)
	ClassList = Listbox(Final, width=20, height=10)
	scrollC = Scrollbar(Final, orient=VERTICAL)
	scrollC.config(command=ClassList.yview)
	ClassList.config(yscrollcommand=scrollC.set)
	print(ClassFeatChoices)
	print(TotalClassFeats)
	for i in range(TotalClassFeats):	
		ClassList.insert(END, ClassFeatChoices[i])
		CLastFeatIndex = [i]
	ClassList.place(x=75, y=310)
	scrollC.pack(side=RIGHT, fill=Y)
	scrollC.place(x=200,y=310, height = 163)
	delete1 = Button(Final, text="Delete", command= lambda: DeleteListElement(ClassList))
	delete1.place(x=218,y=310)
	add1 = Button(Final, text="Add", command= lambda: AddListElement(ClassList, TotalClassFeats, ClassFeatChoices, CLastFeatIndex))
	add1.place(x=218,y=350)

	label_R = Label(Final, text="Race Feats:",width=30,font=("bold", 10), justify=LEFT)
	label_R.place(x=-10+ShiftX1,y=280)

	TotalRaceFeats = ClassInfo[1]
	if(len(RaceFeatChoices) < TotalRaceFeats):
		TotalRaceFeats = len(RaceFeatChoices)
	RaceList = Listbox(Final, width=20, height=10)
	scrollR = Scrollbar(Final, orient=VERTICAL)
	scrollR.config(command=RaceList.yview)
	RaceList.config(yscrollcommand=scrollR.set)
	for i in range(TotalRaceFeats):	
		RaceList.insert(END, RaceFeatChoices[i])
		RLastFeatIndex = [i]
	RaceList.place(x=75+ShiftX1, y=310)
	scrollR.pack(side=RIGHT, fill=Y)
	scrollR.place(x=200+ShiftX1,y=310, height = 163)
	delete2 = Button(Final, text="Delete", command= lambda: DeleteListElement(RaceList))
	delete2.place(x=218+ShiftX1,y=310)
	add2 = Button(Final, text="Add", command= lambda: AddListElement(RaceList, TotalRaceFeats, RaceFeatChoices, RLastFeatIndex))
	add2.place(x=218+ShiftX1,y=350)

	label_G = Label(Final, text="General Feats:",width=30,font=("bold", 10), justify=LEFT)
	label_G.place(x=5,y=280+ShiftY1)

	TotalGeneralFeats = ClassInfo[2]
	if(len(GeneralFeatChoices) < TotalGeneralFeats):
		TotalGeneralFeats = len(GeneralFeatChoices)
	GeneralList = Listbox(Final, width=20, height=10)
	scrollG = Scrollbar(Final, orient=VERTICAL)
	scrollG.config(command=GeneralList.yview)
	GeneralList.config(yscrollcommand=scrollG.set)
	for i in range(TotalGeneralFeats):	
		GeneralList.insert(END, GeneralFeatChoices[i])
		GLastFeatIndex = [i]
	GeneralList.place(x=75, y=310+ShiftY1)
	scrollG.pack(side=RIGHT, fill=Y)
	scrollG.place(x=200,y=310+ShiftY1, height = 163)
	delete3 = Button(Final, text="Delete", command= lambda: DeleteListElement(GeneralList))
	delete3.place(x=218,y=310+ShiftY1)
	add3 = Button(Final, text="Add", command= lambda: AddListElement(GeneralList, TotalGeneralFeats, GeneralFeatChoices, GLastFeatIndex))
	add3.place(x=218,y=350+ShiftY1)

	label_S = Label(Final, text="Skill Feats:",width=30,font=("bold", 10), justify=LEFT)
	label_S.place(x=-15+ShiftX1,y=280+ShiftY1)

	TotalSkillFeats = ClassInfo[4]
	if(len(SkillFeatChoices) < TotalSkillFeats):
		TotalSkillFeats = len(SkillFeatChoices)
	SkillList = Listbox(Final, width=20, height=10)
	scrollS = Scrollbar(Final, orient=VERTICAL)
	scrollS.config(command=SkillList.yview)
	SkillList.config(yscrollcommand=scrollS.set)
	for i in range(TotalSkillFeats):	
		SkillList.insert(END, SkillFeatChoices[i])
		SLastFeatIndex = [i]
	SkillList.place(x=75+ShiftX1, y=310+ShiftY1)
	scrollS.pack(side=RIGHT, fill=Y)
	scrollS.place(x=200+ShiftX1,y=310+ShiftY1, height = 163)
	delete4 = Button(Final, text="Delete", command= lambda: DeleteListElement(SkillList))
	delete4.place(x=218+ShiftX1,y=310+ShiftY1)
	add4 = Button(Final, text="Add", command= lambda: AddListElement(SkillList, TotalSkillFeats, SkillFeatChoices, SLastFeatIndex))
	add4.place(x=218+ShiftX1,y=350+ShiftY1)

	Final.mainloop()

def Submit(race, background, Class, level, weapon, Attack, Defense, Utility, toggle):
	Level = 0
	Race = ""
	Focus = []
	if(Class.get() == "Select Class" and weapon.get() == "Select Weapon"):
		tkinter.messagebox.showinfo("Requirement","Class and Weapon are required")
	elif(Class.get() == "Select Class"):
		tkinter.messagebox.showinfo("Requirement","Class is required")
	elif(weapon.get() == "Select Weapon"):
		tkinter.messagebox.showinfo("Requirement","Weapon is required")
	else:
		if(Attack[0].get() == 1):
			Focus.append(1)
		else:
			Focus.append(0)
		if(Defense[0].get() == 1):
			Focus.append(1)
		else:
			Focus.append(0)
		if(Utility[0].get() == 1):
			Focus.append(1)
		else:
			Focus.append(0)
		if(level.get() == "Select Level"):
			Level = 1
		else:
			Level = int(level.get())

		xcelLocation = ("Feat_Database.xlsx")
		GSCFeats = xlrd.open_workbook(xcelLocation)
		ClassFeatsSheet = GSCFeats.sheet_by_name(str(Class.get()))
		GeneralFeatsSheet = GSCFeats.sheet_by_name("General")
		SkillFeatsSheet = GSCFeats.sheet_by_name("Skill")
		TotalEntriesC = ClassFeatsSheet.nrows - 1
		TotalEntriesG = GeneralFeatsSheet.nrows - 1
		TotalEntriesS = SkillFeatsSheet.nrows - 1

		Class = Class.get()
		weapon = weapon.get()
		ClassInfo = ClassSpecifics(Class, Level)
		ClassFeatChoices = OptimizeFeats(ClassFeatsSheet, TotalEntriesC, Level, weapon, Focus)
		GeneralFeatChoices = OptimizeFeats(GeneralFeatsSheet, TotalEntriesG, Level, weapon, Focus)
		SkillFeatChoices = OptimizeFeats(SkillFeatsSheet, TotalEntriesS, Level, weapon, Focus)

		if (race.get() == "Select Race"):
			if(Focus[1] == 0):
				Race = "Human" #OptimizeRace(Focus)
			else:
				Race = "Dwarf"
		else:
			Race = race.get()

		if (background.get() == "Select Background"):
			Background = "Acoylte"
		else:
			Background = background.get()

		xcelLocation = ("Ancestry_Race.xlsx")
		RaceDataBook = xlrd.open_workbook(xcelLocation)
		RaceFeatSheet = RaceDataBook.sheet_by_name(str(Race))
		RaceDataSheet = RaceDataBook.sheet_by_name("General")

		RaceInfo = RaceSpecifics(Race, RaceDataSheet)
		RaceFeatChoices = GetRaceFeats(RaceFeatSheet, Level)

		xcelLocation = ("Backgrounds.xlsx")
		BackgroundDataBook = xlrd.open_workbook(xcelLocation)
		BackgroundDataSheet = BackgroundDataBook.sheet_by_name("Sheet1")

		xcelLocation = ("ClassAttributes.xlsx")
		ClassAttributesDataBook = xlrd.open_workbook(xcelLocation)
		ClassDataSheet = ClassAttributesDataBook.sheet_by_name("Sheet1")

		StatBonuses = GetStatBonus(Focus, Race, RaceDataSheet, Background, BackgroundDataSheet, Class, ClassDataSheet, Level)
		#StatBonuses = [2,2,2,2,2,2]

		FinalDisplay(Race, Class, Background, Level, weapon, RaceFeatChoices, ClassFeatChoices, GeneralFeatChoices, SkillFeatChoices, Focus, RaceInfo, ClassInfo, StatBonuses)

#Just focuses on main attribute for class. If there is another option then it considers "Focus"
def GetStatBonus(Focus, Race, RaceDataSheet, Background, BackgroundDataSheet, Class, ClassDataSheet, Level):
	#Have 3 Focuses. First from Class. Second from Class(if it has one) or depending how they wanna "Focus". And Third from how they wanna "Focus"
	#Offense: Str, Dex, Con
	#Defense: Dex, Con, Wis 
	#Utility: Wis, Int, Cha
	#IF they pick two or more "Focuses", pick specifically defense since it is an alrounder
	StatBonuses = [0] * 6
	RAttributeBonuses = []
	BackgroundAttributeBonuses = []
	ClassAttributeBonuses = []
	FreeAttributeBonuses = []

	RaceInfo = RaceSpecifics(Race, RaceDataSheet)
	
	RAttributeBonuses.append(RaceInfo[0])
	RAttributeBonuses.append(RaceInfo[1])
	RAttributeBonuses.append(RaceInfo[2])
	RAttributeBonuses.append(RaceInfo[3])

	BRow = 0
	for i in range(1, BackgroundDataSheet.nrows):
		if(BackgroundDataSheet.cell_value(i,0) == Background):
			BRow = i
			break
	CRow = 0
	for i in range(1, ClassDataSheet.nrows):
		if(ClassDataSheet.cell_value(i,0) == Class):
			CRow = i
			break

	for i in range(len(RAttributeBonuses)):
		sign = 1
		if(i == 3):
			sign = -1
		if(RAttributeBonuses[i] == ""):
			break
		if(RAttributeBonuses[i] == "Free"):
			if(not(ClassDataSheet.cell_value(CRow, 1) in RAttributeBonuses)):
				RAttributeBonuses[i] = ClassDataSheet.cell_value(CRow, 1)
			else:
				RChoosenAttribute = ""
				#Defense
				if(Focus[1] == 1 or Focus == [0,0,0]):
					if(not("Dex" in RAttributeBonuses)):
						RChoosenAttribute = "Dex"
					elif(not("Con" in RAttributeBonuses)):
						RChoosenAttribute = "Con"
					else:
						RChoosenAttribute = "Wis"
				#Attack
				elif(Focus[0] == 1):
					if(not("Str" in RAttributeBonuses)):
						RChoosenAttribute = "Str"
					elif(not("Dex" in RAttributeBonuses)):
						RChoosenAttribute = "Dex"
					else:
						RChoosenAttribute = "Con"

				#Utility
				elif(Focus[2] == 1):
					if(not("Wis" in RAttributeBonuses)):
						RChoosenAttribute = "Wis"
					elif(not("Int" in RAttributeBonuses)):
						RChoosenAttribute = "Int"
					else:
						RChoosenAttribute = "Cha"
				#If it is 
				else:
					print("Error: Race Stat not selected")
				RAttributeBonuses[i] = RChoosenAttribute
		if(RAttributeBonuses[i] == "Str"):
			StatBonuses[0] = StatBonuses[0] + sign * 2
		elif(RAttributeBonuses[i] == "Con"):
			StatBonuses[1] = StatBonuses[1] + sign * 2
		elif(RAttributeBonuses[i] == "Wis"):
			StatBonuses[2] = StatBonuses[2] + sign * 2
		elif(RAttributeBonuses[i] == "Int"):
			StatBonuses[3] = StatBonuses[3] + sign * 2
		elif(RAttributeBonuses[i] == "Dex"):
			StatBonuses[4] = StatBonuses[4] + sign * 2
		elif(RAttributeBonuses[i] == "Cha"):
			StatBonuses[5] = StatBonuses[5] + sign * 2
		else:
			if(not(RAttributeBonuses[i] == "")):
				print("Error: Unknow Stat in RAttributeBonuses")
				print(RAttributeBonuses[i])

	BackgroundAttributeBonuses.append(BackgroundDataSheet.cell_value(BRow, 1))
	BackgroundAttributeBonuses.append(BackgroundDataSheet.cell_value(BRow, 2))
	for i in range(len(BackgroundAttributeBonuses)):
		if(BackgroundAttributeBonuses[i] == "Str"):
			StatBonuses[0] = StatBonuses[0] + 2
		elif(BackgroundAttributeBonuses[i] == "Con"):
			StatBonuses[1] = StatBonuses[1] + 2
		elif(BackgroundAttributeBonuses[i] == "Wis"):
			StatBonuses[2] = StatBonuses[2] + 2
		elif(BackgroundAttributeBonuses[i] == "Int"):
			StatBonuses[3] = StatBonuses[3] + 2
		elif(BackgroundAttributeBonuses[i] == "Dex"):
			StatBonuses[4] = StatBonuses[4] + 2
		elif(BackgroundAttributeBonuses[i] == "Cha"):
			StatBonuses[5] = StatBonuses[5] + 2
		else:
			print("Error: Unknow Stat in BackgroundAttributeBonuses")

	ClassAttributeBonuses.append(ClassDataSheet.cell_value(CRow, 1)) 
	if(ClassAttributeBonuses[0] == "Str"):
		StatBonuses[0] = StatBonuses[0] + 2
	elif(ClassAttributeBonuses[0] == "Con"):
		StatBonuses[1] = StatBonuses[1] + 2
	elif(ClassAttributeBonuses[0] == "Wis"):
		StatBonuses[2] = StatBonuses[2] + 2
	elif(ClassAttributeBonuses[0] == "Int"):
		StatBonuses[3] = StatBonuses[3] + 2
	elif(ClassAttributeBonuses[0] == "Dex"):
		StatBonuses[4] = StatBonuses[4] + 2
	elif(ClassAttributeBonuses[0] == "Cha"):
		StatBonuses[5] = StatBonuses[5] + 2
	else:
		print("Error: Unknow Stat in ClassAttributeBonuses")

	FreeAttributeBonuses.append(ClassDataSheet.cell_value(CRow, 1))
	FChoosenAttribute = ""
	#Defense
	if(Focus[1] == 1 or Focus == [0,0,0]):
		if(not("Dex" in FreeAttributeBonuses)):
			FChoosenAttribute = "Dex"
		else:
			FChoosenAttribute = "Con"
	#Attack
	elif(Focus[0] == 1):
		if(not("Str" in FreeAttributeBonuses)):
			FChoosenAttribute = "Str"
		else:
			FChoosenAttribute = "Dex"

	#Utility
	elif(Focus[2] == 1):
		if(not("Wis" in FreeAttributeBonuses)):
			FChoosenAttribute = "Wis"
		else:
			FChoosenAttribute = "Int"

	FreeAttributeBonuses.append(FChoosenAttribute)

	for i in range(len(FreeAttributeBonuses)):
		if(FreeAttributeBonuses[i] == "Str"):
			StatBonuses[0] = StatBonuses[0] + 2
		elif(FreeAttributeBonuses[i] == "Con"):
			StatBonuses[1] = StatBonuses[1] + 2
		elif(FreeAttributeBonuses[i] == "Wis"):
			StatBonuses[2] = StatBonuses[2] + 2
		elif(FreeAttributeBonuses[i] == "Int"):
			StatBonuses[3] = StatBonuses[3] + 2
		elif(FreeAttributeBonuses[i] == "Dex"):
			StatBonuses[4] = StatBonuses[4] + 2
		elif(FreeAttributeBonuses[i] == "Cha"):
			StatBonuses[5] = StatBonuses[5] + 2
		else:
			print("Error: Unknow Stat in FreeAttributeBonuses")

	StatProgressions = int(Level/5)
	for i in range(StatProgressions):
		Bonus = 2
		if(ClassAttributeBonuses[0] == "Str"):
			if(StatBonuses[0] >= 8):
				Bonus = 1
			StatBonuses[0] = StatBonuses[0] + Bonus
		elif(ClassAttributeBonuses[0] == "Con"):
			if(StatBonuses[1] >= 8):
				Bonus = 1
			StatBonuses[1] = StatBonuses[1] + Bonus
		elif(ClassAttributeBonuses[0] == "Wis"):
			if(StatBonuses[2] >= 8):
				Bonus = 1
			StatBonuses[2] = StatBonuses[2] + Bonus
		elif(ClassAttributeBonuses[0] == "Int"):
			if(StatBonuses[3] >= 8):
				Bonus = 1
			StatBonuses[3] = StatBonuses[3] + Bonus
		elif(ClassAttributeBonuses[0] == "Dex"):
			if(StatBonuses[4] >= 8):
				Bonus = 1
			StatBonuses[4] = StatBonuses[4] + Bonus
		elif(ClassAttributeBonuses[0] == "Cha"):
			if(StatBonuses[5] >= 8):
				Bonus = 1
			StatBonuses[5] = StatBonuses[5] + Bonus

	return StatBonuses


def GetRaceFeats(RaceFeatSheet, Level):
	RaceFeatList = []
	for i in range(1, RaceFeatSheet.nrows):
		if(RaceFeatSheet.cell_value(i,6) <= int(Level)):
			RaceFeatList.append(RaceFeatSheet.cell_value(i,0))
		else:
			break
	random.shuffle(RaceFeatList)
	return RaceFeatList


def RaceSpecifics(Race, RaceDataSheet):
	Row = 0
	for i in range(1, RaceDataSheet.nrows):
		if(RaceDataSheet.cell_value(i,0) == Race):
			Row = i
	AbilityBoost1 = RaceDataSheet.cell_value(Row, 1) 
	AbilityBoost2 = RaceDataSheet.cell_value(Row, 2)
	AbilityBoost3 = RaceDataSheet.cell_value(Row, 3)
	AbilityFlaw = RaceDataSheet.cell_value(Row, 4)
	Health = RaceDataSheet.cell_value(Row, 5)
	Size = RaceDataSheet.cell_value(Row, 6)
	Speed = RaceDataSheet.cell_value(Row, 7)
	RaceInfo = []
	RaceInfo.append(AbilityBoost1)
	RaceInfo.append(AbilityBoost2)
	RaceInfo.append(AbilityBoost3)
	RaceInfo.append(AbilityFlaw)
	RaceInfo.append(Health)
	RaceInfo.append(Size)
	RaceInfo.append(Speed)
	return RaceInfo

#Returns health as well as total ancestry, general, and class feats
#the specific class gets at the given level.
def ClassSpecifics(Class, Level):
	ClassInfo = class_levelup_workbook.sheet_by_name(str(Class))
	Health = 0
	CFeats = 0 #Class Feats
	AFeats = 0 #Ancestry Feats
	GFeats = 0 #General Feats
	SFeats = 0 #Skill Feats
	#for j in range(1, ClassInfo.ncols):
	for i in range(1, ClassInfo.nrows):
		#print(ClassInfo.cell_value(i,j))
		if(ClassInfo.cell_value(i,0) == Level + 1):
			break;
		Health = Health + int(ClassInfo.cell_value(i, 1))
		if("Feat:Ancestry" in ClassInfo.cell_value(i, 4)):
			AFeats = AFeats + 1
		if("Feat:General" in ClassInfo.cell_value(i, 4)):
			GFeats = GFeats + 1
		if("Feat:" + str(Class) in ClassInfo.cell_value(i, 4)):
			CFeats = CFeats + 1
		if("Feat:Skill" in ClassInfo.cell_value(i, 4)):
			SFeats = SFeats + 1
	AllInfo = []
	AllInfo.append(Health)
	AllInfo.append(AFeats)
	AllInfo.append(GFeats)
	AllInfo.append(CFeats)
	AllInfo.append(SFeats)
	return AllInfo
	

def WeaponType(weapon): #Dual, Melee, Ranged, 1H, 2H, Any #agile, volley, shield, 2H, FH, reload_0, pierce
	Weapon = weapon
	WeaponTypes = []
	if(Weapon == "1-Handed"):
		WeaponTypes = ["Melee", "1H", "Any", "agile", "FH", "pierce"]
	elif(Weapon == "2-Handed"):
		WeaponTypes = ["Melee", "2H", "Any", "pierce"]
	elif(Weapon == "1-Handed/Shield"):
		WeaponTypes = ["Melee", "1H", "Any", "pierce", "agile", "shield"]
	elif(Weapon == "Dual-Wielding"):
		WeaponTypes = ["Melee", "Dual", "Any", "pierce", "agile"]
	elif(Weapon == "Shortbow"):
		WeaponTypes = ["Ranged", "Any", "reload_0"]
	elif(Weapon == "Longbow"):
		WeaponTypes = ["Ranged", "Any", "reload_0", "volley"]
	elif(Weapon == "Crossbow"):
		WeaponTypes = ["Ranged", "Any"]
	elif(Weapon == "Heavy-Crossbow"):
		WeaponTypes = ["Ranged", "Any"]
	else:
		WeaponTypes = ["Melee", "Ranged", "Any"]
	return WeaponTypes
	
	"1-Handed", "2-Handed", "1-Handed/Shield", 
	"Dual-Wielding", "Shortbow", "Longbow", "Crossbow", "Heavy-Crossbow"

def OptimizeFeats(ClassFeatsSheet, TotalEntries, level, weapon, Focus):
	WeaponTypes = WeaponType(weapon)
	FeatChoice = []
	Search = True
	while(Search):
		MaxRating = -1
		FeatIndex = -1
		#Attack
		if(Focus == [1,0,0]):
			for i in range(TotalEntries): #TotalEntries
				if((ClassFeatsSheet.cell_value(i+1,2) > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):
						MaxRating = ClassFeatsSheet.cell_value(i+1,2)
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#Defense
		elif(Focus == [0,1,0]):
			for i in range(TotalEntries): #TotalEntries
				if((ClassFeatsSheet.cell_value(i+1,4) > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):						
						MaxRating = ClassFeatsSheet.cell_value(i+1,4)
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#Utility
		elif(Focus == [0,0,1]):
			for i in range(TotalEntries): #TotalEntries
				if((ClassFeatsSheet.cell_value(i+1,3) > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):					
						MaxRating = ClassFeatsSheet.cell_value(i+1,3)
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#Attack and Defense
		elif(Focus == [1,1,0]):
			for i in range(TotalEntries): #TotalEntries
				if(((ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,4))/2 > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):						
						MaxRating = (ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,4))/2
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#Attack and Utility
		elif(Focus == [1,0,1]):
			for i in range(TotalEntries): #TotalEntries
				if(((ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,3))/2 > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):						
						MaxRating = (ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,3))/2
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#Defense and Utility
		elif(Focus == [0,1,1]):
			for i in range(TotalEntries): #TotalEntries
				if(((ClassFeatsSheet.cell_value(i+1,4) + ClassFeatsSheet.cell_value(i+1,3))/2 > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):						
						MaxRating = (ClassFeatsSheet.cell_value(i+1,4) + ClassFeatsSheet.cell_value(i+1,3))/2
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
		#All
		else:
			for i in range(TotalEntries): #TotalEntries
				if(((ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,4) + ClassFeatsSheet.cell_value(i+1,3))/3 > MaxRating) and (ClassFeatsSheet.cell_value(i+1,1) <= level) and not(ClassFeatsSheet.cell_value(i+1,0) in FeatChoice)):
					if(ClassFeatsSheet.cell_value(i+1,5) == "-" or ClassFeatsSheet.cell_value(i+1,5) in WeaponTypes and (ClassFeatsSheet.cell_value(i+1,6) == "-" or ClassFeatsSheet.cell_value(i+1,6) in WeaponTypes)):						
						MaxRating = (ClassFeatsSheet.cell_value(i+1,2) + ClassFeatsSheet.cell_value(i+1,4) + ClassFeatsSheet.cell_value(i+1,3))/3
						FeatIndex = i+1
			if(FeatIndex != -1):
				FeatChoice.append(ClassFeatsSheet.cell_value(FeatIndex,0))
			else:
				Search = False
	#print(FeatChoice)
	return FeatChoice

def AdvancedOptions(S2,S3,S5,S6,S7,S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,toggle):
	if(toggle[0] == False):
		S2.place(x=80, y=400)
		S3.place(x=80, y=460)
		S5.place(x=100, y=350)
		S6.place(x=160, y=350)
		S7.place(x=220, y=350)
		S8.place(x=100, y=370)
		S9.place(x=160, y=370)
		S10.place(x=220, y=370)
		S11.place(x=100, y=430)
		S12.place(x=160, y=430)
		S13.place(x=220, y=430)
		S14.place(x=100, y=490)
		S15.place(x=160, y=490)
		S16.place(x=220, y=490)
		S17.place(x=100, y=520)
		toggle[0] = True
	else:
		S2.place(x=80, y=360)
		S3.place(x=80, y=400)
		S5.place_forget()
		S6.place_forget()
		S7.place_forget()
		S8.place_forget()
		S9.place_forget()
		S10.place_forget()
		S11.place_forget()
		S12.place_forget()
		S13.place_forget()
		S14.place_forget()
		S15.place_forget()
		S16.place_forget()
		S17.place_forget()
		toggle[0] = False

#def test(newwin,event):
#	print (newwin.winfo_width())
#	print (newwin.winfo_height())

def new_winF():
	newwin = Tk()
	X = 400
	Y = 640
	newwin.geometry(str(X) + 'x' + str(Y))
	#newwin.update()
	#newwin.bind("<Configure>", lambda event: test(newwin, event))
	newwin.title("Pathfinder 2e")
	Race=StringVar(newwin)
	Class=StringVar(newwin)
	varA=StringVar(newwin)
	varB=StringVar(newwin)
	varC=StringVar(newwin)
	varL=StringVar(newwin)
	varW=StringVar(newwin)
	varAttack_0 = IntVar(newwin)
	varAttack_1 = IntVar(newwin)
	varAttack_2 = IntVar(newwin)
	varAttack_3 = IntVar(newwin)
	varAttack_4 = IntVar(newwin)
	varAttack_5 = IntVar(newwin)
	varAttack_6 = IntVar(newwin)
	varDefence_0 = IntVar(newwin)
	varDefence_1 = IntVar(newwin)
	varDefence_2 = IntVar(newwin)
	varDefence_3 = IntVar(newwin)
	varUtility_0 = IntVar(newwin)
	varUtility_1 = IntVar(newwin)
	varUtility_2 = IntVar(newwin)
	varUtility_3 = IntVar(newwin)
	varUtility_4 = IntVar(newwin)
	Title=Label(newwin,text="Welcome to Pathfinder 2nd Edition",relief="solid",font=("Times", 12,"bold")).place(x=90,y=20)

	#label_0 = Label(newwin, text="* Indicates required fields",width=20,fg = "red",font=("bold", 8))
	#label_0.place(x=90,y=55)

	label_1 = Label(newwin, text="Ancestry :",width=20,font=("bold", 10))
	label_1.place(x=39,y=80)
	RaceList=["Dwarf", "Elf", "Gnome", "Goblin", "Half-Elf", "Halfling", "Half-Orc", "Human"]
	droplist=OptionMenu(newwin,varA,*RaceList)
	varA.set("Select Race")
	droplist.config(width=16)
	droplist.place(x=160,y=75)

	label_2 = Label(newwin, text="Background :",width=20,font=("bold", 10))
	label_2.place(x=32,y=120)
	BackgroundList=["Acolyte", "Acrobat", "Animal Whisperer", "Artisan", "Artist", "Barkeep", "Barrister", "Bounty Hunter", "Charlatan", 
	"Criminal", "Detective", "Droskari Disciple", "Emissary", "Entertainer", "Farmhand", "Field Medic", "Fortune Teller", "Gambler",
	"Gladiator", "Guard", "Herbalist", "Hermit", "Hunter", "Laborer", "Martial Disciple", "Merchant", "Miner", "Noble", "Nomad",
	"Prisoner", "Sailor", "Scholar", "Scout", "Street Urchin", "Tinker", "Warrior"]
	droplist=OptionMenu(newwin,varB,*BackgroundList)
	varB.set("Select Background")
	droplist.config(width=16)
	droplist.place(x=160,y=115)

	label_3 = Label(newwin, text="Class :",width=20,font=("bold", 10))
	label_3.place(x=50,y=160)
	#ClassList=["Alchemist", "Barbarian", "Bard", "Champion", "Cleric", "Druid", "Fighter", "Monk", "Ranger", "Rogue", "Sorcerer", "Wizard"]
	droplist=OptionMenu(newwin,varC,*class_list)
	varC.set("Select Class")
	droplist.config(width=16)
	droplist.place(x=160,y=155)

	label_4 = Label(newwin, text="Level :",width=20,font=("bold", 10))
	label_4.place(x=50,y=200)
	LevelList=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
	droplist=OptionMenu(newwin,varL,*LevelList)
	varL.set("Select Level")
	droplist.config(width=16)
	droplist.place(x=160,y=195)

	label_5 = Label(newwin, text="Weapon :",width=20,font=("bold", 10))
	label_5.place(x=40,y=240)
	WeaponList=["1-Handed", "2-Handed", "1-Handed/Shield", "Dual-Wielding", "Shortbow", "Longbow", "Crossbow", "Heavy-Crossbow"]
	droplist=OptionMenu(newwin,varW,*WeaponList)
	varW.set("Select Weapon")
	droplist.config(width=16)
	droplist.place(x=160,y=235)

	label_6 = Label(newwin, text="Specialization :",width=20,font=("bold", 10))
	label_6.place(x=50,y=280)
	S1 = Checkbutton(newwin, text="Attack", variable=varAttack_0)
	S1.place(x=80,y=320)
	S2 = Checkbutton(newwin, text="Defense", variable=varDefence_0)
	S2.place(x=80,y=360)
	S3 = Checkbutton(newwin, text="Utility", variable=varUtility_0)
	S3.place(x=80,y=400)
	toggle = [False]
	S4 = Button(newwin, text="Advanced", command= lambda: AdvancedOptions(S2,S3,S5,S6,S7,S8,S9,S10,S11,S12,S13,S14,S15,S16,S17,toggle))
	S4.place(x=152,y=600)

	#L_5_6 = Label(newwin, text="Damage:",width=20,font=("bold", 10))
	S5 = Checkbutton(newwin, text="DOT", variable=varAttack_1)
	S6 = Checkbutton(newwin, text="Burst", variable=varAttack_2)
	#L_7_8 = Label(newwin, text="Target:",width=20,font=("bold", 10))
	S7 = Checkbutton(newwin, text="Single", variable=varAttack_3)
	S8 = Checkbutton(newwin, text="AOE", variable=varAttack_4)
	#L_9_10 = Label(newwin, text="Type:",width=20,font=("bold", 10))
	S9 = Checkbutton(newwin, text="Str", variable=varAttack_5)
	S10 = Checkbutton(newwin, text="Dex", variable=varAttack_6)

	S11 = Checkbutton(newwin, text="AC", variable=varDefence_1)
	S12 = Checkbutton(newwin, text="HP", variable=varDefence_2)
	S13 = Checkbutton(newwin, text="DR", variable=varDefence_3)

	S14 = Checkbutton(newwin, text="Shove", variable=varUtility_1)
	S15 = Checkbutton(newwin, text="Trip", variable=varUtility_2)
	S16 = Checkbutton(newwin, text="Disarm", variable=varUtility_3)
	S17 = Checkbutton(newwin, text="Movement", variable=varUtility_4)

	Attack = [varAttack_0, varAttack_1, varAttack_2, varAttack_3, varAttack_4, varAttack_5, varAttack_6]
	Defence = [varDefence_0, varDefence_1, varDefence_2, varDefence_3]
	Utility = [varUtility_0, varUtility_1, varUtility_2, varUtility_3, varUtility_4]


	submit = Button(newwin, text="Submit", command= lambda: Submit(varA, varB, varC, varL, varW, Attack, Defence, Utility, toggle))
	submit.place(x=160, y=560)
	newwin.mainloop()



class Example(Frame):
    def __init__(self, master, *pargs):
        Frame.__init__(self, master, *pargs)

        self.image = Image.open("Dragon.jpeg")
        self.img_copy= self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = Label(self, image=self.background_image)
        self.background.pack(fill=BOTH, expand=YES)
        self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)

e = Example(root)
e.pack(fill=BOTH, expand=YES)

label_0 = Label(root, text="Welcome to Character Creator",relief="solid",width=30,font=("Times", 19,"bold"))
label_0.place(x=90,y=150)

def Pathfinder1e():
	tkinter.messagebox.showinfo("D&D","Currently not ready")

def Pathfinder2e():
	new_winF()

def Dnd():
    tkinter.messagebox.showinfo("D&D","Currently not ready")

def ext_1():
    exit()

menu = Menu(root)
root.config(menu=menu)

subm1 = Menu(menu)
menu.add_cascade(label="File",menu=subm1)
subm1.add_command(label="Exit",command=ext_1)

subm2 = Menu(menu)
menu.add_cascade(label="Pathfinder",menu=subm2)
subm2.add_command(label="Pathfinder 1st edition",command=Pathfinder1e)
subm2.add_command(label="Pathfinder 2nd edition",command=Pathfinder2e)

subm3 = Menu(menu)
menu.add_cascade(label="D&D",menu=subm3)
subm3.add_command(label="D&D 1st edition",command=Dnd)
subm3.add_command(label="D&D 2nd edition",command=Dnd)
subm3.add_command(label="D&D 3rd edition",command=Dnd)
subm3.add_command(label="D&D 4th edition",command=Dnd)
subm3.add_command(label="D&D 5th edition",command=Dnd)

root.mainloop()

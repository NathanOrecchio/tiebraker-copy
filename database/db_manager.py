import logging
from pymongo import MongoClient
from pymongo.database import Database
from bson.objectid import ObjectId
from pymongo.collection import Collection

from models import Event

class MongoManager:
    __client : MongoClient = None
    __db : Database = None
    __event_collection : Collection = None
    __roster_collection : Collection = None
    __futsal_events_collection : Collection = None

    # Connect to Database
    def connect_to_database(self, URI : str, DEFAULT_DB : str):
        logging.info("Connecting to Database.")
        self.__client = MongoClient(URI)
        self.__db = self.__client.get_database(DEFAULT_DB)
        self.get_collections()
        logging.info("Connected to database.")


    def get_collections(self):
        self.__event_collection = self.__db.get_collection("Event")
        self.__roster_collection = self.__db.get_collection("Roster")
        self.__futsal_events_collection = self.__db.get_collection("FutsalEvent")

        if self.__event_collection is None:
            return {"Could not connect to events collection."}


    # Close Database conneciton
    def close_database_connection(self):
        logging.info("Closing database connection.")
        self.__client.close()
        logging.info("Database connection successfully closed.")


    async def format_age_division(self, event_id : str):
        age_divisions = self.__event_collection.find_one({"_id" : ObjectId(event_id)}, {"_id" : 0, "ageDivisions" : {"gender": 1, "years":1}}).get("ageDivisions")
        male_age_divisions = []
        female_age_divisions = []
        coed_age_divisions = []

        for division in age_divisions:
            if division["gender"] == "MALE":
                male_age_divisions.append(division["years"][0])
            elif division["gender"] == "FEMALE":
                female_age_divisions.append(division["years"][0])
            else:
                coed_age_divisions.append(division["years"][0])
        
        male_age_divisions.sort()
        female_age_divisions.sort()
        coed_age_divisions.sort()

        formatted_age_divisions = {
            "Boys" : male_age_divisions,
            "Girls" : female_age_divisions,
            "COED" : coed_age_divisions,
        }

        
        return formatted_age_divisions

    
    
    async def get_event_data(self, event_list : list) -> dict:
        # For event, Find the the rosters for every age division, and the red and yellow cards for the team

        # First create data variable that will be returned with the required data
        data = {}

        for event_id in event_list:
            formatted_age_divisions = await self.format_age_division(event_id=event_id)
            boys_rosters_info = await self.get_rosters(event_id=event_id, gender="MALE", divisions=formatted_age_divisions["Boys"])
            girls_rosters_info = await self.get_rosters(event_id=event_id, gender="FEMALE", divisions=formatted_age_divisions["Girls"])
            coed_rosters_info = await self.get_rosters(event_id=event_id, gender="COED", divisions=formatted_age_divisions["COED"])

            data[event_id] = boys_rosters_info
            data[event_id]["FEMALE"] = girls_rosters_info["FEMALE"]
            data[event_id]["COED"] = coed_rosters_info["COED"]
            

        return data    


    async def get_rosters(self, event_id : str, gender : str, divisions : list):
        # Find all of the rosters for the event and the age division and return only the roster id, name, and age division gender and age

        roster_data = { gender : {}}

        for roster in divisions:
            result = self.__roster_collection.find({"ageDivision.gender" : gender, "ageDivision.years" : [roster], "eventId" : ObjectId(event_id)}, {'_id' : 1, "name" : 1 })
            roster_card_info = []
            for item in result:
                formatted_result = await self.get_card_counts(roster_id=item["_id"])
                roster_card_info.append(formatted_result)
            roster_data[gender][str(roster)] = roster_card_info

        return roster_data
    
    async def get_roster_name(self, roster_id : str) -> str:
        roster_name = self.__roster_collection.find_one({"_id": ObjectId(roster_id)}, {"_id":0, "name":1}).get("name")

        return roster_name



    async def get_card_counts(self, roster_id : str):
        # Find all futsal events by team roster id and return the action id, action, team id, and user id
        roster_query = {"rosterId" : ObjectId(roster_id)}
        card_projections = {"_id":1, "action":1, "rosterId": 1, "userId": 1}
        team_card_info = list(self.__futsal_events_collection.find(roster_query, card_projections))

        formatted_card_info = {}
        team_red_cards = 0
        team_yellow_cards = 0

        for card in team_card_info:
            if card.get("action") == "RED_CARD":
                team_red_cards = team_red_cards + 1
            elif card.get("action") == "YELLOW_CARD":
                team_yellow_cards = team_yellow_cards + 1
        
        formatted_card_info["name"] = await self.get_roster_name(roster_id=roster_id)
        formatted_card_info["red_cards"] = team_red_cards
        formatted_card_info["yellow_cards"] = team_yellow_cards

        if formatted_card_info is not None:
            return formatted_card_info
        else:
            return {f"No match events found for that team {roster_id}"}

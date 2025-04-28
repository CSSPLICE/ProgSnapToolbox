

# Organization
progsnap2-client: A typescript logging library that provides objects and abstractions for keeping track of state and sending it gracefully to the server.
progsnap2: A python library with 3 packages for handling 
* progsnap2: a package with enums to hold the keywords, helper functions etc.
* progsnap2.data: a package ahndling read/writes from various databases using SQLAlchemy, representing all of the PS2 tables or subtables as Pandas dataframes
* progsnap2.api: a package with a FastAPI server that the client or other apps can connect to read and write to the database
* progsnap2.analyze: a package with common analytics for a PS2 dataset and useful abstractions
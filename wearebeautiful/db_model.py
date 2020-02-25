from peewee import *
import dateutil.parser

# This file is duplicate in the -tools repo. :(

db = SqliteDatabase(None)

class DBModel(Model):
    """
    Manifest metadata about a 3D model
    """

    class Meta:
        database = db
        table_name = "model"

    id = AutoField()
    model_id = TextField()
    code = TextField()
    created = DateField()
    released = DateField()
    processed = DateField()
    gender = TextField()
    gender_comment = TextField(null = False)
    body_type = TextField()
    body_part = TextField()
    pose = TextField()
    mother = TextField()
    arrangement = TextField()
    excited = TextField()
    tags = TextField(null = False)
    modification = TextField(null = False)
    comment = TextField(null = False)

    def parse_data(self):
        self.tags_list = self.tags.split(",")
        self.mods_list = self.modification.split(",")

    def __repr__(self):
        return "<DBModel(%s-%s)>" % (self.model_id, self.code)

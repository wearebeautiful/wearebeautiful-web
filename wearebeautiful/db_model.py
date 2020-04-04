from peewee import *
import dateutil.parser

# This file is duplicate in the -tools repo. :(

DB_FILE = "wab-models.db"
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
    version = IntegerField()
    code = TextField()
    created = DateField()
    released = DateField()
    gender = TextField()
    gender_comment = TextField(null = False)
    sex = TextField()
    sex_comment = TextField(null = False)
    body_type = TextField()
    body_part = TextField()
    pose = TextField()
    given_birth = TextField()
    arrangement = TextField()
    excited = TextField()
    tags = TextField(null = False)
    history = TextField(null = False)
    comment = TextField(null = False)

    def parse_data(self):
        self.info_list = []
        if self.comment:
            self.info_list.append("comment")
        self.tags_list = (self.tags or "").split(",")
        self.history_list = (self.history or "").split(",")
        if self.given_birth != "no":
            self.history_list.append((self.given_birth or "") + " birth")
        if self.excited != "not excited":
            self.history_list.append(self.excited)

        if self.version == 1:
            self.display_code = "%s-%s" % (self.model_id, self.code)
        else:
            self.display_code = "%s-%s-%d" % (self.model_id, self.code, self.version)

    def __repr__(self):
        return "<DBModel(%s-%s)>" % (self.model_id, self.code)

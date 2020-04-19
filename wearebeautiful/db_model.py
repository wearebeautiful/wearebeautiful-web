from peewee import *
import dateutil.parser

from wearebeautiful.utils import url_for_screenshot

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
    links = TextField(null = False)
    comment = TextField(null = False)

    def parse_data(self):
        self.info_list = []
        if self.comment:
            self.info_list.append("comment")
        if self.links:
            self.info_list.append("links")
        self.tags_list = (self.tags or "").split(",")
        self.history_list = (self.history or "").split(",")
        self.link_list = (self.links or "").split(" ")
        if self.given_birth != "no":
            self.history_list.append((self.given_birth or "") + " birth")

        if self.version == 1:
            self.display_code = "%s-%s" % (self.model_id, self.code)
        else:
            self.display_code = "%s-%s-%d" % (self.model_id, self.code, self.version)


    def english_description(self):

        desc = "A %s model of " % self.body_part
        if self.sex in ('male', 'female'):
            desc = "a %s " % self.sex
        elif self.sex == "intersex":
            desc = "an intersex person "
        else:
            desc = "a person "

        if self.body_type == "average":
            desc += "with an %s body type" % self.body_type
        else:
            desc += "with a %s body type" % self.body_type

        if self.given_birth != "no":
            desc += " who has given %s birth" % self.given_birth

        return desc


    def to_json(self):

        return {
            'model_id' : self.model_id,
            'version' : self.version,
            'code' : self.code,
            'created' : self.created.strftime("%Y-%m"),
            'released' : self.released.strftime("%Y-%m-%d"),
            'gender' : self.gender,
            'gender_comment' : self.gender_comment,
            'sex' : self.sex,
            'sex_comment' : self.sex_comment,
            'body_type' : self.body_type,
            'body_part' : self.body_part,
            'pose' : self.pose,
            'given_birth' : self.given_birth,
            'arrangement' : self.arrangement,
            'excited' : self.excited,
            'tags' : self.tags,
            'history' : self.history,
            'links' : self.links,
            'comment' : self.comment,
            'info_list' : self.info_list,
            'tags_list' : self.tags_list,
            'history_list' : self.history_list,
            'link_list' : self.link_list,
            'given_birth' : self.given_birth,
            'display_code' : self.display_code,
            'english_description' : self.english_description(),
            'screenshot_url' : url_for_screenshot(self.model_id, self.code, self.version)
        }

    def english_description(self):

        desc = "A %s model of " % self.body_part
        if self.sex in ('male', 'female'):
            desc = "a %s " % self.sex
        elif self.sex == "intersex":
            desc = "an intersex person "
        else:
            desc = "a person "

        if self.body_type == "average":
            desc += "with an %s body type" % self.body_type
        else:
            desc += "with a %s body type" % self.body_type

        if self.given_birth != "no":
            desc += " who has given %s birth" % self.given_birth

        return desc


    def __repr__(self):
        return "<DBModel(%s-%s)>" % (self.model_id, self.code)

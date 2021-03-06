import logging

import semver
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from marshmallow import fields, EXCLUDE, validates_schema, ValidationError as MarshmallowValidationError

from api_gateway.executiondb import Base, IDMixin, BaseSchema
from api_gateway.executiondb.action import ActionApiSchema

logger = logging.getLogger(__name__)


class AppApi(IDMixin, Base):
    __tablename__ = "app_api"
    name = Column(String(), nullable=False, unique=True)
    app_version = Column(String(), nullable=False)
    walkoff_version = Column(String(), nullable=False)
    description = Column(String(), default="")
    contact = Column(JSON, default={})
    license_ = Column(JSON, default={})
    external_docs = Column(JSON, default={})
    actions = relationship('ActionApi', backref='app_api', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, **kwargs):
        super(AppApi, self).__init__(**kwargs)
        self.validate()

    def validate(self):
        """Validates the object"""
        # ToDo: Allow broken App APIs to be visible on frontend with errors
        pass


class AppApiSchema(BaseSchema):
    """
    Schema for App API
    """
    actions = fields.Nested(ActionApiSchema, many=True)

    class Meta:
        model = AppApi
        unknown = EXCLUDE

    @validates_schema
    def validate_app_api(self, data):
        # Enforce Semantic Versioning
        for key in ("walkoff_version", "app_version"):
            try:
                semver.parse(data[key])
            except ValueError as e:
                raise MarshmallowValidationError(f"Error in {key}: {e}")

        # Version in name and app_version must match
        name = data["name"].split(":")
        if len(name) != 2:
            raise MarshmallowValidationError(f"App name must follow the format app_name:1.2.3")
        else:
            if name[1] != data["app_version"]:
                raise MarshmallowValidationError(f"Version in app_name must match version in app_version")

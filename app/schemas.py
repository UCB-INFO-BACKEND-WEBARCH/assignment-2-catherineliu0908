import re
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Category

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class TaskCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    due_date = fields.DateTime(required=False, allow_none=True)
    category_id = fields.Int(required=False, allow_none=True)

    @validates("category_id")
    def validate_category_id(self, value):
        if value is not None:
            category = Category.query.get(value)
            if not category:
                raise ValidationError("Category does not exist.")


class TaskUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))
    completed = fields.Bool(required=False)
    due_date = fields.DateTime(required=False, allow_none=True)
    category_id = fields.Int(required=False, allow_none=True)

    @validates("category_id")
    def validate_category_id(self, value):
        if value is not None:
            category = Category.query.get(value)
            if not category:
                raise ValidationError("Category does not exist.")


class CategoryCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(required=False, allow_none=True)

    @validates("color")
    def validate_color(self, value):
        if value is not None and not HEX_COLOR_RE.match(value):
            raise ValidationError("Color must be a valid hex code like #FF5733.")
# This file is part of Indico.
# Copyright (C) 2002 - 2015 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from indico.core.db import db
from indico.core.db.sqlalchemy import PyIntEnum
from indico.util.string import return_ascii
from indico.util.struct.enum import IndicoEnum


def _get_next_position(context):
    """Get the next position for a form item."""
    regform_id = context.current_parameters['registration_form_id']
    parent_id = context.current_parameters['parent_id']
    res = (db.session.query(db.func.max(RegistrationFormItem.position))
           .filter_by(parent_id=parent_id, registration_form_id=regform_id, is_deleted=False)
           .one())
    return (res[0] or 0) + 1


class RegistrationFormItemType(int, IndicoEnum):
    section = 1
    field = 2
    text = 3


class RegistrationFormItem(db.Model):
    __tablename__ = 'registration_form_items'
    __table_args__ = {'schema': 'event_registration'}
    __mapper_args__ = {
        'polymorphic_on': 'type',
        'polymorphic_identity': None
    }

    #: The ID of the object
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    #: The ID  of the registration form
    registration_form_id = db.Column(
        db.Integer,
        db.ForeignKey('event_registration.registration_forms.id'),
        nullable=False
    )
    #: The type of the registration form item
    type = db.Column(
        PyIntEnum(RegistrationFormItemType),
        nullable=False
    )
    #: The ID of the parent form item
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('event_registration.registration_form_items.id'),
        nullable=True
    )
    position = db.Column(
        db.Integer,
        nullable=False,
        default=_get_next_position
    )
    #: The title of this field
    title = db.Column(
        db.String,
        nullable=False
    )
    #: Description of this field
    description = db.Column(
        db.String,
        nullable=True
    )
    #: Whether the field is enabled
    is_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )
    #: Whether field has been "deleted"
    is_deleted = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    # The registration form
    registration_form = db.relationship(
        'RegistrationForm',
        lazy=True,
        backref=db.backref(
            'form_items',
            lazy=True,
            cascade='all, delete-orphan'
        )
    )

    # The children of the item and the parent backref
    children = db.relationship(
        'RegistrationFormItem',
        lazy=True,
        order_by='RegistrationFormItem.position',
        backref=db.backref(
            'parent',
            lazy=False,
            remote_side=[id]
        )
    )

    @property
    def view_data(self):
        """Returns object with data that Angular can understand"""
        raise NotImplementedError

    @return_ascii
    def __repr__(self):
        return '<{}({})>'.format(type(self).__name__, self.id)


class RegistrationFormSection(RegistrationFormItem):
    __mapper_args__ = {
        'polymorphic_identity': RegistrationFormItemType.section
    }

    @property
    def locator(self):
        return dict(self.registration_form.locator, section_id=self.id)

    @property
    def view_data(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'items': [child.view_data for child in self.children if not child.is_deleted],
            'enabled': self.is_enabled,
            '_type': 'GeneralSectionForm',
            'required': False
        }


class RegistrationFormText(RegistrationFormItem):
    __mapper_args__ = {
        'polymorphic_identity': RegistrationFormItemType.text
    }
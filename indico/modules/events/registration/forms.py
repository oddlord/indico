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

from wtforms.fields import StringField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional

from indico.util.i18n import _
from indico.web.forms.base import IndicoForm
from indico.web.forms.fields import IndicoDateTimeField
from indico.web.forms.validators import HiddenUnless, DateTimeRange, LinkedDateTime
from indico.web.forms.widgets import SwitchWidget


class RegistrationFormForm(IndicoForm):
    title = StringField(_("Title"), [DataRequired()], description=_("The title of the registration form"))
    introduction = TextAreaField(_("Introduction"),
                                 description=_("An introduction to be displayed before the registration process"))
    require_user = BooleanField(_("Only logged-in users"), widget=SwitchWidget(),
                                description=_("Only logged-in users can register"))
    limit_registrations = BooleanField(_("Limit registrations"), widget=SwitchWidget(),
                                       description=_("Whether there is a limit of registrations"))
    registration_limit = IntegerField(_("Capacity"), [HiddenUnless('limit_registrations'), DataRequired(),
                                                      NumberRange(min=1)],
                                      description=_("Maximum number of registrations"))


class RegistrationFormScheduleForm(IndicoForm):
    start_dt = IndicoDateTimeField(_("Start"), [DataRequired(), DateTimeRange(earliest='now')],
                                   description=_("Moment when the registrations will be open"))
    end_dt = IndicoDateTimeField(_("End"), [Optional(), LinkedDateTime('start_dt')],
                                 description=_("Moment when the registrations will be closed"))

    def __init__(self, *args, **kwargs):
        regform = kwargs.pop('regform')
        self.timezone = regform.event.tz
        super(IndicoForm, self).__init__(*args, **kwargs)
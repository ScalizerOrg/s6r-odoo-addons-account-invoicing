# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_date
from odoo.tools import frozendict, mute_logger, date_utils, config

import re
from collections import defaultdict
from psycopg2 import sql, DatabaseError


class SequenceMixin(models.AbstractModel):
    _inherit = 'sequence.mixin'


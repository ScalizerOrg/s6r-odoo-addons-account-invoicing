import logging
import re
from psycopg2 import sql, DatabaseError

from odoo import models, fields, api, _
from odoo.tools import frozendict, mute_logger, date_utils
from odoo.exceptions import ValidationError
from odoo.tools import config


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_last_sequence(self, relaxed=False, with_prefix=None):
        
        if self.move_type == 'out_invoice' and not config['test_enable']:
            date_start, date_end = self._get_sequence_date_range('year')
            moves = self.env['account.move'].sudo().search([
                ('move_type', '=', 'out_invoice'),
                ('journal_id', '=', self.journal_id.id),
                ('id', '!=', self.id or self._origin.id),
                ('name', 'not in', ('/', '', False)),
                ('date', '>=', date_start),
                ('date', '<=', date_end),
            ])
            moves_name = moves.mapped('name')

            numbers = [m.split('-')[2] for m in moves_name if len(m.split('-')) == 3]
            if numbers:
                return '{}-00-{}'.format(date_start.year, max(numbers))

        return super()._get_last_sequence(relaxed, with_prefix)

    def _get_sequence_format_param(self, previous):
        
        if self.move_type == 'out_invoice' and not config['test_enable']:
            if not previous or previous == '/':
                previous = self._get_starting_sequence()
            res = super()._get_sequence_format_param(previous)
            res[1]['prefix2'] = "{:02d}".format(self.date.month)
            return res
        return super()._get_sequence_format_param(previous)

    @api.model
    def _deduce_sequence_number_reset(self, name):
        
        if self.move_type == 'out_invoice' and not config['test_enable']:
            if not name or name == '/':
                name = self._get_starting_sequence()
            for regex, ret_val, requirements in [
                (self._sequence_yearly_regex, 'year', ['seq', 'prefix2', 'year']),
                (self._sequence_fixed_regex, 'never', ['seq']),
            ]:
                match = re.match(regex, name or '')
                if match:
                    groupdict = match.groupdict()
                    if (
                            groupdict.get('year_end') and groupdict.get('year')
                            and (
                            len(groupdict['year']) < len(groupdict['year_end'])
                            or self._truncate_year_to_length((int(groupdict['year']) + 1),
                                                             len(groupdict['year_end'])) != int(groupdict['year_end'])
                    )
                    ):
                        # year and year_end are not compatible for range (the difference is not 1)
                        continue
                    if all(groupdict.get(req) is not None for req in requirements):
                        return ret_val
            raise ValidationError(_(
                'The sequence regex should at least contain the seq grouping keys. For instance:\n'
                r'^(?P<prefix1>.*?)(?P<seq>\d*)(?P<suffix>\D*?)$'
            ))
        return super()._deduce_sequence_number_reset(name)

    def _set_next_sequence(self):

        if self.move_type == 'out_invoice' and not config['test_enable']:
            self.ensure_one()
            last_sequence = self._get_last_sequence()
            new = not last_sequence
            if new:
                last_sequence = self._get_last_sequence(relaxed=True) or self._get_starting_sequence()

            format_string, format_values = self._get_sequence_format_param(last_sequence)
            sequence_number_reset = self._deduce_sequence_number_reset(last_sequence)
            if new:
                date_start, date_end = self._get_sequence_date_range(sequence_number_reset)
                format_values['seq'] = 0
                format_values['year'] = self._truncate_year_to_length(date_start.year, format_values['year_length'])
                format_values['year_end'] = self._truncate_year_to_length(date_end.year, format_values['year_end_length'])
                format_values['month'] = date_start.month
                format_values['prefix2'] = "{:02d}".format(date_start.month)
            self.flush_recordset()
            registry = self.env.registry
            triggers = registry._field_triggers[self._fields[self._sequence_field]]
            for inverse_field, triggered_fields in triggers.items():
                for triggered_field in triggered_fields:
                    if not triggered_field.store or not triggered_field.compute:
                        continue
                    for field in registry.field_inverses[inverse_field[0]] if inverse_field else [None]:
                        self.env.add_to_compute(triggered_field, self[field.name] if field else self)
            while True:
                format_values['seq'] = format_values['seq'] + 1
                format_values['prefix2'] = "{:02d}".format(self.date.month)
                sequence = format_string.format(**format_values)
                try:
                    with self.env.cr.savepoint(flush=False), mute_logger('odoo.sql_db'):
                        self[self._sequence_field] = sequence
                        self.flush_recordset([self._sequence_field])
                        break
                except DatabaseError as e:
                    if e.pgcode not in ('23P01', '23505'):
                        raise e
            self._compute_split_sequence()
            self.flush_recordset(['sequence_prefix', 'sequence_number'])
            return True
        return super()._set_next_sequence()

    @api.depends(lambda self: [self._sequence_field])
    def _compute_split_sequence(self):
        test = False

        for record in self:
            if record.move_type == 'out_invoice' and not config['test_enable']:
                test = True
                sequence = record[record._sequence_field] or ''
                regex = re.sub(r"\?P<\w+>", "?:",
                               record._sequence_fixed_regex.replace(r"?P<seq>", ""))
                matching = re.match(regex, sequence)
                if matching: # Condition added by Scalizer
                    record.sequence_prefix = sequence[:matching.start(1)]
                    record.sequence_number = int(matching.group(1) or 0)
        if not test:
            super(AccountMove, self)._compute_split_sequence()
    def _sequence_matches_date(self):
        res = super()._sequence_matches_date()
        if self.move_type == 'out_invoice' and not config['test_enable']:
            sequence = self[self._sequence_field]
            format_values = self._get_sequence_format_param(sequence)[1]
            match = re.match(self._sequence_yearly_regex, sequence or '')
            if match:
                groupdict = match.groupdict()
                if groupdict['prefix2'] != format_values['prefix2']:
                    return False
        return res

    def _get_starting_sequence(self):
        # EXTENDS account sequence.mixin
        self.ensure_one()
        
        if self.move_type == 'out_invoice' and not config['test_enable']:
            starting_sequence = "%04d-%02d-%s000" % (self.date.year, self.date.month, self.journal_id.code)
            return starting_sequence
        return super()._get_starting_sequence()

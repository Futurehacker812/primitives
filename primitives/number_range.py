import six
from functools import total_ordering


class NumberRangeException(Exception):
    pass


class RangeBoundsException(NumberRangeException):
    def __init__(self, lower, upper):
        self.message = 'Min value %d is bigger than max value %d.' % (
            lower,
            upper
        )


@total_ordering
class Range(object):
    def __eq__(self, other):
        try:
            return (
                self.lower == other.lower and
                self.upper == other.upper
            )
        except AttributeError:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        try:
            return self.lower > other.lower and self.upper > other.upper
        except AttributeError:
            return NotImplemented

    def __repr__(self):
        return 'NumberRange(%r, %r)' % (self.lower, self.upper)

    def __str__(self):
        if self.lower != self.upper:
            return '%s - %s' % (self.lower, self.upper)
        return str(self.lower)

    def __add__(self, other):
        try:
            return NumberRange(
                self.lower + other.lower,
                self.upper + other.upper
            )
        except AttributeError:
            return NotImplemented

    def __sub__(self, other):
        try:
            return NumberRange(
                self.lower - other.lower,
                self.upper - other.upper
            )
        except AttributeError:
            return NotImplemented


class NumberRange(Range):
    def __init__(self, *args):
        if len(args) > 2:
            raise NumberRangeException(
                'NumberRange takes at most two arguments'
            )
        elif len(args) == 2:
            lower, upper = args
            if lower > upper:
                raise RangeBoundsException(lower, upper)
            self.lower = lower
            self.upper = upper
            self.lower_inc = self.upper_inc = True
        else:
            if isinstance(args[0], six.integer_types):
                self.lower = self.upper = args[0]
                self.lower_inc = self.upper_inc = True
            elif isinstance(args[0], six.string_types):
                if ',' not in args[0]:
                    self.lower, self.upper = self.parse_range(args[0])
                    self.lower_inc = self.upper_inc = True
                else:
                    self.from_range_with_bounds(args[0])
            elif hasattr(args[0], 'lower') and hasattr(args[0], 'upper'):
                self.lower = args[0].lower
                self.upper = args[0].upper
                if not args[0].lower_inc:
                    self.lower += 1

                if not args[0].upper_inc:
                    self.upper -= 1

    def from_range_with_bounds(self, value):
        """
        Returns new NumberRange object from normalized number range format.

        Example ::

            range = NumberRange.from_normalized_str('[23, 45]')
            range.lower = 23
            range.upper = 45

            range = NumberRange.from_normalized_str('(23, 45]')
            range.lower = 24
            range.upper = 45

            range = NumberRange.from_normalized_str('(23, 45)')
            range.lower = 24
            range.upper = 44
        """
        values = value[1:-1].split(',')
        try:
            lower, upper = map(
                lambda a: int(a.strip()), values
            )
        except ValueError as e:
            raise NumberRangeException(e.message)

        self.lower_inc = value[0] == '('
        if self.lower_inc:
            lower += 1

        self.upper_inc = value[-1] == ')'
        if self.upper_inc:
            upper -= 1

        self.lower = lower
        self.upper = upper

    def parse_range(self, value):
        if value is not None:
            values = value.split('-')
            if len(values) == 1:
                lower = upper = int(value.strip())
            else:
                try:
                    lower, upper = map(
                        lambda a: int(a.strip()), values
                    )
                except ValueError as e:
                    raise NumberRangeException(str(e))
            return lower, upper

    @property
    def normalized(self):
        return '[%s, %s]' % (self.lower, self.upper)

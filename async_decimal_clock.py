""" A pointless, asynchronous clock capable of displaying standard and French decimal time. """
import asyncio
import sys

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import floor

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

@dataclass
class Clock:
    """ Represents a 'ticking' clock. """
    current_time: tuple = ()

    def __str__(self) -> str:
        """ Returns the Clock's current time. """

        try:
            return ":".join([str(n).zfill(2) for n in self.current_time[0:3]])
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError

    async def do_tick(self) -> None:
        """ Wraps the blocking clock tick. """

        try:
            ct = self.tick()
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError
        else:
            self.update(ct)

    def update(self, ct: tuple) -> None:
        """ Updates the current time if it has changed. """

        try:
            if ct != self.current_time:
                self.current_time = ct
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError

    def tick(self) -> tuple:
        """ Computes the current time. """

        try:
            dt = datetime.now()
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError
        else:
            return (dt.hour, dt.minute, dt.second, dt.microsecond)

class DecimalClock(Clock):
    """ Represents a 'ticking' decimal clock. """

    class StandardDay(float, Enum):
        """ One day in standard time units. """
        SECONDS = 86400
        MINUTES = 1440
        HOURS = 24

    class StandardHour(float, Enum):
        """ One hour in standard time units. """
        SECONDS = 3600
        MINUTES = 60
        HOURS = 1

    class StandardMinute(float, Enum):
        """ One minute in standard time units. """
        SECONDS = 60
        MINUTES = 1
        HOURS = 1/60

    class DecimalDay(float, Enum):
        """ One day in decimal time units. """
        SECONDS = 100000
        MINUTES = 10000
        HOURS = 10

    class DecimalHour(float, Enum):
        """ One hour in decimal time units. """
        SECONDS = 10000
        MINUTES = 100
        HOURS = 1

    class DecimalMinute(float, Enum):
        """ One minute in decimal time units. """
        SECONDS = 100
        MINUTES = 1
        HOURS = 0.1

    def __str__(self) -> str:
        """ Returns the DecimalClock's current time. """

        try:
            to_decimal = self.standard_to_decimal(self.current_time)
            s = ":".join([str(n).zfill(2) for n in to_decimal[0:2]])
            s += f":{str(to_decimal[2]).zfill(3)}"
            return s
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError

    def standard_to_seconds(self, dt: tuple) -> float:
        """ Calculates the number of standard seconds since midnight. """

        try:
            hours = float(dt[0]) * self.StandardHour.SECONDS.value
            minutes = float(dt[1]) * self.StandardMinute.SECONDS.value
            seconds = dt[2] + (dt[3]/1000000)
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError
        else:
            return hours + minutes + seconds

    def standard_to_decimal(self, dt: tuple) -> tuple:
        """ Converts standard time to decimal time. """

        try:
            stn_secs = self.standard_to_seconds(dt)                                                 # standard seconds since midnight
            dec_secs = stn_secs * (self.DecimalDay.SECONDS.value / self.StandardDay.SECONDS.value)  # decimal seconds since midnight
            dec_hrs  = floor(dec_secs / self.DecimalDay.MINUTES.value)                              # decimal hours since midnight
            dec_secs = dec_secs - self.DecimalHour.SECONDS.value * dec_hrs                          # decimal seconds since the current decimal hour
            dec_mins = floor(dec_secs / self.DecimalHour.MINUTES)                                   # decimal minutes since the current decimal hour
            dec_secs = floor(dec_secs - self.DecimalMinute.SECONDS.value * dec_mins)                # decimal seconds since the current decimal minute
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise asyncio.CancelledError
        else:
            return (dec_hrs, dec_mins, dec_secs)

async def main():
    """ Main loop function. """

    standard_clock = Clock()
    decimal_clock = DecimalClock()

    try:
        while True:
            standard_tick = asyncio.ensure_future(standard_clock.do_tick())
            decimal_tick = asyncio.ensure_future(decimal_clock.do_tick())
            try:
                await asyncio.shield(standard_tick)
                await asyncio.shield(decimal_tick)
            except (asyncio.CancelledError, KeyboardInterrupt):
                raise asyncio.CancelledError
            else:
                continue
            finally:
                print(f"\rSTANDARD: {str(standard_clock)}    DECIMAL: {str(decimal_clock)} ",end="", flush=True)
    except asyncio.CancelledError:
        await asyncio.sleep(0.2) # give any remaining tasks time to complete

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass
finally:
    sys.exit()

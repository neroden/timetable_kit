#! /usr/bin/env python3
# feed_enhanced.pyi
# Part of timetable_kit
# Copyright 2022, 2023 Nathanael Nerode.  Licensed under GNU Affero GPL v.3 or later.

from __future__ import annotations

from typing import Optional, Type, Any

from gtfs_kit import Feed
from pandas import DataFrame, Series

GTFS_DAYS: tuple[str, str, str, str, str, str, str]

class FeedEnhanced(Feed):
    dist_units: str
    agency: Optional[DataFrame] = None
    stops: Optional[DataFrame] = None
    routes: Optional[DataFrame] = None
    trips: Optional[DataFrame] = None
    stop_times: Optional[DataFrame] = None
    calendar: Optional[DataFrame] = None
    calendar_dates: Optional[DataFrame] = None
    fare_attributes: Optional[DataFrame] = None
    fare_rules: Optional[DataFrame] = None
    shapes: Optional[DataFrame] = None
    frequencies: Optional[DataFrame] = None
    transfers: Optional[DataFrame] = None
    feed_info: Optional[DataFrame] = None
    attributions: Optional[DataFrame] = None

    @classmethod
    def enhance(cls: Type[FeedEnhanced], regular_feed: Feed) -> FeedEnhanced: ...
    def copy(self) -> FeedEnhanced: ...
    def filter_by_dates(self: FeedEnhanced, first_date, last_date) -> FeedEnhanced: ...
    def filter_by_day_of_week(self: FeedEnhanced, day: str) -> FeedEnhanced: ...
    def filter_by_days_of_week(self: FeedEnhanced, days: list[str]) -> FeedEnhanced: ...
    def filter_by_route_ids(self: FeedEnhanced, route_ids) -> FeedEnhanced: ...
    def filter_by_service_ids(self: FeedEnhanced, service_ids) -> FeedEnhanced: ...
    def filter_bad_service_ids(self: FeedEnhanced, bad_service_ids) -> FeedEnhanced: ...
    def filter_remove_one_day_calendars(self: FeedEnhanced) -> FeedEnhanced: ...
    def filter_find_one_day_calendars(self: FeedEnhanced) -> FeedEnhanced: ...
    def filter_by_trip_short_names(
        self: FeedEnhanced, trip_short_names
    ) -> FeedEnhanced: ...
    def filter_by_trip_ids(self: FeedEnhanced, trip_ids) -> FeedEnhanced: ...

    def get_single_trip(self: FeedEnhanced) -> Series: ...
    def get_single_trip_stop_times(self: FeedEnhanced, trip_id) -> DataFrame: ...
    def get_trip_short_name(self: FeedEnhanced, trip_id) -> str: ...

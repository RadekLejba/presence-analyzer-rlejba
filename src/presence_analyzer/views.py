# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort, url_for
from flask.ext.mako import render_template
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    get_months,
    mean,
    group_by_weekday,
    group_by_start_end,
    group_by_months,
    get_xml_data,
    sum_of_specific_month
)

import locale
import logging
import heapq
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('pages', page="presence_start_end.html"))


@app.route('/<page>')
def pages(page):
    """
    Renders templates.
    """
    try:
        return render_template(page, page=page)
    except TopLevelLookupException:
        return render_template('404.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    locale.setlocale(locale.LC_COLLATE, 'pl_PL.UTF-8')
    data = get_xml_data()
    data = [
        {'user_id': key, 'name': value['user_name']}
        for key, value in data.iteritems()
    ]
    sorted_data = sorted(
        data,
        key=lambda x: x['name'],
        cmp=locale.strcoll,
    )
    return sorted_data


@app.route('/api/v1/months', methods=['GET'])
@jsonify
def month_view():
    """
    Month listing for dropdown.
    """
    data = get_months()
    data = [
        {'month': data.index(item), 'date': item}
        for item in data
    ]
    return data


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@jsonify
def avatar_view(user_id):
    """
    Returns adress of user avatar.
    """
    data = get_xml_data()
    return data[str(user_id)]['avatar']


@app.route('/api/v1/workers_of_the_month/<string:month>', methods=['GET'])
@jsonify
def workers_of_the_month_view(month):
    """
    Returns 5 workers with most worked hours in given month.
    If result<5 then empy indexes are filled with ['nouser', 0].
    """
    result = []
    month = month.encode('utf-8')
    months = get_months()
    data = get_data()
    xml_data = get_xml_data()

    if month not in months:
        return 0

    for key in xml_data.keys():
        try:
            result.append([xml_data[key]['user_name'], sum_of_specific_month(data[int(key)], month)])
        except KeyError:
            continue
    result = heapq.nlargest(5, result, key=lambda e:e[1])

    if len(result) <5:
        for i in range(5 - len(result)):
            result.append(['nouser', 0])
    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        return 0

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        return 0

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean presence time of given
    user grouped by weekday and start/end hour.
    """
    data = get_data()
    if user_id not in data:
        return 0

    weekdays = group_by_start_end(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(start_end[0]), mean(start_end[1]))
        for weekday, start_end in enumerate(weekdays)
    ]
    return result


@app.route('/api/v1/monthly_presence/<int:user_id>', methods=['GET'])
@jsonify
def monthly_presence_view(user_id):
    """
    Returns monthly presence from the start of work.

    The result is grouped like this:
    result = [
        ['2013.03', 23553]
        ['2013.04', 29928]
        ['2013.06', 44211]
    ]
    """
    data = get_data()
    if user_id not in data:
        return 0

    months = group_by_months(data[user_id])
    result = [
        [month, value] for (month, value) in months.items()
    ]
    result.sort()
    result.insert(0, ('Month', 'Presence (s)'))

    return result

# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 CERN.
#
# invenio-app-ils is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest fixtures and plugins for the API application."""

from __future__ import absolute_import, print_function

import pytest
from invenio_app.factory import create_api
from invenio_circulation.api import Loan
from invenio_circulation.pidstore.pids import CIRCULATION_LOAN_PID_TYPE
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search

from invenio_app_ils.circulation.receivers import index_item_after_loan_change
from invenio_app_ils.records.api import Document, InternalLocation, Item, \
    Location

from ..helpers import load_json_from_datadir
from .helpers import mint_record_pid

from invenio_app_ils.pidstore.pids import (  # isort:skip
    DOCUMENT_PID_TYPE,
    INTERNAL_LOCATION_PID_TYPE,
    ITEM_PID_TYPE,
    LOCATION_PID_TYPE
)


@pytest.fixture(scope='module')
def create_app():
    """Create test app."""
    return create_api


@pytest.fixture()
def json_headers():
    """JSON headers."""
    return [('Content-Type', 'application/json'),
            ('Accept', 'application/json')]


@pytest.fixture()
def json_patch_headers():
    """JSON headers for Invenio Records REST PATCH api calls."""
    return [('Content-Type', 'application/json-patch+json'),
            ('Accept', 'application/json')]


@pytest.fixture()
def testdata(app, db, es_clear):
    """Create, index and return test data."""
    indexer = RecordIndexer()

    locations = load_json_from_datadir('locations.json')
    for location in locations:
        record = Location.create(location)
        mint_record_pid(LOCATION_PID_TYPE, Location.pid_field, record)
        record.commit()
        db.session.commit()
        indexer.index(record)

    internal_locations = load_json_from_datadir('internal_locations.json')
    for internal_location in internal_locations:
        record = InternalLocation.create(internal_location)
        mint_record_pid(INTERNAL_LOCATION_PID_TYPE, InternalLocation.pid_field,
                        record)
        record.commit()
        db.session.commit()
        indexer.index(record)

    documents = load_json_from_datadir('documents.json')
    for doc in documents:
        record = Document.create(doc)
        mint_record_pid(DOCUMENT_PID_TYPE, Document.pid_field, record)
        record.commit()
        db.session.commit()
        indexer.index(record)

    items = load_json_from_datadir('items.json')
    for item in items:
        record = Item.create(item)
        mint_record_pid(ITEM_PID_TYPE, Item.pid_field, record)
        record.commit()
        db.session.commit()
        indexer.index(record)

    loans = load_json_from_datadir('loans.json')
    for loan in loans:
        record = Loan.create(loan)
        mint_record_pid(CIRCULATION_LOAN_PID_TYPE, Loan.pid_field, record)
        record.commit()
        db.session.commit()
        indexer.index(record)
        # re-index item attached to the loan
        index_item_after_loan_change(app, record)

    # flush all indices after indexing, otherwise ES won't be ready for tests
    current_search.flush_and_refresh(index=None)

    return {
        'locations': locations,
        'documents': documents,
        'items': items,
        'loans': loans
    }
from datetime import datetime, timedelta

import pytest

from app.database.requests import db


@pytest.mark.asyncio
async def test_add_user():
    await db.add_user(1, 'GGG', 'wefa')
    await db.add_user(2, 'FAFA', 'fa')


@pytest.mark.asyncio
async def test_add_used_generation():
    await db.add_used_and_daily_generation(1)


@pytest.mark.asyncio
async def test_subscribe_user():
    await db.subscribe_user(2, subscription_end_date=datetime.now() + timedelta(days=7))


@pytest.mark.asyncio
async def test_add_payment():
    await db.add_payment(user_id=1, purchase_amount=179, subscription_end_date=datetime.now() + timedelta(days=7))
    await db.add_payment(user_id=1, purchase_amount=279, subscription_end_date=datetime.now() + timedelta(days=14))
    await db.add_payment(user_id=2, purchase_amount=379, subscription_end_date=datetime.now() + timedelta(days=31))


@pytest.mark.asyncio
async def test_get_user_data():
    res = await db.get_user_data(user_id=1)
    assert res == {'id': 1, 'name': 'GGG', 'username': 'wefa', 'used_generations': 1,
                   'subscription_end_date': res['subscription_end_date'],
                   'datetime_registration': res['datetime_registration'],
                   'daily_generation': 1}


@pytest.mark.asyncio
async def test_get_payments():
    res = await db.get_payments_of_user(user_id=1)
    assert len(res) == 2



@pytest.mark.asyncio
async def test_remove_user():
    await db.remove_user(1)

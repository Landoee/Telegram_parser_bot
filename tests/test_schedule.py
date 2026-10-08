import unittest
import os
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from aiogram.types import Message, Chat
# Импорт моделей создаёт engine, но тесты не подключаются к БД.
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://test:test@localhost/test')
from src.services.parser import (Group, INSTITUTES, ScheduleError, parse_schedule,
                                 resolve_group, matches_date, _fetch)
from src.handlers.schedule import show_schedule, render_schedule

HTML = (Path(__file__).parent / 'fixtures/ki26_01.html').read_text()


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.schedule = parse_schedule(HTML, 'КИ26-01 (1 подгруппа)', date(2026, 10, 8))

    def test_real_thursday(self):
        lessons = self.schedule.for_day(date(2026, 10, 8))
        self.assertEqual(len(lessons), 4)
        self.assertEqual(lessons[0].time, '08:30-10:05')
        self.assertIn('Аналитическая геометрия', lessons[0].text)
        self.assertIn('Кириллов К. А.', lessons[0].text)
        self.assertIn('ауд. 1-16', lessons[0].text)

    def test_parity_and_single_date(self):
        even = self.schedule.for_day(date(2026, 10, 5))
        odd = self.schedule.for_day(date(2026, 10, 12))
        self.assertEqual([x.number for x in even], ['3', '4', '5'])
        self.assertEqual([x.number for x in odd], ['2', '3', '4', '5'])
        self.assertTrue(matches_date('только 07.09. 2026 г.', date(2026, 9, 7)))
        self.assertFalse(matches_date('только 07.09. 2026 г.', date(2026, 10, 5)))
        self.assertEqual(self.schedule.for_day(date(2026, 10, 11)), [])

    def test_invalid_page_is_not_empty_day(self):
        with self.assertRaises(ScheduleError):
            parse_schedule('<html>Ошибка сервера</html>', 'КИ26-01', date.today())

    def test_group_resolution(self):
        groups = [Group(n, INSTITUTES['IKIT'], 1) for n in
                  ['КИ26-01 (1 подгруппа)', 'КИ26-01 (2 подгруппа)', 'КИ26-01Б (1 подгруппа)']]
        self.assertEqual(resolve_group(groups, 'ки26-01', 'IKIT', 1, 2), groups[1].name)
        with self.assertRaises(ScheduleError):
            resolve_group(groups, '01', 'IKIT', 1, 1)
        with self.assertRaises(ScheduleError):
            resolve_group(groups, 'КИ26-01', 'IKIT', 2, 1)

    def test_long_week(self):
        self.schedule.lessons *= 30
        chunks = render_schedule(self.schedule, 'week')
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(x) <= 3500 for x in chunks))

    def test_timeout(self):
        import requests
        with patch('src.services.parser.requests.get', side_effect=requests.Timeout):
            with self.assertRaises(ScheduleError):
                _fetch()


class HandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_today_button(self):
        message = Message(message_id=1, date=0, chat=Chat(id=42, type='private'), text='Меню')
        callback = SimpleNamespace(answer=AsyncMock(), message=message,
                                   from_user=SimpleNamespace(id=42), data='schedule:today')
        student = SimpleNamespace(group_name='КИ26-01', uni_name='IKIT', course=1, subgroup_number=1)
        session = SimpleNamespace(get=AsyncMock(return_value=student))
        schedule = parse_schedule(HTML, 'КИ26-01', date(2026, 10, 8))
        with patch('src.handlers.schedule.get_schedule', AsyncMock(return_value=schedule)) as fetch, \
             patch.object(Message, 'edit_text', AsyncMock()) as edit:
            await show_schedule(callback, session)
            callback.answer.assert_awaited_once()
            fetch.assert_awaited_once_with('КИ26-01', 'IKIT', 1, 1)
            edit.assert_awaited_once()
            self.assertIn('КИ26-01', edit.call_args.args[0])

    async def test_unregistered(self):
        message = Message(message_id=1, date=0, chat=Chat(id=42, type='private'))
        callback = SimpleNamespace(answer=AsyncMock(), message=message, from_user=SimpleNamespace(id=42))
        with patch.object(Message, 'answer', AsyncMock()) as answer:
            await show_schedule(callback, SimpleNamespace(get=AsyncMock(return_value=None)))
            self.assertIn('/registration', answer.call_args.args[0])

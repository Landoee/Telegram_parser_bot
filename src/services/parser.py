"""HTML-каталог и расписание edu.sfu-kras.ru (без браузера)."""
import asyncio
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

URL = "https://edu.sfu-kras.ru/timetable"
TZ = ZoneInfo("Asia/Krasnoyarsk")
DAYS = ("Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье")
INSTITUTES = dict(zip(
    ("Voen", "Guman", "ISI", "IAD", "IIFIR", "IKIT", "IMIFI", "INiG", "IPPS", "ITSUs", "IUBP", "IFKST", "IFIYK", "IFBB", "ICMM", "IEG", "IUGIF", "Poly", "PONOP", "UrI"),
    ("Военно-инженерный институт", "Гуманитарный институт", "Инженерно-строительный институт", "Институт архитектуры и дизайна", "Институт инженерной физики и радиоэлектроники", "Институт космических и информационных технологий", "Институт математики и фундаментальной информатики", "Институт нефти и газа", "Институт педагогики, психологии и социологии", "Институт торговли и сферы услуг", "Институт управления бизнес-процессами", "Институт физической культуры, спорта и туризма", "Институт филологии и языковой коммуникации", "Институт фундаментальной биологии и биотехнологии", "Институт цветных металлов и материаловедения", "Институт экологии и географии", "Институт экономики, государственного управления и финансов", "Политехнический институт", "Проектный офис новых образовательных практик", "Юридический институт"),
))


class ScheduleError(Exception):
    """Ошибка источника или выбора группы, которую можно показать студенту."""


def clean(text: str) -> str:
    return " ".join(text.split())


@dataclass(frozen=True)
class Group:
    name: str
    institute: str
    course: int


@dataclass(frozen=True)
class Lesson:
    weekday: int
    number: str
    time: str
    text: str
    parity: int | None  # 0 — чётная, 1 — нечётная, None — обе


@dataclass
class Schedule:
    group: str
    lessons: list[Lesson]
    current_parity: int
    fetched_on: date

    def for_day(self, day: date) -> list[Lesson]:
        monday = self.fetched_on - timedelta(days=self.fetched_on.weekday())
        parity = (self.current_parity + (day - monday).days // 7) % 2
        return [lesson for lesson in self.lessons
                if lesson.weekday == day.weekday()
                and lesson.parity in (None, parity)
                and matches_date(lesson.text, day)]


def matches_date(text: str, day: date) -> bool:
    # Явные разовые занятия встречаются прямо в поле аудитории.
    match = re.search(r"только\s+(\d{1,2})\.(\d{1,2})\.\s*(\d{4})", text, re.I)
    if match:
        d, m, y = map(int, match.groups())
        return (day.day, day.month, day.year) == (d, m, y)
    return True


def parse_catalog(html: str) -> list[Group]:
    soup = BeautifulSoup(html, "html.parser")
    groups = []
    for link in soup.select('#groups a[href^="?group="]'):
        titles = []
        for parent in link.parents:
            if "collapsed-block" in parent.get("class", []):
                title = parent.select_one(':scope > a > .trigger-title')
                if title:
                    titles.append(clean(title.get_text()))
        course = next((re.match(r"(\d+)\s+курс", t) for t in titles if re.match(r"(\d+)\s+курс", t)), None)
        institute = next((t for t in titles if t in INSTITUTES.values()), "")
        name = parse_qs(urlsplit(link['href']).query).get('group', [''])[0]
        if name and course and institute:
            groups.append(Group(clean(name), institute, int(course[1])))
    if not groups:
        raise ScheduleError("Не удалось прочитать каталог групп СФУ. Попробуй позже.")
    return groups


def resolve_group(groups: list[Group], name: str, institute: str, course: int | None, subgroup: int | None) -> str:
    name = clean(name).casefold()
    candidates = []
    for group in groups:
        if group.institute != INSTITUTES.get(institute, institute) or group.course != course:
            continue
        full = group.name.casefold()
        base = re.sub(r"\s*\(\d+\s+подгруппа\)", "", full).strip()
        sg = re.search(r"\((\d+)\s+подгруппа\)", full)
        if sg and int(sg[1]) != subgroup:
            continue
        number = re.search(r"-(\d+)", base)
        if name in (full, base) or (name.isdigit() and number and int(name) == int(number[1])):
            candidates.append(group.name)
    candidates = sorted(set(candidates))
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        raise ScheduleError("Номер группы неоднозначен. Через /registration введи полное название с сайта:\n" + "\n".join(candidates[:12]))
    raise ScheduleError("Группа не найдена. Проверь институт, курс и полное название группы через /registration.")


def parse_schedule(html: str, group: str, fetched_on: date) -> Schedule:
    soup = BeautifulSoup(html, "html.parser")
    parity_match = re.search(r"Ид[её]т\s+(неч[её]тная|ч[её]тная)\s+неделя", soup.get_text(' ', strip=True), re.I)
    tables = soup.select('table.timetable')
    if not tables or not parity_match:
        raise ScheduleError("СФУ не вернул таблицу расписания или чётность недели. Попробуй позже.")
    lessons = []
    seen_day = False
    for table in tables:
        weekday = None
        for row in table.select('tr'):
            heading = row.select_one('th')
            if heading and clean(heading.get_text()) in DAYS:
                weekday = DAYS.index(clean(heading.get_text()))
                seen_day = True
                continue
            cells = row.find_all('td', recursive=False)
            if not cells:
                continue
            if weekday is None or len(cells) not in (3, 4) or any(c.get('rowspan', '1') != '1' for c in cells):
                raise ScheduleError("Структура таблицы СФУ изменилась. Проверь расписание на сайте.")
            if len(cells) == 3 and cells[2].get('colspan') != '2':
                raise ScheduleError("Не удалось определить чётность занятия.")
            for index, cell in enumerate(cells[2:]):
                for br in cell.find_all('br'):
                    br.replace_with('\n')
                text = '\n'.join(clean(line) for line in cell.get_text().splitlines() if clean(line))
                if text:
                    lessons.append(Lesson(weekday, clean(cells[0].text), clean(cells[1].text), text, None if len(cells) == 3 else (1 if index == 0 else 0)))
    if not seen_day:
        raise ScheduleError("Таблица расписания пуста. Уточни расписание на сайте СФУ.")
    return Schedule(group, lessons, int(parity_match[1].lower().startswith('не')), fetched_on)


def _fetch(params=None) -> str:
    try:
        response = requests.get(URL, params=params, timeout=(5, 25), headers={"User-Agent": "SFU-Schedule-Bot/0.1"})
        response.raise_for_status()
        return response.content.decode('utf-8', errors='replace')
    except requests.exceptions.SSLError:
        # Системный curl может использовать доверенные сертификаты ОС,
        # отсутствующие в Python/certifi. Проверка TLS остаётся включённой.
        url = requests.Request('GET', URL, params=params).prepare().url
        try:
            result = subprocess.run(
                ['curl', '--fail', '--silent', '--show-error', '--location',
                 '--proto', '=https', '--proto-redir', '=https',
                 '--connect-timeout', '5', '--max-time', '30', url],
                capture_output=True, check=True, timeout=35,
            )
            return result.stdout.decode('utf-8', errors='replace')
        except (OSError, subprocess.SubprocessError) as fallback_exc:
            raise ScheduleError('Не удалось установить HTTPS-соединение с СФУ. Проверь сертификаты системы.') from fallback_exc
    except requests.RequestException as exc:
        raise ScheduleError("Сайт расписания СФУ недоступен. Попробуй ещё раз позже.") from exc


def _load(group: str, institute: str, course: int | None, subgroup: int | None) -> Schedule:
    name = resolve_group(parse_catalog(_fetch()), group, institute, course, subgroup)
    return parse_schedule(_fetch({'group': name}), name, datetime.now(TZ).date())


async def get_schedule(group: str, institute: str, course: int | None, subgroup: int | None) -> Schedule:
    # requests и разбор большого каталога не блокируют цикл aiogram.
    return await asyncio.to_thread(_load, group, institute, course, subgroup)


if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('group')
    cli.add_argument('--institute', default='IKIT')
    cli.add_argument('--course', type=int, default=1)
    cli.add_argument('--subgroup', type=int, default=1)
    cli.add_argument('--date', type=date.fromisoformat, default=datetime.now(TZ).date())
    args = cli.parse_args()
    result = asyncio.run(get_schedule(args.group, args.institute, args.course, args.subgroup))
    print(result.group, args.date)
    for item in result.for_day(args.date):
        print(item.time, item.text, sep='\n')
    if not result.for_day(args.date):
        print('Занятий нет.')

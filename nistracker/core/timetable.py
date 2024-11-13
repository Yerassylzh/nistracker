import asyncio
from datetime import datetime, timedelta
import requests


class TimeTable:     
    @staticmethod
    def get_datefrom() -> str:
        datefrom = datetime.now()
        while datefrom.weekday() != 0:
            datefrom -= timedelta(days=1)
        return datefrom.strftime('%Y-%m-%d')

    @staticmethod
    def get_dateto() -> str:
        dateto = datetime.now()
        while dateto.weekday() != 6:
            dateto += timedelta(days=1)
        return dateto.strftime('%Y-%m-%d')
    
    @staticmethod
    async def get_ids() -> dict[dict]:
        teacher_to_id = dict()
        id_to_teacher = dict()

        subject_to_id = dict()
        id_to_subject = dict()

        classroom_to_id = dict()
        id_to_classroom = dict()

        grade_to_id = dict()
        id_to_grade = dict()
        
        time_periods : list[tuple] = list()

        payload = {
            '__args': [
                'null',
                str(datetime.now().year),
                {
                    'vt_filter': { 
                        'datefrom': TimeTable.get_datefrom(), 'dateto': TimeTable.get_dateto() 
                    }
                },
                {
                    'op': 'fetch',
                    'needed_combos': {},
                    'needed_part': {
                        'classes': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "classroomid"],
                        'classrooms': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "name", "short"],
                        'dates': ["tt_num", "tt_day"],
                        'dayparts': ["starttime", "endtime"],
                        'dayparts': ["starttime", "endtime"],
                        'event_types': ["name", "icon"],
                        'events': ["typ", "name"],
                        'igroups': ["short", "name", "firstname", "lastname", "callname", "subname", "code"],
                        'periods': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "period", "starttime", "endtime"],
                        'students': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "classid"],
                        'subjects': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "name", "short"],
                        'subst_absent': ["date", "absent_typeid", "groupname"],
                        'teachers': ["short", "name", "firstname", "lastname", "callname", "subname", "code", "cb_hidden", "expired", "firstname", "lastname", "short"]
                    }
                }
            ],
            '__gsh': "0" * 8
        }

        with requests.Session() as s:
            url = 'https://nistaldykorgan.edupage.org/rpr/server/maindbi.js?__func=mainDBIAccessor'
            r = await asyncio.to_thread(s.post, url=url, json=payload)
            data = r.json()

        for teacher_data in data['r']['tables'][0]['data_rows']:
            teacher_to_id[teacher_data['short']] = teacher_data['id']
            id_to_teacher[teacher_data['id']] = teacher_data['short']
        
        for subject_data in data['r']['tables'][1]['data_rows']:
            subject_to_id[subject_data['short']] = subject_data['id']
            id_to_subject[subject_data['id']] = subject_data['short']
        
        for classroom_data in data['r']['tables'][2]['data_rows']:
            classroom_to_id[classroom_data['short']] = classroom_data['id']
            id_to_classroom[classroom_data['id']] = classroom_data['short']
        
        for grade_data in data['r']['tables'][3]['data_rows']:
            grade_to_id[grade_data['short']] = grade_data['id']
            id_to_grade[grade_data['id']] = grade_data['short']

        for period_data in data['r']['tables'][6]['data_rows']:
            starttime = datetime.strptime(period_data['starttime'], '%H:%M')
            starttime = (starttime.hour, starttime.minute)

            endtime = datetime.strptime(period_data['endtime'], '%H:%M')
            endtime = (endtime.hour, endtime.minute)
            
            time_periods.append((starttime, endtime))

        return {
            'teacher_to_id': teacher_to_id,
            'id_to_teacher': id_to_teacher,
            'subject_to_id': subject_to_id,
            'id_to_subject': id_to_subject,
            'classroom_to_id': classroom_to_id,
            'id_to_classroom': id_to_classroom,
            'grade_to_id': grade_to_id,
            'id_to_grade': id_to_grade
        }

    @staticmethod
    async def get_tt_from_id(target_id: int) -> dict:
        # see tt_example.json for understanding
        timetable : list[list[list[list]]]= [[] for _ in range(5)]              
        
        with requests.Session() as s:
            s.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            })
            url = 'https://nistaldykorgan.edupage.org/timetable/server/currenttt.js?__func=curentttGetData'
            payload = {
                '__args': [
                    'null',
                    {
                        'datefrom': TimeTable.get_datefrom(),
                        'dateto': TimeTable.get_dateto(),
                        'id': target_id,
                        'log_module': 'CurrentTTView',
                        'showColors': True,
                        'showIgroupsInClasses': False,
                        'showOrig': True,
                        'table': "classes",
                        'year': datetime.now().year
                    }
                ],
                '__gsh': '0' * 8
            }
            r = await asyncio.to_thread(s.post, url=url, json=payload)

        datefrom = datetime.strptime(TimeTable.get_datefrom(), '%Y-%m-%d')
        data = r.json()
        for subject_data in data['r']['ttitems']:
            day_num = (datetime.strptime(subject_data['date'], '%Y-%m-%d') - datefrom).days
            times = [subject_data['starttime'], subject_data['endtime']]

            starttime = datetime.strptime(times[0], '%H:%M')
            starttime = (starttime.hour, starttime.minute)

            endtime = datetime.strptime(times[1], '%H:%M')
            endtime = (endtime.hour, endtime.minute)

            if day_num < 0 or day_num > 4:
                continue

            if len(timetable[day_num]) == 0 or (timetable[day_num][-1][0], timetable[day_num][-1][1]) != (starttime, endtime):
                timetable[day_num].append([starttime, endtime, []])
            
            timetable[day_num][-1][-1].append(subject_data)

        for day_tt in timetable:
            for subject in day_tt:
                subject[-1].sort(key=lambda x: x['groupnames'])

        return {
            'tt': timetable
        }

    '''
        Options for "v_type" argument:
          1. "g" = grade
          2. "s" = subject
          3. "t" = teacher
          4. "c" = classroom
        "Exception" instance will be raised if "v_type" argument is invalid.
    '''
    @staticmethod
    async def get_tt_from_value(value: str, v_type: str) -> dict:
        ids = await TimeTable.get_ids()

        target_id = None
        if v_type == "g":
            target_id = ids["grade_to_id"][value]
        elif v_type == "s":
            target_id = ids["subject_to_id"][value]
        elif v_type == "t":
            target_id = ids["teacher_to_id"][value]
        elif v_type == "c":
            target_id = ids["classroom_to_id"][value]
        else:
            raise Exception(
                f"Cannot load time table from invalid 'v_type' argument: {v_type}"
            )

        return await TimeTable.get_tt_from_id(target_id)


tests = [
    {'intervals': {'lesson': [1594663200, 1594666800],
             'pupil': [1594663340, 1594663389, 1594663390, 1594663395, 1594663396, 1594666472],
             'tutor': [1594663290, 1594663430, 1594663443, 1594666473]},
     'answer': 3117
    },
    {'intervals': {'lesson': [1594702800, 1594706400],
             'pupil': [1594702789, 1594704500, 1594702807, 1594704542, 1594704512, 1594704513, 1594704564, 1594705150, 1594704581, 1594704582, 1594704734, 1594705009, 1594705095, 1594705096, 1594705106, 1594706480, 1594705158, 1594705773, 1594705849, 1594706480, 1594706500, 1594706875, 1594706502, 1594706503, 1594706524, 1594706524, 1594706579, 1594706641],
             'tutor': [1594700035, 1594700364, 1594702749, 1594705148, 1594705149, 1594706463]},
    'answer': 3577
    },
    {'intervals': {'lesson': [1594692000, 1594695600],
             'pupil': [1594692033, 1594696347],
             'tutor': [1594692017, 1594692066, 1594692068, 1594696341]},
    'answer': 3565
    },
]


def get_person_intervals_in_lesson(person_intervals: list, lesson_start: int, lesson_end: int) -> list:
    """ Фильтрует и обрезает интервалы ученика/учителя, возвращая только те, которые были во время урока.
        Не копируется person_intervals, так как в коде исходный массив не меняется, а создается новый,
        но для полной надежности можно и скопировать
    """

    person_intervals_in_lesson = []
    for index in range(0, len(person_intervals), 2):
        person_entry = person_intervals[index]
        person_exit = person_intervals[index + 1]

        entry_in_lesson = lesson_start <= person_entry <= lesson_end  # вход во время урока
        exit_in_lesson = lesson_start <= person_exit <= lesson_end  # выход во время урока
        full_lesson = person_entry <= lesson_start and person_exit >= lesson_end  # весь урок

        if entry_in_lesson or exit_in_lesson or full_lesson:
            # обрезаем интервал по времени урока
            person_entry = max(person_entry, lesson_start)
            person_exit = min(person_exit, lesson_end)
            person_intervals_in_lesson.extend([person_entry, person_exit])

    return person_intervals_in_lesson


def merge_person_intervals(intervals: list) -> list:
    """ Слияние интервалов ученика/учителя, чтобы избежать перекрытия и двойного подсчета секунд
        Проходим по парам (вход, выход), если есть пересечения интервалов, то объединяем в 1
    """

    intervals_pairs = [(intervals[index_elem], intervals[index_elem + 1]) for index_elem in range(0, len(intervals), 2)]
    intervals_pairs = sorted(intervals_pairs)
    merged_intervals = []

    for current_interval in intervals_pairs:
        merged = False

        # проход по уже соединенным интервалом с проверкой, чтобы точно все интервалы объеденились при пересечении
        for index in range(len(merged_intervals)):
            merged_interval = merged_intervals[index]

            # Проверка на пересечение интервалов
            if not (current_interval[1] < merged_interval[0] or current_interval[0] > merged_interval[1]):
                start = min(current_interval[0], merged_interval[0])
                end = max(current_interval[1], merged_interval[1])
                merged_intervals[index] = (start, end)
                merged = True
                break

        if not merged:
            merged_intervals.append(current_interval)

    merged_list = []
    for interval in merged_intervals:
        for endpoint in interval:
            merged_list.append(endpoint)
    return merged_list


def calculate_total_time_in_lesson(pupil_merged_intervals: list, tutor_merged_intervals: list) -> int:
    """ Вычисляет пересечение времени между учителем и учеником.
        Данные уже чистые (включают в себя скомпилированные временные отрезки только во время урока)
    """

    total_seconds = 0
    for outer in range(0, len(pupil_merged_intervals), 2):
        pupil_entry = pupil_merged_intervals[outer]
        pupil_exit = pupil_merged_intervals[outer + 1]

        for inner in range(0, len(tutor_merged_intervals), 2):
            tutor_entry = tutor_merged_intervals[inner]
            tutor_exit = tutor_merged_intervals[inner + 1]

            entry_intersection = max(pupil_entry, tutor_entry)
            exit_intersection = min(pupil_exit, tutor_exit)

            if entry_intersection < exit_intersection:
                overlap_time = exit_intersection - entry_intersection
                total_seconds += overlap_time

    return total_seconds


def appearance(intervals: dict[str, list[int]]) -> int:
    """ Обработка данных из словаря для вычисления пересечения времени ученика и учителя
        Сразу возвращает 0, если
            - Нет данных у кого-либо о сессиях (отсутствуют интервалы)
            - Кто-то из участников не было на уроке совсем (интервалы вне урока)
    """

    lesson_time_interval = intervals.get('lesson')
    lesson_start = lesson_time_interval[0]
    lesson_end = lesson_time_interval[1]

    pupil_intervals = intervals.get('pupil')
    tutor_intervals = intervals.get('tutor')
    # если вообще не пришли данные о входе ученика/учителя
    if pupil_intervals is None or tutor_intervals is None:
        return 0

    # фильтрация интервалов, если ученик/учитель не был на уроке вообще, то смысла проверять дальше нет, будет 0
    pupil_intervals_in_lesson = get_person_intervals_in_lesson(pupil_intervals, lesson_start, lesson_end)
    tutor_intervals_in_lesson = get_person_intervals_in_lesson(tutor_intervals, lesson_start, lesson_end)

    if not pupil_intervals_in_lesson or not tutor_intervals_in_lesson:
        return 0

    # слияние интервалов для ученика и учителя
    pupil_merged_intervals = merge_person_intervals(pupil_intervals_in_lesson)
    tutor_merged_intervals = merge_person_intervals(tutor_intervals_in_lesson)

    total_seconds = calculate_total_time_in_lesson(pupil_merged_intervals, tutor_merged_intervals)
    return total_seconds


if __name__ == '__main__':
    for i, test in enumerate(tests):
        test_answer = appearance(test['intervals'])
        assert test_answer == test['answer'], f'Error on test case {i}, got {test_answer}, expected {test["answer"]}'

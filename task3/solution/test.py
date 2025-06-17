import unittest

from solution import *


class TestAppearance(unittest.TestCase):

    def test_all_data_valid(self):
        """ Все данные валидны и есть пересечение времени на уроке у ученика и учителя """

        for _, test_data in enumerate(tests):
            result = appearance(test_data['intervals'])
            self.assertEqual(result, test_data['answer'])

    def test_no_data_time(self):
        """ Нет данных о сессиях у ученика/учителя (pupil или tutor пустые) """

        test_data1 = {'lesson': [1594663200, 1594666800],
                      'pupil': [1594663202, 1594666800],
                      'tutor': []
                      }

        test_data2 = {'lesson': [1594663200, 1594666800],
                      'pupil': [],
                      'tutor': [1594663202, 1594666800]
                      }

        result1 = appearance(test_data1)
        result2 = appearance(test_data2)

        self.assertEqual(result1, 0)
        self.assertEqual(result2, 0)

    def test_not_in_lesson(self):
        """ Ученик или учитель не присутствовал на уроке (интервалы вне урока) """

        test_data1 = {'lesson': [1594663200, 1594666800],
                      'pupil': [1594663179, 1594663199],
                      'tutor': [1594663200, 1594666800]
                      }

        test_data2 = {'lesson': [1594663200, 1594666800],
                      'pupil': [1594663200, 1594666800],
                      'tutor': [1594663179, 1594663199]
                      }

        result1 = appearance(test_data1)
        result2 = appearance(test_data2)

        self.assertEqual(result1, 0)
        self.assertEqual(result2, 0)


class TestGetPersonIntervalsInLesson(unittest.TestCase):

    def test_all_intervals_in_lesson(self):
        """ Все интервалы внутри урока без выхода за время.
            Интервалы только внутри самого урока
        """

        test_data = {'lesson': [1594663200, 1594666800],
                     'pupil': [1594663200, 1594666800],  # пограничный случай
                     'tutor': [1594663201, 1594666799]  # полностью внутри урока
                     }
        result_pupil = get_person_intervals_in_lesson(test_data['pupil'],
                                                      test_data['lesson'][0],
                                                      test_data['lesson'][1])
        result_tutor = get_person_intervals_in_lesson(test_data['tutor'],
                                                      test_data['lesson'][0],
                                                      test_data['lesson'][1])

        self.assertEqual(result_pupil, test_data['pupil'])
        self.assertEqual(result_tutor, test_data['tutor'])

    def test_different_intervals(self):
        """ Проверяет, что интервалы правильно фильтруются
            (остаются только интервалы, которые затрагивают время урока).
            И проверяет, что интервалы правильно обрезаются, оставляя только то время,
            которое относится к уроку
        """

        test_data = {'lesson': [1594663200, 1594666800],
                     # все интервалы вне урока
                     'pupil': [1594663189, 1594663199],
                     # интервалы задевают урок и их нужно обрезать
                     'tutor': [1594663189, 1594663206, 1594666700, 1594666850]
                     }
        result_pupil = get_person_intervals_in_lesson(test_data['pupil'],
                                                      test_data['lesson'][0],
                                                      test_data['lesson'][1])
        result_tutor = get_person_intervals_in_lesson(test_data['tutor'],
                                                      test_data['lesson'][0],
                                                      test_data['lesson'][1])

        self.assertEqual(result_pupil, [])
        self.assertEqual(result_tutor, [1594663200, 1594663206, 1594666700, 1594666800])


class TestMergePersonIntervals(unittest.TestCase):
    def test_no_merge_intervals(self):
        """ Нет интервалов, которые можно соединить """

        test_data = [1594663200, 1594663400, 1594663500, 1594663600]

        result = merge_person_intervals(test_data)

        self.assertEqual(result, test_data)

    def test_merge__multiple_intervals(self):
        """ Соединение нескольких интервалов """

        test_data = [1594663200, 1594663400, 1594663300, 1594663500, 1594663400, 1594663600]

        result = merge_person_intervals(test_data)
        true_merge_list = [1594663200, 1594663600]

        self.assertEqual(result, true_merge_list)


class TestCalculateTotalTimeInLesson(unittest.TestCase):

    def test_1_intersection(self):
        """ 1 пересечение интервалов """

        pupil_merged_intervals = [1594663200, 1594663260, 1594663280, 1594663290]
        tutor_merged_intervals = [1594663250, 1594663270, 1594663350, 1594663370]

        result = calculate_total_time_in_lesson(pupil_merged_intervals, tutor_merged_intervals)
        self.assertEqual(result, 10)

    def test_2_intersections(self):
        """ 2 пересечения интервалов (правильно ли считается сумма пересечений) """

        pupil_merged_intervals = [1594663200, 1594663260, 1594663280, 1594663290, 1594663320, 1594663370]
        tutor_merged_intervals = [1594663250, 1594663290]

        result = calculate_total_time_in_lesson(pupil_merged_intervals, tutor_merged_intervals)
        self.assertEqual(result, 20)

    def test_0_intersections(self):
        """ Нет пересечений """

        pupil_merged_intervals = [1594663200, 1594663260, 1594663280, 1594663290]
        tutor_merged_intervals = [1594663270, 1594663279]

        result = calculate_total_time_in_lesson(pupil_merged_intervals, tutor_merged_intervals)
        self.assertEqual(result, 0)

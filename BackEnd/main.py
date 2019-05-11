#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request

from ModelProcess import *
from Service import *


def after_request(response):
    """
    允许客户端异步加载
    :param response:
    :return:
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


def main():
    app = Flask(__name__)
    app.after_request(after_request)
    query_process = ModelProcess()
    service = Service()
    neo4j = Neo4j()

    @app.route('/')
    def index():
        return "index"

    @app.route('/course/adv', methods={"GET"})
    def get_adv_courses():
        """
        获取一门课程的所有先修课程
        :return:
        """
        # 获取course_name参数
        course_name = request.form.get('course_name')
        if not course_name:
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()
        return service.get_adv_courses(course_name)

    @app.route('/course/info', methods={"GET"})
    def get_course_info():
        """
        获取课程详细信息
        :return:
        """
        # 获取course_name参数
        course_name = request.form.get('course_name')
        if not course_name:
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()
        return service.get_course_info(course_name)

    @app.route('/course/teacher', methods={"GET"})
    def get_course_teacher():
        """
        获取课程的教师信息
        :return:
        """
        # 获取course_name参数
        course_name = request.form.get('course_name')
        if not course_name:
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()
        return service.get_course_teacher(course_name)

    @app.route('/teacher/all_courses', methods={"GET"})
    def get_teacher_all_courses():
        """
        获取教师教的所有课程
        :return:
        """
        # 获取teacher_name参数
        teacher_name = request.form.get('teacher_name')
        if not teacher_name:
            return ResponseData(ExceptionMsg.REQUIRE_TEACHER_NAME).encode()
        return service.get_teacher_all_courses(teacher_name)

    @app.route('/query')
    def query():

        # 获取question参数
        question = request.form.get('question')
        if not question:
            return ResponseData(ExceptionMsg.REQUIRE_QUESTION).encode()

        """
        返回对应的问题下标以及将模板中代词替换为具体名词之后的结果
        如:
            1:cn 先修课程
        将会返回:
            1,['离散数学','先修课程']
        """
        question_index, pattern = query_process.analysis_query(question)
        if question_index == 1:
            # 获取课程的先修课程
            course_name = pattern[0]
            return service.get_adv_courses(course_name)
        elif question_index == 8:
            # 获取课程的授课老师
            course_name = pattern[0]
            return service.get_course_teacher(course_name)
        else:
            # 获取课程的属性信息
            course_name = pattern[0]
            course_info = neo4j.get_course_node(course_name)
            if question_index == 0:
                return ResponseData(data=course_info['details']).encode()
            elif question_index == 2:
                return ResponseData(data=course_info['semester']).encode()
            elif question_index == 3:
                return ResponseData(data=course_info['optional']).encode()
            elif question_index == 4:
                return ResponseData(data=course_info['credit']).encode()
            elif question_index == 5:
                return ResponseData(data=course_info['credit_hour']).encode()
            elif question_index == 6:
                return ResponseData(data=course_info['id']).encode()
            elif question_index == 7:
                return ResponseData(data=course_info['english_name']).encode()
            else:
                return ResponseData(ExceptionMsg.QUESTION_IDENTIFICATION_WRONG).encode()

    app.run(debug=True)


if __name__ == '__main__':
    main()

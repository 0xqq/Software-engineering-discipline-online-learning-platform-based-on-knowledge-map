# coding=gbk
import re
import xml.dom.minidom
from pyquery import PyQuery as pq
from jieba.analyse import *

doc = xml.dom.minidom.Document()


def init_xml():
    """
    :return: �γ����Ƶ�xml���� ���޿γ̵�xml����
    """
    # ��ʼ��һ��xml����
    global doc
    root = doc.createElement("root")
    doc.appendChild(root)

    # �γ����ֶ�Ӧ�ı�ǩ
    courses_name_xml = doc.createElement("courses")
    root.appendChild(courses_name_xml)

    # ���޿γ̶�Ӧ�ı�ǩ
    adv_courses_xml = doc.createElement("adv-course")
    root.appendChild(adv_courses_xml)

    return courses_name_xml, adv_courses_xml


def save_course_name_and_detail_to_xml(courses, courses_name_xml):
    """
    �洢�γ����ƺ���ϸ������Ϣ
    :param courses: ���пγ���ɵ�list
    :param courses_name_xml: xml����(�γ���Ϣ���ᱣ�浽����)
    :return: �γ����ƺͶ�Ӧ�±���ɵ��ֵ�
    """
    global doc
    course_index = 0
    course_name_to_index = {}
    courses_name = courses["name"]
    courses_detail = courses["detail"]
    for i in range(len(courses_name)):
        # ���γ����ƴ��xml�����
        create_node(node_parent=courses_name_xml, node_name="name", node_content=courses_name[i])
        create_node(node_parent=courses_name_xml, node_name="details", node_content=courses_detail[i])

        # ���γ����ƺͶ�Ӧ���±�洢��һ��dict
        course_name_to_index[courses_name[i]] = course_index
        course_index += 1

    return course_name_to_index


def convert_adv_course(courses_advance, course_name_to_index):
    """
    :param courses_advance: ���޿γ�
    :param course_name_to_index: �γ������±�Ķ�Ӧ��ϵ
    :return: ���޿γ��ֵ�
    """
    pre_course_index = 0
    adv_course_dict = {}
    for course_adv in courses_advance:
        # ȡ���γ̵����޿���Ϣ
        if course_adv != "��":
            for course_adv_item in course_name_to_index.keys():
                # �ҳ��ڱ��ſγ̵����޿��еĿγ�����
                if course_adv_item in course_adv:
                    if pre_course_index not in adv_course_dict.keys():
                        adv_course_dict[pre_course_index] = [course_name_to_index[course_adv_item]]
                    else:
                        adv_course_dict[pre_course_index].append(course_name_to_index[course_adv_item])
            # �˴�����"����������������"�������
            if "����������������" in course_adv:
                if pre_course_index not in adv_course_dict.keys():
                    adv_course_dict[pre_course_index] = [-1]
                else:
                    adv_course_dict[pre_course_index].append(-1)

        pre_course_index += 1
    return adv_course_dict


def save_course_adv_to_xml(adv_course_dict, courses_adv_xml):
    """
    :param adv_course_dict: ���޿γ��ֵ�
    :param courses_adv_xml: ���޿γ̵�xml����
    :return: none
    """
    for pre_course, adv_courses in adv_course_dict.items():
        for adv_course in adv_courses:
            # ����һ�����޿νڵ�
            node = doc.createElement("item")
            # �������޿νڵ���ӵ��������޿νڵ���
            courses_adv_xml.appendChild(node)
            # �������޿��е�ǰ�γ̵Ľڵ�
            create_node(node_parent=node, node_name="adv", node_content=pre_course)
            # �������޿������޿γ̵���Ϣ
            create_node(node_parent=node, node_name="pre", node_content=adv_course)


def create_node(node_parent, node_name, node_content):
    """
    :param node_parent: �����Ԫ�صĸ��ڵ�
    :param node_name: Ҫ��ӵĽڵ�����
    :param node_content: �ڵ�����
    :return:
    """
    global doc
    node_adv = doc.createElement(node_name)
    node_adv.appendChild(doc.createTextNode(str(node_content)))
    node_parent.appendChild(node_adv)


def save_xml_to_file():
    global doc
    fp = open('data.xml', 'w')
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="gbk")


def parse_html(filename):
    """
    :param filename: html�ļ���
    :return: �γ���Ϣlist
    """
    pyquery_html = pq(filename=filename)
    # ��ȡ�γ̱�������޿γ�
    li = pyquery_html('body > div.WordSection2 > table,p')
    courses_temp = re.findall("�γ�����\n(.*?)\n�γ̱��.*?���޿γ�\n(.*?)�γ�����.*?�����γ̽�ѧĿ��(.*?)�����γ���֧�ŵı�ҵҪ��", li.text(),
                              flags=re.DOTALL)

    return {"name": [item[0].strip('���ģ�') for item in courses_temp],
            "advance": [item[1].strip('��ſγ����� ') for item in courses_temp],
            "detail": [item[2].strip() for item in courses_temp]}


def find_all_course_can_study(courses_name, adv_course_dict, learned_courses=[]):
    """
    ����Ѱ�����еĵ�ǰ�����ϵĿγ�
    :param courses_name: �γ����ֶ�Ӧ������
    :param adv_course_dict: �γ������޿εĶ�Ӧ�ֵ�
    :param learned_courses: �Ѿ�ѧ���Ŀγ�
    :return: ����ѡ��Ŀγ�
    """
    can_be_selected_courses = []
    for course_index in range(len(courses_name)):
        # ��ǰ�γ�û��ѧ��
        if course_index not in learned_courses:
            # ��ǰ�γ������޿γ�
            if course_index in adv_course_dict:
                # �ж��Ƿ��������޿γ̶��Ѿ�ѧ����
                all_adv_courses_has_been_learned = True
                for adv_course in adv_course_dict[course_index]:
                    if adv_course not in learned_courses:
                        all_adv_courses_has_been_learned = False
                        break
                if all_adv_courses_has_been_learned:
                    can_be_selected_courses.append(course_index)
            else:
                can_be_selected_courses.append(course_index)
    return can_be_selected_courses


tags = ["���ݿ�", "���ݽṹ", "c����", "Java", "Linux", "XML", "�������", "�������", "C++", "���������"]


def count_tags_occurrences_in_every_courses_details(courses_details, favorite_tags_index):
    tags_occurrences = []
    for course_index in range(len(courses_details)):
        tags_occurrences.append(0)
        for favorite_tag_index in favorite_tags_index:
            # ͳ��һ����ǩ�ڿγ̽����г��ֵĴ���
            tag_occurrences_in_one_class = courses_details[course_index].count(tags[favorite_tag_index])
            tags_occurrences[course_index] += tag_occurrences_in_one_class
    return tags_occurrences


def main():
    courses = parse_html("hello.htm")
    courses_name_xml, adv_courses_xml = init_xml()
    course_name_to_index = save_course_name_and_detail_to_xml(courses, courses_name_xml)
    adv_course_dict = convert_adv_course(courses["advance"], course_name_to_index)
    save_course_adv_to_xml(adv_course_dict, adv_courses_xml)
    save_xml_to_file()

    can_be_selected_courses = find_all_course_can_study(courses_name=courses["name"], adv_course_dict=adv_course_dict,
                                                        learned_courses=[])
    tags_occurrences = count_tags_occurrences_in_every_courses_details(courses_details=courses["detail"], favorite_tags_index=[0, 1, 2])
    print(tags_occurrences)


if __name__ == '__main__':
    main()

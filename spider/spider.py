# coding=gbk
import os
import re
import xml.dom.minidom
from setting import data_xml_dir_path

from pyquery import PyQuery as pq

doc = xml.dom.minidom.Document()


def init_xml():
    """
    ��ʼ��һ��xml�ļ����󣬷��������ڵ�
    :return: �γ���ϸ��Ϣ��xml���� ���޿γ̵�xml����
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


def convert_adv_course(courses_info, course_name_to_index):
    """
    �����ְ�����޿γ���ϢתΪ���ֱ�ʾ���ֵ�
    :param courses_info: �γ���Ϣ
    :param course_name_to_index: �γ������±�Ķ�Ӧ��ϵ
    :return: ���޿γ��ֵ�(��һ�ſε��±�ָ�����ſγ�)
    """
    adv_courses_dict = {}
    for i, course_info in enumerate(courses_info):
        # ��õ�ǰ�γ̵����޿γ�
        course_adv = course_info['advance']
        if course_adv == "��":
            continue
        # �������еĿγ�����,������޿γ��а���������,�ͼӽ�ȥ
        for course_name in course_name_to_index.keys():
            if course_name not in course_adv:
                continue
            if i not in adv_courses_dict.keys():
                adv_courses_dict[i] = [course_name_to_index[course_name]]
            else:
                adv_courses_dict[i].append(course_name_to_index[course_name])
    print(adv_courses_dict)
    return adv_courses_dict


def save_course_adv_to_xml(courses_info, course_name_to_index, courses_adv_xml):
    """
    # �����޿γ���Ϣ����xml��
    :param courses_info: �γ���Ϣ
    :param course_name_to_index:�γ������±�Ķ�Ӧ��ϵ
    :param courses_adv_xml: ���޿γ̵�xml����
    :return: None
    """
    # �����ְ�Ŀγ�������Ϣת��Ϊ�ֵ�
    adv_course_dict = convert_adv_course(courses_info=courses_info, course_name_to_index=course_name_to_index)
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
    print("�ɹ�Ϊ���޿γ̴���Ϊxml�ڵ�")


def create_node(node_parent, node_name, node_content=None):
    """
    # ����һ���ڵ�,�ڵ�ĸ��ڵ�Ϊnode_parent,�½������Ϊnode_name,�ڵ�����Ϊnode_content
    :param node_parent: �½ڵ�ĸ��ڵ�
    :param node_name: �½ڵ������
    :param node_content: �ڵ�����
    :return: �´����Ľڵ����
    """
    global doc
    node_adv = doc.createElement(node_name)
    if node_content is not None:
        node_adv.appendChild(doc.createTextNode(str(node_content)))
    node_parent.appendChild(node_adv)
    return node_adv


def save_xml_to_file():
    """
    ��xml��Ϣд���ļ���
    :return:
    """
    global doc
    path = os.path.join('../', data_xml_dir_path)
    fp = open(path, 'w')
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="gbk")
    print('�ɹ���xml�ڵ����'+path+'��')


def parse_html(html_name):
    """
    ����html_name�е�����,����ȡ���Ŀγ���Ϣ����
    :param html_name: html�ļ���
    :return: [{"name":,"id":...}...]
    """
    pyquery_html = pq(filename=html_name)
    # ��ȡ�γ̱�������޿γ�
    li = pyquery_html('body > div.WordSection2 > table,p')
    print(li.text())
    courses_temp = re.findall("�γ�����\n(.*?)"  # �γ�����
                              "\n�γ̱��\n(.*?)"  # �γ̱��
                              "\n(.*?)"  # Ӣ������ 
                              "\nѧ��/ѧʱ\n(.*?)/(.*?)"
                              "\n(.*?)"
                              "\n����ѧ��\n(.*?)\n.*?"
                              "\n���޿γ�\n(.*?)�γ�����.*?�����γ̽�ѧĿ��(.*?)�����γ���֧�ŵı�ҵҪ��.*?ִ����:(.*?)�����", li.text(),
                              flags=re.DOTALL)
    courses_info = []
    for item in courses_temp:
        courses_info.append({
            # �γ�����
            "name": "".join(item[0].strip('���ģ�').split()),
            # �γ̱��
            "id": "".join(item[1].strip("").split()),
            # Ӣ������
            "english_name": item[2].strip("Ӣ�ģ�").replace(u'\xa0', u' '),
            # ѧ��
            "credit": "".join(item[3].strip("").split()),
            # ѧʱ
            "credit_hour": "".join(item[4].strip("").split()),
            # # ѡ��/����
            "optional": 'y' if '���ޣ���' in "".join(item[5].strip("").split())
                .replace(u'\u2a57', u'').replace(u'\uf0fc', u'') else 'n',
            # ����ѧ��
            "semester": "".join(item[6].strip("").split()),
            # ���޿γ�
            "advance": "".join(item[7].strip("").split()),
            # �γ���ϸ��Ϣ
            "details": "".join(item[8].strip("").split()),
            # �γ���ʦ
            "teacher": "".join(item[9].strip("").split())
        })
    print("�ɹ�����html�еĿγ���Ϣ,�γ�����Ϊ:", len(courses_info))
    return courses_info


def save_courses_info_to_xml(courses_info):
    """
    ���γ���Ϣ����xml��
    :param courses_info: �γ���Ϣ
    :return: None
    """
    courses_info_xml, adv_courses_xml = init_xml()
    course_name_to_index = {}
    for i, course_info in enumerate(courses_info):
        course_node_xml = create_node(node_parent=courses_info_xml, node_name="course")
        for key, value in course_info.items():
            if key == 'advance':
                continue
            create_node(node_parent=course_node_xml, node_name=str(key), node_content=str(value))
        # ���γ����ƺͶ�Ӧ���±�洢��һ��dict
        course_name_to_index[course_info['name']] = i
    print("�ɹ�Ϊ�γ̵���Ϣ(�����޿γ�)����Ϊxml�ڵ�")
    save_course_adv_to_xml(courses_info, course_name_to_index, adv_courses_xml)
    save_xml_to_file()


def main():
    # ����xml
    courses_info = parse_html("hello.htm")
    # ���������Ŀγ���Ϣ����xml��
    save_courses_info_to_xml(courses_info)


if __name__ == '__main__':
    main()

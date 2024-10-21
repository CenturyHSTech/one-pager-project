import pytest
from webcode_tk import html_tools
from webcode_tk import validator_tools as validator

project_dir = "project/"
all_html_files = html_tools.get_all_html_files(project_dir)

# List of required elements (per web page)
required_elements = [("doctype", 1),
                     ("html", 1),
                     ("head", 1),
                     ("title", 1),
                     ("h1", 1)]

min_required_elements = [
    ("h2", 3),
    ("p", 6),
    ("ul OR ol", 1),
    ("li", 4),
    ("figure", 2),
    ("img", 2),
    ("a", 4)
    ]

exact_number_of_elements = []
min_number_of_elements = []

for file in all_html_files:
    for i in range(len(required_elements)):
        # Get requirements for exact number
        element, number = required_elements[i]
        exact_number_of_elements.append((file, element, number))
    for i in range(len(min_required_elements)):
        # Get requirements for minimum number
        element, number = min_required_elements[i]
        min_number_of_elements.append((file, element, number))


@pytest.fixture
def html_files():
    html_files = html_tools.get_all_html_files(project_dir)
    return html_files


def test_has_index_file(html_files):
    assert "project/index.html" in html_files


@pytest.mark.parametrize("file,element,num", exact_number_of_elements)
def test_files_for_exact_number_of_elements(file, element, num):
    if not html_files:
        assert False
    actual = html_tools.get_num_elements_in_file(element, file)
    assert actual == num


@pytest.mark.parametrize("file,element,num", min_number_of_elements)
def test_files_for_minimum_number_of_elements(file, element, num):
    if not html_files:
        assert False
    if "or" in element.lower():
        elements = element.split()
        actual = 0
        for el in elements:
            el = el.strip()
            actual += html_tools.get_num_elements_in_file(el, file)
    else:
        actual = html_tools.get_num_elements_in_file(element, file)
    assert actual >= num


def test_passes_html_validation(html_files):
    errors = []
    if not html_files:
        assert "html files" in html_files
    for file in html_files:
        errors += validator.get_markup_validity(file)
    assert not errors

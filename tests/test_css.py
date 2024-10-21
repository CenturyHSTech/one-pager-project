import pytest
import re
from file_clerk import clerk
from webcode_tk import css_tools as css
from webcode_tk import html_tools as html
from webcode_tk import validator_tools as validator

project_dir = "project/"


def get_all_project_stylesheets(project_dir: str) -> list:
    directory = project_dir
    html_files = clerk.get_all_files_of_type(directory, "html")
    all_files_styles = []
    for file in html_files:
        filename = clerk.get_file_name(file)
        stylesheets = css.get_all_stylesheets_by_file(file)
        all_files_styles.append((filename, stylesheets))
    return all_files_styles


all_files_styles = get_all_project_stylesheets(project_dir)
all_files = clerk.get_all_project_files(project_dir)


# Build test data for style attribute check (none allowed)
def get_style_attributes(file):
    has_style_attr = html.has_style_attribute_data(file)
    if has_style_attr:
        result = f"fail: {file} uses style attributes"
    else:
        result = f"pass: {file} does not use style attributes"
    return result


style_attributes_in_project = []
html_files = clerk.get_all_files_of_type(project_dir, "html")
for file in html_files:
    try:
        attributes = get_style_attributes(file)
        style_attributes_in_project.append(attributes)
    except AttributeError as err:
        print(err)


# Build validation data
def validation_errors():
    validation_results = []
    for file in all_files:
        errors = []
        code = ""
        file_name = clerk.get_file_name(file)
        expected = f"pass: {file_name} passes CSS validation!"
        file_type = clerk.get_file_type(file)
        if file_type == "html":
            style_tag = html.get_elements("style", file)
            if style_tag:
                code = html.get_element_content(style_tag)
                result = validator.validate_css(code)
                errors = validator.get_css_errors_list(result)
        elif file_type == "css":
            code = clerk.file_to_string(file)
            result = validator.validate_css(code)
            errors = validator.get_css_errors_list(result)
        if errors:
            for error in errors:
                actual_result = f"fail: {file_name}: {error}"
                validation_results.append(actual_result)
        else:
            if code:
                validation_results.append(expected)
    if not validation_results:
        validation_results = ["fail: no files present to validate"]
    return validation_results


css_validation_results = validation_errors()


# Make sure all HTML files apply styles
def styles_applied_check():
    files_with_styles = []
    for file in all_files:
        file_type = clerk.get_file_type(file)
        if file_type != "html":
            continue
        expected = f"pass: {file} applies CSS."
        styles = css.get_all_stylesheets_by_file(file)
        if not styles:
            results = f"fail: {file} does NOT apply CSS."
            files_with_styles.append(results)
        else:
            results = expected
            files_with_styles.append(results)
    if not files_with_styles:
        files_with_styles.append("fail: no files to apply styles to")
    return files_with_styles


applying_styles_results = styles_applied_check()


# Test for font-families applied
def get_font_data():
    font_data = []
    all_file_data = css.get_styles_by_html_files(project_dir)
    for file in all_file_data:
        filename = clerk.get_file_name(file.get("file"))
        stylesheets = file.get("stylesheets")
        font_styles = []
        for sheet in stylesheets:
            font_details = css.get_font_families(sheet)
            for item in font_details:
                selector = item.get("selector")
                family = item.get("family")
                if "," in family:
                    first_font = family.split(",")[0].strip()
                else:
                    first_font = family
                first_font = first_font.replace("'", "")
                first_font = first_font.replace('"', "")
                if first_font.lower() == "times new roman":
                    results = f"fail: {filename}: {selector} element was set "
                    results += "to the default font"
                else:
                    results = f"pass: {filename}: {selector} element "
                    results += f"was set to {first_font}"

                font_styles.append(results)
        # We have all font styles applied
        if not font_styles:
            font_data.append(f"fail: {filename} No modified" +
                             f" fonts for {filename}")
        else:
            font_data += font_styles
    if not font_data:
        font_data.append(
            "fail: no html files to apply font styling to")
    return tuple(font_data)


font_data = get_font_data()


# Test for colors applied and color contrast results
def get_global_color_data():
    color_rule_data = []
    for data in all_files_styles:
        filename = data[0]
        passes = []
        for sheet in data[1]:
            rules = sheet.rulesets
            global_color_data = css.get_global_color_details(rules)
            if global_color_data:
                for item in global_color_data:
                    file, result = get_color_data(filename, item)
                    passes.append(f"pass: {file} {result}")
        if passes:
            details = ""
            for detail in passes:
                details += detail
        else:
            details = f"fail: {filename} does NOT apply global colors"
        color_rule_data.append(details)
    if not color_rule_data:
        color_rule_data.append(
            "fail: no html files to apply color styles to"
            )
    return color_rule_data


def get_color_data(file, item):
    selector = item.get("selector")
    bg_color = item.get("background-color")
    color = item.get("color")
    contrast_ratio = item.get("contrast_ratio")
    passes = item.get("passes_normal_aaa")
    if passes:
        results = "passes global colors"
    else:
        results = f"{selector} {bg_color} and {color} fail with a contrast"
        results += f" ratio of {contrast_ratio}."
    color_data = (file, results)
    return color_data


global_color_rule_data = get_global_color_data()


def get_header_color_rule_data():
    data = []
    header_re = css.regex_patterns.get("header_selector")
    for file in all_files_styles:
        filename = file[0]
        filepath = project_dir + filename
        all_color_rules = css.get_all_color_rules(filepath)
        header_selectors = []
        for key, val in all_color_rules.items():
            if key == "file":
                continue
            is_header_selector = re.findall(header_re, key)
            if is_header_selector:
                # we have a header selector
                # we only need to check color
                color_data = val
                color_value = color_data.get("color")
                bg_value = color_data.get("background-color")
                if color_value:
                    if bg_value:
                        header_selectors.append((filename,
                                                 color_value,
                                                 bg_value))
                    else:
                        header_selectors.append((filename,
                                                 color_value,
                                                 None))
                if bg_value:
                    header_selectors.append((filename,
                                             None,
                                             bg_value))
        if header_selectors:
            data.append(f"pass: {filename} applies colors to headers")
        else:
            data.append(
                f"fail: {filename} does NOT apply colors to headers")
    if not data:
        data.append(
            "fail: no html files to apply header colors to"
        )
    return data


header_color_rule_data = get_header_color_rule_data()


@pytest.fixture
def project_files():
    all_files = clerk.get_all_project_files(project_dir)
    return all_files


@pytest.mark.parametrize("results", style_attributes_in_project)
def test_css_for_no_style_attributes(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", css_validation_results)
def test_css_validation(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", applying_styles_results)
def test_if_file_applies_styles(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results",
                         global_color_rule_data)
def test_global_colors(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", font_data)
def test_font_requirements(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", header_color_rule_data)
def test_for_colors_applied_to_headings(results):
    assert "pass" == results[:4]
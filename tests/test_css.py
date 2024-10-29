import pytest
from webcode_tk import cascade_tools as cascade
from webcode_tk import css_tools as css
from webcode_tk import validator_tools as validator
from file_clerk import clerk

project_dir = "project/"

style_attributes_in_project = css.no_style_attributes_allowed_report(
    project_dir)
css_validation_results = validator.get_project_validation(
    project_dir, "css"
)


files_by_styles = css.get_styles_by_html_files(project_dir)
color_contrast_results = []
for file in files_by_styles:
    fails = []
    success = ""
    filepath = file.get("file")
    filename = clerk.get_file_name(filepath)
    stylesheets = file.get("stylesheets")
    tree = cascade.CSSAppliedTree(filepath, stylesheets)
    results = cascade.get_color_contrast_details(tree, "AAA")
    for result in results:
        if "fail" in result and result not in fails:
            msg = f"fail: {filename} - {result}"
            fails.append(msg)
        if "success" in result:
            success = result.replace("success", "pass")
    if success and not fails:
        color_contrast_results.append(success)
    else:
        color_contrast_results += fails
if not color_contrast_results:
    color_contrast_results.append(
        "fail: there are no colors applied to check contrast")

applying_styles_results = css.styles_applied_report(project_dir)
font_data = css.fonts_applied_report(project_dir)
header_color_rule_data = css.get_heading_color_report(project_dir)


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
                         color_contrast_results)
def test_global_colors(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", font_data)
def test_font_requirements(results):
    assert "pass" == results[:4]


@pytest.mark.parametrize("results", header_color_rule_data)
def test_for_colors_applied_to_headings(results):
    assert "pass" == results[:4]

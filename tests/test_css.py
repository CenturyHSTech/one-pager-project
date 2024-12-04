import pytest
from webcode_tk import css_tools as css
from webcode_tk import validator_tools as validator

project_dir = "project/"

style_attributes_in_project = css.no_style_attributes_allowed_report(
    project_dir)
css_validation_results = validator.get_project_validation(
    project_dir, "css"
)


color_contrast_results = []
color_contrast_results = css.get_project_color_contrast_report(project_dir)

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

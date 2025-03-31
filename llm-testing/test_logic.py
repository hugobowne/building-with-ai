"""
To run:
> pytest -vv test_logic.py
"""
from datetime import datetime
import concurrent.futures

import pytest
import logic
import json

# (1) example pytest test functions

# pytest -vv test_logic.py::test_some_logic
def test_some_logic():
    actual = logic.addition(1, 2)
    assert actual == 3

# pytest -vv test_logic.py::test_some_logic_parameterized
@pytest.mark.parametrize(
    "a,b,expected", [
        (1, 2, 3),
        (-1, 2, 1),
])
def test_some_logic_parameterized(a, b, expected):
    actual = logic.addition(a, b)
    assert actual == expected


# Helper function to load text from a file
def load_text_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

# (2) testing our LLM call
extract_profile_data = logic.extract_profile_data
# extract_profile_data = logic.extract_profile_data_strict

# pytest -vv test_logic.py::test_extract_profile_data_stefan
def test_extract_profile_data_stefan():
    """Can look like a regular test."""
    linkedin_text = load_text_from_file("data/stefanLI.txt")
    expected = {
        "Name": "Stefan Krawczyk",
        "Current Role": "CEO @ DAGWorks Inc.",
        "Location": "San Francisco, California, United States",
        "Previous Roles": [],
        "Education": [],
    }
    output = extract_profile_data(linkedin_text)
    assert output["Name"] == expected["Name"]
    assert output["Current Role"] == expected["Current Role"]
    assert output["Location"] == expected["Location"]
    assert output["Previous Roles"] == expected["Previous Roles"]
    assert output["Education"] == expected["Education"]
    assert output == expected
    # problem: asserts fail at the first failure,
    # but we want to evaluate all of them...

# (3) Where should we focus? Understand the variance
# pytest -vv test_logic.py::test_extract_profile_data_stefan_stability
def test_extract_profile_data_stefan_stability():
    """Let's run it a few times to see output variability."""
    linkedin_text = load_text_from_file("data/stefanLI.txt")
    outputs = run_in_parallel(linkedin_text, num_iterations=10)
    # Check for consistency - for each key create a set of values
    variances = {}
    for key in outputs[0].keys():
        all_values = set(json.dumps(output[key]) for output in outputs)
        if len(all_values) > 1:
            variances[key] = list(all_values)
    variances_str = json.dumps(variances, indent=2)
    assert len(variances) == 0, "Outputs vary across iterations:\n" + variances_str

# (4) Show one prompt iteration

# (5) Do parametrized testing for more inputs
expected_values = {
    "data/stefanLI.txt": {
        "Name": "Stefan Krawczyk",
        "Current Role": "CEO @ DAGWorks Inc.",
        "Location": "San Francisco, California, United States",
        "Previous Roles": [],
        "Education": [],
    },
    "data/hbaLI.txt": {
        "Name": "Hugo Bowne-Anderson",
        "Current Role": "Independent Data and AI Scientist",
        "Location": "Darlinghurst, New South Wales, Australia",
        "Previous Roles": [
            {"Title": "Head of Developer Relations", "Company": "Outerbounds", "Duration": "Feb 2022 - Aug 2024"},
            {"Title": "Head of Data Science Evangelism and Marketing", "Company": "Coiled", "Duration": "May 2020 - Oct 2021"},
        ],
        "Education": [
            {"Degree": "Doctor of Philosophy (PhD)", "Field": "Pure Mathematics", "Institution": "UNSW", "Years": "2006 - 2011"},
            {"Degree": "Bachelor of Science (B.S.) (First Class Honors)", "Field": "Mathematics, English Literature", "Institution": "University of Sydney", "Years": "2001 - 2005"},
        ],
    },
}

# (5) Parametrized testing & pytest-harvest & collating results into a CSV
# pytest -vv -rP test_logic.py::test_extract_profile_data test_logic.py::test_print_results
@pytest.mark.parametrize(
    "file_path,expected", [
        ("data/stefanLI.txt", expected_values["data/stefanLI.txt"]),
        ("data/hbaLI.txt", expected_values["data/hbaLI.txt"]),
])
def test_extract_profile_data(file_path, expected, results_bag):
    """Parametrized test for extract_profile_data function
    Uses pytest-harvest `results_bag` fixture to store results."""
    linkedin_text = load_text_from_file(file_path)
    actual = extract_profile_data(linkedin_text)
    results_bag.input = linkedin_text
    results_bag.expected = expected
    results_bag.actual = actual
    results_bag.exact_match = actual == expected
    for k in expected.keys():
        results_bag[k] = actual[k] == expected[k]
    assert actual["Name"] == expected["Name"]  # Name should be 100%


def test_print_results(module_results_df):
    """This is run last and prints out the results.

    This is where we could put some hard asserts as well to fail
    the test suite if we need to.

    Alternatively we could write pytest hooks, etc. but for this
    lesson this is simpler.

    :param module_results_df: pytest-harvest fixture
    """
    module_results_df.reset_index(inplace=True)
    # filter to only the tests of interest
    tests_of_interest = module_results_df[
        module_results_df["exact_match"].isna() == False
    ]
    print(tests_of_interest.columns)
    print(tests_of_interest.head())
    # compute accuracy by field
    fields = ["Name", "Current Role", "Location", "Previous Roles", "Education"]
    field_accuracy = {
        field: (
           sum(tests_of_interest[field]) / len(tests_of_interest)
        ) * 100.0
        for field in fields
    }
    # print accuracy by field
    print("Accuracy by field:")
    for field, accuracy in field_accuracy.items():
        print(f"{field}: {accuracy}%")
    # can save to CSV etc
    current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
    columns_to_output = [
        "test_id",
        "status",
        "duration_ms",
        "file_path",
        "input",
        "expected",
        "actual",
        "exact_match",

    ] + fields
    tests_of_interest[columns_to_output].to_csv(
        f"logic_results{current_datetime}.csv", quoting=1
    )
    # assert anything we must fail on
    assert field_accuracy["Name"] > 99.0

#--- helpers
# Run the extract_profile_data function in parallel
def run_in_parallel(linkedin_text, num_iterations=10):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(extract_profile_data, linkedin_text)
                   for _ in range(num_iterations)]
        outputs = [future.result()
                   for future in concurrent.futures.as_completed(futures)]
    return outputs
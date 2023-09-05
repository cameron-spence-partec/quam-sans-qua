import json
from dataclasses import dataclass

from quam_components.serialisation.json import JSONSerialiser
from quam_components.core import QuamRoot, QuamComponent


@dataclass
class BareQuamRoot(QuamRoot):
    pass


def test_serialise_empty_quam_root(tmp_path):
    quam = BareQuamRoot()
    json_serialiser = JSONSerialiser()

    file = tmp_path / "quam2.json"

    json_serialiser.save(quam, path=file)

    with open(file) as f:
        contents = json.load(f)
        assert contents == {"__class__": "test_serialisation.BareQuamRoot"}

    contents, metadata = json_serialiser.load(file)
    assert contents == {"__class__": "test_serialisation.BareQuamRoot"}
    assert metadata["component_mapping"] == {}
    assert metadata["default_filename"] == "quam2.json"
    assert metadata["default_foldername"] is None


@dataclass(kw_only=True, eq=False)
class QuamRoot1(QuamRoot):
    int_val: int
    quam_component: QuamComponent
    quam_component_separate: QuamComponent


@dataclass(kw_only=True, eq=False)
class QuamComponent1(QuamComponent):
    int_val: int


def test_save_load_basic(tmp_path):
    quam = QuamRoot1(
        int_val=1,
        quam_component=QuamComponent1(int_val=2),
        quam_component_separate=QuamComponent1(int_val=3),
    )

    json_serialiser = JSONSerialiser()
    json_file = tmp_path / "quam.json"

    json_serialiser.save(quam, path=json_file)

    quam_dict = json.load(json_file.open("r"))

    assert quam_dict == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        },
    }

    contents, metadata = json_serialiser.load(json_file)
    assert contents == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        },
    }
    assert metadata["component_mapping"] == {}
    assert metadata["default_filename"] == "quam.json"
    assert metadata["default_foldername"] == None


def test_save_load_basic_content_mapping(tmp_path):
    quam = QuamRoot1(
        int_val=1,
        quam_component=QuamComponent1(int_val=2),
        quam_component_separate=QuamComponent1(int_val=3),
    )

    json_serialiser = JSONSerialiser()
    json_file = tmp_path / "state.json"

    json_serialiser.save(
        quam,
        path=json_file,
        component_mapping={"separate.json": "quam_component_separate"},
    )

    quam_dict = json.load(json_file.open("r"))

    assert quam_dict == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
    }

    tmp_file = tmp_path / "separate.json"
    quam_dict = json.load(tmp_file.open("r"))
    assert quam_dict == {
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        }
    }

    contents, metadata = json_serialiser.load(tmp_path)
    assert contents == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        },
    }
    assert metadata["component_mapping"] == {
        "separate.json": ["quam_component_separate"]
    }
    assert metadata["default_filename"] == "state.json"
    assert metadata["default_foldername"] == str(tmp_path)


def test_save_load_folder_content_mapping(tmp_path):
    quam = QuamRoot1(
        int_val=1,
        quam_component=QuamComponent1(int_val=2),
        quam_component_separate=QuamComponent1(int_val=3),
    )

    json_serialiser = JSONSerialiser()
    json_folder = tmp_path / "quam"

    json_serialiser.save(
        quam,
        path=json_folder,
        component_mapping={"separate.json": "quam_component_separate"},
    )

    json_file = json_folder / "state.json"
    quam_dict = json.load(json_file.open("r"))

    assert quam_dict == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
    }

    tmp_file = json_folder / "separate.json"
    quam_dict = json.load(tmp_file.open("r"))
    assert quam_dict == {
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        }
    }

    contents, metadata = json_serialiser.load(json_folder)
    assert contents == {
        "__class__": "test_serialisation.QuamRoot1",
        "int_val": 1,
        "quam_component": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 2,
        },
        "quam_component_separate": {
            "__class__": "test_serialisation.QuamComponent1",
            "int_val": 3,
        },
    }
    assert metadata["component_mapping"] == {
        "separate.json": ["quam_component_separate"]
    }
    assert metadata["default_filename"] == "state.json"
    assert metadata["default_foldername"] == str(json_folder)


@dataclass
class TestQuamComponent(QuamComponent):
    int_val: int
    inner_quam: QuamComponent = None


@dataclass
class TestQuam(QuamRoot):
    int_val: int
    inner_quam: QuamComponent


def test_save_explicit_class(tmp_path):
    test_quam = TestQuamComponent(int_val=42, inner_quam=TestQuamComponent(43))

    json_serialiser = JSONSerialiser()
    json_file = tmp_path / "quam.json"

    json_serialiser.save(test_quam, path=json_file)

    with open(json_file) as f:
        contents = json.load(f)
        assert contents == {
            "int_val": 42,
            "inner_quam": {
                "__class__": "test_serialisation.TestQuamComponent",
                "int_val": 43,
            },
        }


def test_save_explicit_class_root(tmp_path):
    test_quam = TestQuam(int_val=42, inner_quam=TestQuamComponent(43))

    json_serialiser = JSONSerialiser()
    json_file = tmp_path / "quam.json"

    json_serialiser.save(test_quam, path=json_file)

    with open(json_file) as f:
        contents = json.load(f)
        assert contents == {
            "int_val": 42,
            "inner_quam": {
                "__class__": "test_serialisation.TestQuamComponent",
                "int_val": 43,
            },
            "__class__": "test_serialisation.TestQuam",
        }

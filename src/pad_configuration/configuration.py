################################################################################
#
#  Copyright (C) 2012-2022 Jack Araz, Eric Conte & Benjamin Fuks
#  The MadAnalysis development team, email: <ma5team@iphc.cnrs.fr>
#
#  This file is part of MadAnalysis 5.
#  Official website: <https://github.com/MadAnalysis/madanalysis5>
#
#  MadAnalysis 5 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MadAnalysis 5 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MadAnalysis 5. If not, see <http://www.gnu.org/licenses/>
#
################################################################################

import json
import os
from collections import namedtuple
from typing import Text, NamedTuple, Sequence, Union, Optional, Dict

import jsonschema


class Configuration:
    """
    Public Analysis Database configuration interpreter

    Parameters
    ----------
    padname : Text
        name of the PAD which can be "PAD", "PADForMA5tune", "PADForSFS"
    pad_data: Optional[Sequence[NamedTuple]]
        create configuration with existing data structure

    Raises
    ------
    AssertionError:
        invalid PAD name
    """

    _currentpath = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(_currentpath, "meta", "data_structure.json"), "r") as f:
        _schema = json.load(f)

    PADEntry = namedtuple(
        "PADEntry",
        ["name", "description", "url", "padversion", "ma5version", "gcc", "bibtex"], )
    URL = namedtuple("URL", ["cpp", "header", "info", "json", "detector"])
    # JSON = namedtuple("JSON", ["name", "url"])

    _paddata = {
        "PAD"          : os.path.join(_currentpath, "meta", "pad_data.json"),
        "PADForMA5tune": os.path.join(_currentpath, "meta", "padforma5tune_data.json"),
        "PADForSFS"    : os.path.join(_currentpath, "meta", "padforsfs_data.json"),
    }


    def __init__(self, padname: Text, pad_data: Optional[Sequence[NamedTuple]] = None):
        assert padname in ["PAD", "PADForMA5tune",
                           "PADForSFS", ], f"Unknown PAD name: {padname}"

        self.padname = padname

        if pad_data is None:
            tmp_json = []
            if os.path.isfile(Configuration._paddata[padname]):
                with open(Configuration._paddata[padname], "r") as tmp:
                    tmp_json = json.load(tmp)

            self.pad_data = []
            for entry in tmp_json:
                # entry["url"].update({"json" : [JSON(**jin) for jin in entry["url"]["json"]]})
                entry.update({"url": Configuration.URL(**entry["url"])})
                self.pad_data.append(Configuration.PADEntry(**entry))
        else:
            self.pad_data = pad_data


    def _asdict(self):
        to_return = []
        for entry in self.pad_data:
            entry = entry._asdict()
            entry.update({"url" : entry["url"]._asdict()})
            to_return.append(entry)
        return to_return


    def __getitem__(self, item: int):
        return self.pad_data[item]


    def __iter__(self):
        for entry in self.pad_data:
            yield entry


    def keys(self):
        return (x.name for x in self)


    def filter(self, ma5version: Text, gcc: int):
        """
        Filter the pad metadata with respect to current MadAnalysis 5 and gcc compiler version
        Parameters
        ----------
        ma5version : Text
            Local MadAnalysis 5 version
        gcc : int
            GCC version i.e. 98, 11, 14 etc.

        Returns
        -------
        Configuration
            new configuration limited only to the filtered entries
        """
        if ma5version.startswith("v"):
            ma5version = [int(x) for x in entry.ma5version[1:].split(".")]
        else:
            ma5version = [int(x) for x in entry.ma5version.split(".")]

        tmp = []
        for entry in self.pad_data:
            entry_vma5 = [int(x) for x in entry.ma5version[1:].split(".")]
            entry_vgcc = int(entry.gcc)

            ma5_check = [x >= y for x, y in
                         zip(ma5version[:len(current_ma5version)], entry_vma5)] + [True] * (
                                3 - len(current_ma5version))

            if not ma5_check[0]:
                continue
            if ma5_check[0] and not ma5_check[1]:
                continue
            if ma5_check[0] and ma5_check[1] and not ma5_check[2]:
                continue
            if gcc < entry_vgcc:
                continue

            tmp.append(entry)

        return Configuration(self.padname, tmp)


    def get_analysis(self, analysis: Text) -> NamedTuple:
        """
        Get metadata for a given analysis

        Parameters
        ----------
        analysis : Text
            analysis name

        Returns
        -------
        NamedTuple
            analysis metadata
        """
        for entry in self.pad_data:
            if entry.name == analysis:
                return entry


    def get_collaboration(self, collaboration: Text) -> Sequence[NamedTuple]:
        """
        Get the PAD metadata for a given collaboration

        Parameters
        ----------
        collaboration : Text
            collaboration name: atlas or cms

        Returns
        -------
        Sequence[get_collaboration]
            PAD metadata
        """
        assert collaboration in ["atlas", "cms"], f"Unknown collaboration: {collaboration}"
        collab = []
        for entry in self.pad_data:
            if collaboration in entry.name:
                collab.append(entry)
        return collab


    @staticmethod
    def add_entry(padname: Text, new_entry: Union[Sequence[Dict], Dict]) -> None:
        """
        Add PAD metadata entry for the given padname

        Parameters
        ----------
        padname : Text
            name of the PAD which can be "PAD", "PADForMA5tune", "PADForSFS"
        new_entry : Union[Sequence[Dict], Dict]
            new pad entry

        Raises
        ------
        jsonschema.exceptions.ValidationError:
            invalid new entry
        jsonschema.exceptions.SchemaError:
            invalid new entry
        AssertionError:
            invalid PAD name
            invalid entry type
        """
        assert padname in ["PAD", "PADForMA5tune",
                           "PADForSFS", ], f"Unknown PAD name: {padname}"

        if isinstance(new_entry, dict):
            new_entry = [new_entry]

        assert isinstance(new_entry, list), "Invalid entry type."

        try:
            jsonschema.validate(new_entry, Configuration._schema)
        except jsonschema.exceptions.ValidationError as err:
            print(
                "Invalid entry! please see `Configuration.entry_example` for the correct format."
            )
            raise jsonschema.exceptions.ValidationError(err)
        except jsonschema.exceptions.SchemaError as err:
            print(
                "Invalid entry! please see `Configuration.entry_example` for the correct format."
            )
            raise jsonschema.exceptions.SchemaError(err)

        local_config = None
        if os.path.isfile(Configuration._paddata[padname]):
            local_config = Configuration(padname)

        if local_config is not None:
            new_entries = []
            for entry in new_entry:
                if entry["name"] in local_config.analyses:
                    print(f"{entry['name']} already exist. Please modify the data instead.")
                    continue
                new_entries.append(entry)
        else:
            new_entries = new_entry

        if local_config is not None:
            pad_data = local_config._asdict() + new_entries
        else:
            pad_data = new_entries

        with open(Configuration._paddata[padname], "w") as f:
            json.dump(pad_data, f, indent = 4)


    def add_json_info(self, analysis: Text, entry: Sequence[Dict]):
        if isinstance(entry, dict):
            entry = [entry]
        assert isinstance(entry, list), "Unknown entry type."
        assert analysis in list(self.keys()), f"Unknown analysis: {analysis}"

        # Validate
        valid = []
        for ent in entry:
            if not all([x in ["name", "url"] for x in ent]):
                print("Corrupt entry: " + ent)
                continue
            valid.append(ent)

        if len(valid) > 0:
            pad_data = self._asdict()
            for idx, data_entry in enumerate(pad_data):
                if data_entry["name"] == analysis:
                    pad_data[idx]["url"]["json"] += valid
                    print(pad_data[idx]["url"]["json"])

            jsonschema.validate(pad_data, Configuration._schema)
            with open(Configuration._paddata[self.padname], "w") as f:
                json.dump(pad_data, f, indent = 4)


    @staticmethod
    @property
    def entry_example():
        return [{
            "name"         : "analysis name", "description": "analysis description", "url": {
                "cpp"         : "location of the code",
                "header"      : "location of the header file",
                "info"        : "location of the info file", "json": [{
                    "name": "name of the json extension",
                    "url" : "location of the json file for full likelihoods",
                }], "detector": "location of the detector card",
            }, "padversion": "PAD version of the analysis e.g. vSFS, v1.2, v1.1 etc.",
            "ma5version"   : "minimum madanalysis version required by the analysis",
            "gcc"          : "minimum c++ version required by the analysis",
            "bibtex"       : ["bibliography dedicated to the analysis"],
        }]


    def __str__(self):
        txt = "#    Analysis            | Description\n" + "#                        |\n"
        for entry in self.get_collaboration("atlas"):
            txt += entry.name.ljust(25, " ") + "| " + entry.description + "\n"
        for entry in self.get_collaboration("cms"):
            txt += entry.name.ljust(25, " ") + "| " + entry.description + "\n"
        return txt
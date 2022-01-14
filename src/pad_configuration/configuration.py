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
from collections import namedtuple, OrderedDict
from typing import Text, NamedTuple, Sequence, Union, Optional, Dict, Generator

import jsonschema

from .utils import json_zip, json_unzip


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
        assert padname in ["PAD", "PADForMA5tune", "PADForSFS", "combined"], \
            f"Unknown PAD name: {padname}"

        self.padname = padname

        if pad_data is None:
            assert padname != "combined", "Combined configuration requires independent data."
            tmp_json = []
            if os.path.isfile(Configuration._paddata[padname]):
                with open(Configuration._paddata[padname], "r") as tmp:
                    tmp_json = json.load(tmp)
            elif os.path.isfile(Configuration._paddata[padname].split(".")[0] + ".jz"):
                tmp_json = self._decompress(
                    Configuration._paddata[padname].split(".")[0] + ".jz"
                )
            else:
                raise FileNotFoundError(
                    f"Can not find metadata files: \n\t"
                    f" - {Configuration._paddata[padname]}\n\t"
                    f" - {Configuration._paddata[padname].split('.')[0]}.jz")

            self.pad_data = []
            for entry in tmp_json:
                # entry["url"].update({"json" : [JSON(**jin) for jin in entry["url"]["json"]]})
                entry.update({"url": Configuration.URL(**entry["url"])})
                self.pad_data.append(Configuration.PADEntry(**entry))
        else:
            assert isinstance(pad_data, list) and \
                   all([isinstance(x, Configuration.PADEntry) for x in pad_data]), \
                "Unknown data type."
            self.pad_data = pad_data


    @staticmethod
    def _compress(filename: Text, json_input: Union[Sequence[Dict], Dict]) -> None:
        compressed_pad_data = json_zip(json_input)
        with open(filename, "w") as f:
            f.write(compressed_pad_data)


    @staticmethod
    def _decompress(filename: Text) -> Union[Sequence[Dict], Dict]:
        with open(filename, "r") as f:
            output = json_unzip(f.readlines())
        return output


    @staticmethod
    def save(
            padname: Text, json_input: Union[Sequence[Dict], Dict], compress: bool = True
    ) -> None:
        """
        Save current PAD configuration

        Parameters
        ----------
        padname: Text
            name of the PAD
        json_input: Union[Sequence[Dict], Dict]
            PAD metadata
        compress : bool
            Should data be compressed?

        Raises
        ------
        AssertionError
            for wrong padname.
        """
        assert padname in ["PAD", "PADForMA5tune", "PADForSFS"], \
            f"Configuration can only be saved if padname is PAD, PADForMA5tune or PADForSFS"

        if compress:
            filename = Configuration._paddata[padname].split(".")[0] + ".jz"
            Configuration._compress(filename, json_input)
        else:
            with open(Configuration._paddata[padname], "w") as f:
                json.dump(json_input, f, indent = 4)


    def _asdict(self) -> Sequence[Dict]:
        """
        Returns
        -------
        Sequence[Dict]:
            PAD datastructure as dictionary
        """
        to_return = []
        for entry in self.pad_data:
            entry = entry._asdict()
            entry.update({"url" : entry["url"]._asdict()})
            to_return.append(entry)
        return to_return


    def entry_asdict(self, analysis: Text) -> Dict:
        """
        get an entry as a mutable dictionary

        Parameters
        ----------
        analysis : Text
            analysis name

        Returns
        -------
        Dict
        """
        entry = self[analysis]
        if entry is not None:
            entry_dict = entry._asdict()
            entry_dict.update({"url" : entry["url"]._asdict()})
            return entry_dict


    def update_entry(self, analysis: Text, entry: Union[Sequence[Dict], Dict]) -> None:
        """
        Update a PAD entry

        Parameters
        ----------
        analysis : Text
            analysis name given as in PAD metadata
        entry : Union[Sequence[Dict], Dict]
            Full entry information as dictionary or list

        Raises
        ------
        AssertionError
            If analysis does not exist, entry is neither list nor dict or more than one entry
            given.
        jsonschema.exceptions.ValidationError:
            invalid new entry
        jsonschema.exceptions.SchemaError:
            invalid new entry
        """
        assert analysis in list(self.keys()), f"Can't find {analysis} in {self.padname}."
        if isinstance(entry, dict):
            new_entry = [entry]
        assert isinstance(new_entry, list), "Unknown entry type."
        assert len(entry) == 1, f"Only one entry expected, got {len(entry)}."

        jsonschema.validate(new_entry, Configuration._schema)
        pad_data = self._asdict()
        for idx, entry in enumerate(pad_data):
            if entry["name"] == analysis:
                break
        pad_data[idx] = new_entry[0]

        jsonschema.validate(pad_data, Configuration._schema)
        Configuration.save(self.padname, pad_data)

        # Reinitialize the current configuration
        self.__init__(self.padname)


    @property
    def __dict__(self):
        to_return = {}
        for entry in self:
            to_return.update({entry.name : entry})
        return to_return


    def __len__(self):
        """
        Length of the current configuration.

        Returns
        -------
        int
        """
        return len(self.pad_data)


    def __getitem__(self, item: Union[int, Text]) -> NamedTuple:
        if isinstance(item, int):
            return self.pad_data[item]
        elif isinstance(item, str):
            return self.get_analysis(item)
        else:
            raise ValueError(f"Unknown item: {item}")


    def __iter__(self):
        for entry in self.pad_data:
            yield entry


    def keys(self) -> Generator:
        """
        Returns
        -------
        Generator:
            Get all the analysis names available within current PAD config
        """
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
        NamedTuple or None
            analysis metadata. Returns None if analysis does not exist.
        """
        for entry in self.pad_data:
            if entry.name == analysis:
                return entry

        return None


    def get_collaboration(self, collaboration: Text) -> Generator:
        """
        Get the PAD metadata for a given collaboration

        Parameters
        ----------
        collaboration : Text
            collaboration name: atlas or cms

        Returns
        -------
        Generator
            PAD metadata
        """
        assert collaboration in ["atlas", "cms"], f"Unknown collaboration: {collaboration}"
        return (entry for entry in self if collaboration in entry.name)



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
        assert padname in ["PAD", "PADForMA5tune", "PADForSFS"], \
            f"Unknown PAD name: {padname}"

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

        Configuration.save(padname, pad_data)


    def add_json_info(self, analysis: Text, entry: Union[Sequence[Dict], Dict]) -> None:
        """
        Add information about full likelihood json files. Data structure:

        .. code-block:: python

            entry = [
                {
                    "name" : "name of the json extension",
                    "url" : "location of the json file for full likelihoods"
                }
            ]

        Parameters
        ----------
        analysis : Text
            Analysis name
        entry : Union[Sequence[Dict], Dict]
            json file entry. Multiple files can be given as different dictionaries. Dictionary
            keys must be "name" and "url" where name indicates the extension of the file e.g.
            if the json file name is `atlas_susy_2018_31_SRA.json` name is only "SRA".
            url is the full location url of the json file.

        Raises
        ------
        AssertionError:
            if entry is not dict or list type or if analysis does not exist in current data
            structure.
        jsonschema.exceptions.ValidationError:
            invalid new entry
        jsonschema.exceptions.SchemaError:
            invalid new entry
        """
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
                    break

            jsonschema.validate(pad_data, Configuration._schema)
            self.save(self.padname, pad_data)

            # Reinitialize current config
            self.__init__(self.padname)


    def add_bibtex_info(self, analysis: Text, entry: Union[Sequence[Text], Text]):
        """
        Add bibliography. Data structure:

        .. code-block:: python

            entry = ["bibliography dedicated to the analysis", ]

        Parameters
        ----------
        analysis : Text
            Analysis name
        entry : Union[Sequence[Text], Text]
            bibtex entry.

        Raises
        ------
        AssertionError:
            if entry is not str or list type or if analysis does not exist in current data
            structure.
        jsonschema.exceptions.ValidationError:
            invalid new entry
        jsonschema.exceptions.SchemaError:
            invalid new entry
        """
        if isinstance(entry, str):
            entry = [entry]
        assert isinstance(entry, list), "Unknown entry type."
        assert analysis in list(self.keys()), f"Unknown analysis: {analysis}"

        # Validate
        valid = []
        for ent in entry:
            if not isinstance(ent, str):
                print("Corrupt entry: " + ent)
                continue
            valid.append(ent)

        if len(valid) > 0:
            pad_data = self._asdict()
            for idx, data_entry in enumerate(pad_data):
                if data_entry["name"] == analysis:
                    pad_data[idx]["bibtex"] += valid
                    break

            jsonschema.validate(pad_data, Configuration._schema)
            self.save(self.padname, pad_data)

            # Reinitialize current config
            self.__init__(self.padname)


    @staticmethod
    @property
    def entry_example() -> Sequence[Dict]:
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


    def recast_config(self) -> Text:
        """
        Returns recast_config.dat file in str format

        Returns
        -------
        Text
        """
        def add_analysis(detector_dict, entry):
            if entry.url.detector["name"] in list(detector_cards.keys()):
                detector_cards.update(
                    {
                        entry.url.detector["name"] : \
                            detector_cards[entry.url.detector["name"]] + [entry.name]
                    }
                )
                [entry.url.detector["name"]].append(entry.name)
            else:
                detector_cards.update({entry.url.detector["name"] : [entry.name]})

        detector_cards = OrderedDict()
        for entry in self.get_collaboration("atlas"):
            add_analysis(detector_cards, entry)
        for entry in self.get_collaboration("cms"):
            add_analysis(detector_cards, entry)

        txt = "#             detector card             | Analyses\n" \
              "#                                       |\n"

        for card, analysis_list in detector_cards.items():
            card_name = "delphes_card_" if self.padname in ["PAD", "PADForMA5tune"] else "sfs_card_"
            card_name += card + (self.padname in ["PAD", "PADForMA5tune"])*".tcl" + \
                         (self.padname == "PADForSFS")*".ma5"
            txt += card_name.ljust(40, " ")
            txt += "| " + "   ".join(analysis_list) + "\n"
        return txt


    def write_bibtex(self,filename: Text, analyses: Union[Sequence[Text], Text]) -> None:
        """
        Write bibtex file for given analyses

        Parameters
        ----------
        filename : Text
            to where this file needs to be saved with ".bib" extension.
        analyses : Union[Sequence[Text], Text]
            name of the analyses one or more.

        Raises
        ------
        AssertionError
            If analysis does not exist within current configuration
        """
        with open(
                os.path.join(Configuration._currentpath, "meta", "common_bibliography.bib"),
                "r"
        ) as f:
            bibliography = f.read()
        bibliography += "\n\n\n\n%%%%%%%%%%%%%%%%%%%\n%    Analyses    " \
                        "%%\n%%%%%%%%%%%%%%%%%%%\n\n\n"

        analysis_list = list(self.keys())
        if isinstance(analyses, str):
            assert analyses in analysis_list, f"Unknown analysis: {analyses}"
            for bib in self[analyses].bibtex:
                bibliography += bib + "\n\n\n"
        elif isinstance(analyses, (list, tuple)):
            for analysis in analyses:
                if analysis not in analysis_list:
                    continue
                for bib in self[analysis].bibtex:
                    bibliography += bib + "\n\n\n"

        with open(filename, "w") as bib:
            bib.write(bibliography)


    def __add__(self, other):
        assert isinstance(other, Configuration), "Unknown type."
        return Configuration("combined", self.pad_data + other.pad_data)


    def __str__(self):
        txt = "#    Analysis            | Description\n" + "#                        |\n"
        for entry in self.get_collaboration("atlas"):
            txt += entry.name.ljust(25, " ") + "| " + entry.description + "\n"
        for entry in self.get_collaboration("cms"):
            txt += entry.name.ljust(25, " ") + "| " + entry.description + "\n"
        return txt


    def __repr__(self):
        return self.__str__()
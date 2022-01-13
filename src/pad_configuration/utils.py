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

import base64, json, zlib, datetime

from typing import Dict, Union, Sequence


def json_zip(json_input: Union[Dict, Sequence[Dict]]) -> Dict:
    """
    Compress JSON input

    Parameters
    ----------
    json_input : Union[Dict, Sequence[Dict]]

    Returns
    -------
    Dict:
        Compressed input
    """
    json_output = base64.b64encode(
        zlib.compress(json.dumps(json_input).encode('utf-8'))
    ).decode('ascii')

    time = datetime.datetime.now().astimezone().strftime("%B %d, %Y - %H:%M:%S %Z")
    return f"# Ma5 - PAD metadata created on {time}\n" + json_output


def json_unzip(json_input, insist: bool = True) -> Dict:
    """
    Decompress JSON input
    Parameters
    ----------
    json_input :
    insist :

    Returns
    -------
    Dict:
        Decompressed JSON input

    Raises
    ------
    RuntimeError:
        if its not possible to decode the file
    AssertionError
        Invalid file format
    """
    assert json_input[0].startswith("# Ma5 - PAD metadata created on"), "Unknown entry."

    try:
        json_input = zlib.decompress(base64.b64decode(json_input[1]))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        json_input = json.loads(json_input)
    except:
        raise RuntimeError("Could not interpret the unzipped contents")

    return json_input

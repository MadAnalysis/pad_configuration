import base64
import json
import zlib

from typing import Dict, Union, Sequence

ZIPJSON_KEY = 'base64(zip(o))'


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
    json_output = {
        ZIPJSON_KEY: base64.b64encode(
            zlib.compress(json.dumps(json_input).encode('utf-8'))
        ).decode('ascii')
    }

    return json_output


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
        if JSON input does not have `base64(zip(o))` key or its not possible to decode the file
    """
    try:
        assert json_input.get(ZIPJSON_KEY, False) != False
        assert (set(json_input.keys()) == {ZIPJSON_KEY})
    except:
        if insist:
            raise RuntimeError(
                "JSON not in the expected format {" + str(ZIPJSON_KEY) + ": zipstring}"
            )
        else:
            return json_input

    try:
        json_input = zlib.decompress(base64.b64decode(json_input[ZIPJSON_KEY]))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        json_input = json.loads(json_input)
    except:
        raise RuntimeError("Could not interpret the unzipped contents")

    return json_input

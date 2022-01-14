# Public Analysis Database configuration repository
[![PAD](https://img.shields.io/static/v1?style=plastic&label=Recasting&message=PublicAnalysisDatabase&color=blue)](http://madanalysis.irmp.ucl.ac.be/wiki/PublicAnalysisDatabase)

This repository includes the metadata required to configure the PAD when downloaded in a
local [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) workspace. 
[MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) allows for the installation of various 
(validated) recast analyses. Each analysis requires an appropriate detector simulator, relying either
on Delphes or on the [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5)'s native detector 
simulator, the so-called [SFS](https://arxiv.org/abs/2006.09387).

The implementation of  analyses can be achieved by anyone who wishes to contribute. Please see the 
[related issues section](https://github.com/MadAnalysis/madanalysis5/issues/new?assignees=&labels=PAD&template=code-submission-to-public-analysis-database.md&title=) 
for submitting a new analysis.

Due to the variety of possible settings, [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5) 
requires a detailed  metadata configuration to install the analysis codes properly. The present repository
is designed to build such information flow  to [MadAnalysis 5](https://github.com/MadAnalysis/madanalysis5)
during the PAD toolset installation.

## Installation 

 - `$ pip install -e .` or `$ make install` 

## Metadata structure

```python
[
    {
        "name"          : "analysis name",
        "description"   : "analysis description",
        "url"           : {
            "cpp"      : "location of the code",
            "header"   : "location of the header file",
            "info"     : "location of the info file",
            "json"     : [
                {
                    "name" : "name of the json extension",
                    "url" : "location of the json file for full likelihoods"
                }
            ],
            "detector" : {
                "name" : "name of the detector card",
                "url" : "location of the detector card"
            }
        },
        "padversion"    : "PAD version of the analysis e.g. vSFS, v1.2, v1.1 etc.",
        "ma5version"    : "minimum madanalysis version required by the analysis",
        "gcc"           : "minimum c++ version required by the analysis",
        "bibtex"        : [
            "bibliography dedicated to the analysis"
        ]
    }
]
```

## Usage
```python
from pad_configuration import Configuration
config = Configuration("PADForSFS")
print(config)
```
will output the following;
```
#    Analysis            | Description
#                        |
atlas_exot_2018_05       | ATLAS - 13 TeV - di-jet resonance with a photon (76.8/fb)
atlas_susy_2016_07       | ATLAS - 13 TeV - multijet + met (36.1/fb)
atlas_susy_2017_04_2body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 2-body decays (32.8/fb)
atlas_susy_2017_04_3body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 3-body decays (32.8/fb)
atlas_susy_2018_31       | ATLAS - 13 TeV - multibottoms + MET (139/fb)
atlas_conf_2019_040      | ATLAS - 13 TeV - multijet + met (139/fb)
cms_sus_16_048           | CMS   - 13 TeV - Soft dilepton (35.9/fb)
cms_exo_16_022           | CMS   - 13 TeV - Displaced leptons (2.6/fb)
```
All the metadata in this repository is compressed to save space. In order to decompress and save as JSON file
one can use the decompression utilities;
```python
from pad_configuration import Configuration
config = Configuration("PADForSFS")
config.save(config.padname, config._asdict(), compress = False)
```
this will automatically create a decompressed JSON file. Location of the metadata is stored in 
`config._paddata["PADForSFS"]`.

### Adding a new entry
Once can add one or more entry at a time. First create the metadata dictionary:
```python
entry = [{
    'name'         : 'atlas_exot_2018_05', 
    'description': 'ATLAS - 13 TeV - di-jet resonance with a photon (76.8/fb)',
    'url'          : {
        'cpp'   : 'https://dataverse.uclouvain.be/api/access/datafile/9213',
        'header': 'https://dataverse.uclouvain.be/api/access/datafile/9215',
        'info'  : 'https://dataverse.uclouvain.be/api/access/datafile/9214', 
        'json': [], 
        'detector': {
            'name': 'atlas_exot_2018_05', 
            'url': 'https://dataverse.uclouvain.be/api/access/datafile/9216'
        }
    }, 
    'padversion': 'vSFS', 
    'ma5version': 'v1.9.60', 
    'gcc': '98', 
    'bibtex': []
}]
```
Then simply use `add_entry` function in configuration:
```python
Configuration.add_entry("PADForSFS", entry)
```
Note that first entry is for the PAD name to choose the correct metadata file to add new entry.

### Adding full likelihood information
Information for the files that contains full likelihood json files are can either added wihtin the entry
([see previous topic](#adding-a-new-entry)) where `entry[0]["url"]["json"]` stores the information for 
full likelihoods. This, however, can also be added afterwards using `add_json_info` function. First
we need to prepare the entry;
```python
json_entry = [
    {
        "name": "SRA",
        "url": "https://dataverse.uclouvain.be/api/access/datafile/1603"
    },
    {
        "name": "SRB",
        "url": "https://dataverse.uclouvain.be/api/access/datafile/1599"
    },
    {
        "name": "SRC",
        "url": "https://dataverse.uclouvain.be/api/access/datafile/1602"
    }
]
```
where `name` indicates the identifier of the file. This info is for `atlas_susy_2018_31` analysis so the JSON files are
assumed to be `atlas_susy_2018_31_SRA.json`, `atlas_susy_2018_31_SRB.json` and `atlas_susy_2018_31_SRC.json`. `url` 
keyword indicates the location of the JSON file to be downloaded by MadAnalysis. Now by using `add_json_info` we can 
add this entry to the relevant place;
```python
config = Configuration("PADForSFS")
config.add_json_info("atlas_susy_2018_31", json_entry)
```
This will automatically update the relevant file and analysis.

### Adding Bibliography information
Same as before bibliography can be added with the entry in `entry["bibtex"]` section but it can also be added separately 
using `add_bibtex_info` function. As before we first need to create `bibentry` and then add the information to the 
relevant location;
```python
bibentry = [
    "@article{atlas_susy_2017_04,\n    author = {Utsch, Manuel and Goodsell, Mark},\n    publisher = {Open Data @ UCLouvain},\n    title = {{Implementation of a search for a displaced vertices with oppositely-charged leptons (32.8 fb-1; 13 TeV; CMS-EXO-16-022; SFS implementation)}},\n    year = {2021},\n    version = {V1},\n    doi = {10.14428/DVN/31JVGJ},\n    url = {https://doi.org/10.14428/DVN/31JVGJ}\n}\n"
]
config = Configuration("PADForSFS")
config.add_bibtex_info("atlas_susy_2017_04", bibentry)
```

### Write Bibliography
It is possible to write a bibliography file for a collection of entries;
```python
config = Configuration("PADForSFS") + Configuration("PAD")
config.write_bibtex("my_bibliography.bib", ["atlas_susy_2018_31", "atlas_susy_2015_06"])
```
which will print all the necessary bibliography information into `my_bibliography.bib` file.

# Available Analyses

For details on validation notes, [see our website](http://madanalysis.irmp.ucl.ac.be/wiki/PublicAnalysisDatabase).

### PAD for SFS
|        Analysis         | Description|
|:-----------------------:|------------|
|   atlas_exot_2018_05    | ATLAS - 13 TeV - di-jet resonance with a photon (76.8/fb)|
|   atlas_susy_2016_07    | ATLAS - 13 TeV - multijet + met (36.1/fb)|
|atlas_susy_2017_04_2body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 2-body decays (32.8/fb)|
|atlas_susy_2017_04_3body | ATLAS - 13 TeV - displaced vertices with opposite charge leptons, 3-body decays (32.8/fb)|
|   atlas_susy_2018_31    | ATLAS - 13 TeV - multibottoms + MET (139/fb)|
|   atlas_conf_2019_040   | ATLAS - 13 TeV - multijet + met (139/fb)|
|     cms_sus_16_048      | CMS   - 13 TeV - Soft dilepton (35.9/fb)|
|     cms_exo_16_022      | CMS   - 13 TeV - Displaced leptons (2.6/fb)|
|     cms_exo_19_010      | CMS   - 13 TeV - Disappearing tracks (140/fb)|

### PAD
|        Analysis         | Description|
|:-----------------------:|------------|
|   atlas_exot_2014_06    | ATLAS -  8 TeV - Mono-photon (20.3/fb)|
|   atlas_exot_2015_03    | ATLAS - 13 TeV - Mono-jet (3.2/fb)|
|   atlas_exot_2016_25    | ATLAS - 13 TeV - Mono-Higgs in the bbar channel (36.1/fb)|
|   atlas_exot_2016_27    | ATLAS - 13 TeV - Mono-jet (36.1/fb)|
|   atlas_exot_2016_32    | ATLAS - 13 TeV - Mono-photon (36.1/fb)|
|   atlas_exot_2018_30    | ATLAS - 13 TeV - W' into lepton + neutrino (139/fb)|
|   atlas_susy_2015_06    | ATLAS - 13 TeV - Multi-jet + met (2-6 jets, 3.2/fb)|
|   atlas_susy_2016_07    | ATLAS - 13 TeV - Multi-jet + met (36.1/fb)|
|   atlas_susy_2018_04    | ATLAS - 13 TeV - Staus in the ditau + met channel (139/fb)|
|   atlas_susy_2018_17    | ATLAS - 13 TeV - At least 8 jets + met (139/fb)|
|   atlas_susy_2018_06    | ATLAS - 13 TeV - Electroweakinos with jigsaw variables (139/fb)|
|   atlas_susy_2018_32    | ATLAS - 13 TeV - Sleptons/ewkinos with 2l+met (139/fb)|
|   atlas_susy_2019_08    | ATLAS - 13 TeV - H (in bbar) + lepton + met (139/fb)|
|   atlas_conf_2016_086   | ATLAS - 13 TeV - Dark matter production with a bbar pair (13.3/fb)|
|   atlas_conf_2019_040   | ATLAS - 13 TeV - Multi-jet + met (139/fb)|
|   atlas_conf_2020_002   | ATLAS - 13 TeV - At least 8 jets + met (139/fb)|
|     cms_b2g_12_012      | CMS   -  8 TeV - X_{5/3} partners in the SS2L channel (19.5/fb)|
|     cms_b2g_12_022      | CMS   -  8 TeV - Hadronic monotops (19.7/fb)|
|     cms_b2g_14_004      | CMS   -  8 TeV - Dark matter production with a ttbar pair (19.7/fb)|
|     cms_b2g_17_014      | CMS   - 13 TeV - Vector-like quarks with charge 5/3 with same-sign dileptons (35.9/fb)|
|     cms_exo_12_047      | CMS   -  8 TeV - Mono-photon (19.6/fb)|
|     cms_exo_12_048      | CMS   -  8 TeV - Mono-jet (19.7/fb)|
|     cms_exo_16_010      | CMS   - 13 TeV - Mono-Z (2.3/fb)|
|     cms_exo_16_012      | CMS   - 13 TeV - Mono-Higgs in the diphoton channel (2.3/fb)|
|     cms_exo_16_022      | CMS   - 13 TeV - Displaced leptons (2.6/fb)|
|     cms_exo_17_015      | CMS   - 13 TeV - Leptoquark+DM in the 1 mu+1jet + met channel (77.4/fb)|
|     cms_exo_17_030      | CMS   - 13 TeV - Pairs of resonances decaying into a trijet system (35.9/fb)|
|     cms_exo_19_002      | CMS   - 13 TeV - Type III seesaw and top-philic scalars with multi-leptonic probes (137/fb)|
|     cms_exo_20_004      | CMS   - 13 TeV - Mono-jet (137/fb)|
|     cms_hig_18_011      | CMS   - 13 TeV - Exotic Higgs decays (H to aa to 2mu 2b) (35.9/fb)|
|     cms_sus_16_033      | CMS   - 13 TeV - Supersymmetry in the multi-jets + met channel (35.9/fb)|
|     cms_sus_16_039      | CMS   - 13 TeV - Electroweakinos in the multi-leptons + met channel (35.9/fb)|
|     cms_sus_16_048      | CMS   - 13 TeV - Supersymmetry in the one soft leptons + met channel (35.9/fb)|
|     cms_sus_16_052      | CMS   - 13 TeV - Supersymmetry in the 1 lepton + jets +met channel (35.9/fb)|
|     cms_sus_17_001      | CMS   - 13 TeV - stops in the OS2L + jets + MET channel (35.9/fb)|
|     cms_sus_19_006      | CMS   - 13 TeV - SUSY in the HT / missing HT channel (137/fb)|
|     cms_top_17_009      | CMS   - 13 TeV - 4top analysis in the SS2L and multilepton channel (35.9/fb)|
|     cms_top_18_003      | CMS   - 13 TeV - 4top analysis in the SS2L and multilepton channel (137/fb)|

### PAD for Ma5 Tune

|        Analysis         | Description|
|:-----------------------:|------------|
|   atlas_higg_2013_03    | ATLAS - 8 TeV - ZH in the invisible + 2 leptons channel (20.3/fb)|
|   atlas_susy_2013_02    | ATLAS - 8 TeV - squark-gluino in the 0 leptons + 2-6 jets + met channel (20.3/fb)|
|   atlas_susy_2013_04    | ATLAS - 8 TeV - multijet + met (20.3/fb)|
|   atlas_susy_2013_05    | ATLAS - 8 TeV - stops/sbottoms in the 0-lepton + 2-bjets + met channel (20.1/fb)|
|   atlas_susy_2013_11    | ATLAS - 8 TeV - ewkinos in the 2 leptons + met channel (20.3/fb)|
|   atlas_susy_2013_21    | ATLAS - 8 TeV - susy in the mono-jet and c-jets+MET channels (20.3/fb)|
|   atlas_susy_2014_10    | ATLAS - 8 TeV - squark-gluino in the 2 leptons + jets + met channel (20.3/fb)|
|     cms_sus_13_011      | CMS   - 8 TeV - stop in the single lepton + met channel (19.5/fb)|
|     cms_sus_13_012      | CMS   - 8 TeV - squark-gluino in the MET/MHT channel (19.5/fb)|
|     cms_sus_13_016      | CMS   - 8 TeV - gluinos in the 2 leptons + bjets + met channel (19.7/fb)|
| cms_sus_14_001_monojet  | CMS   - 8 TeV - stop in the monojet channel (19.7/fb)|
|  cms_sus_14_001_toptag  | CMS   - 8 TeV - stops in the top-tagging channel (19.7/fb)|

## TODO
 - [x] Expand the documentations
 - [x] Add individual bibliographies to each entry
 - [ ] Add `PADForMA5tune`
